def pick_backend(requested_device="auto", requested_compute_type="auto"):
    """Return (device, compute_type, backend_note).

    Keeps normal runtime offline-safe. This only checks local hardware/runtime.
    """
    requested_device = (requested_device or "auto").lower()
    requested_compute_type = (requested_compute_type or "auto").lower()

    if requested_device in {"cpu", "cuda"}:
        device = requested_device
    else:
        device = "cpu"
        try:
            import ctranslate2
            if getattr(ctranslate2, "get_cuda_device_count", lambda: 0)() > 0:
                device = "cuda"
        except Exception:
            device = "cpu"

    if requested_compute_type != "auto":
        compute_type = requested_compute_type
    else:
        compute_type = "float16" if device == "cuda" else "int8"

    note = "GPU/CUDA" if device == "cuda" else "CPU"
    return device, compute_type, note


def wrap_transcriber(model, device, batch_size=8):
    """Use batched inference on CUDA when available; keep CPU path simple."""
    try:
        batch_size = int(batch_size)
    except Exception:
        batch_size = 8
    if device == "cuda" and batch_size > 1:
        try:
            from faster_whisper import BatchedInferencePipeline
            return BatchedInferencePipeline(model=model), True
        except Exception:
            return model, False
    return model, False
