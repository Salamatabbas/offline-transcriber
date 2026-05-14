from pathlib import Path

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma", ".mp4", ".m4b"}
LANGUAGE_CODES = {"de", "en", "fr", "fa", "ar", "tr", "es", "it", "nl", "pt", "ru", "zh", "ja", "ko", "auto"}
MODELS = {"small", "medium", "large"}
OUTPUTS = {"txt", "srt", "vtt"}
MODES = {"transcribe", "translate", "both"}


def validate_config(opts):
    errors = []
    warnings = []
    if opts.get("model") not in MODELS:
        errors.append(f"Invalid model: {opts.get('model')}")
    if opts.get("source_language") not in LANGUAGE_CODES:
        errors.append(f"Invalid source language: {opts.get('source_language')}")
    if opts.get("mode") not in MODES:
        errors.append(f"Invalid mode: {opts.get('mode')}")
    outputs = opts.get("outputs", [])
    if not isinstance(outputs, list) or not outputs:
        errors.append("outputs must be a non-empty list")
    else:
        invalid = sorted(set(outputs) - OUTPUTS)
        if invalid:
            errors.append("Invalid outputs: " + ", ".join(invalid))
    for key in ["chunk_minutes", "chunk_overlap_seconds", "chunk_threshold_minutes", "paragraph_pause_threshold", "paragraph_max_sentences"]:
        try:
            if float(opts.get(key)) < 0:
                errors.append(f"{key} must be non-negative")
        except Exception:
            errors.append(f"{key} must be numeric")
    if opts.get("mode") == "translate" and "txt" not in outputs and "srt" not in outputs and "vtt" not in outputs:
        warnings.append("translate mode selected but no output format enabled")
    return errors, warnings


def safe_input_file(input_dir, single_file):
    """Prevent path traversal for -single while keeping normal filename use."""
    if not single_file:
        return None
    candidate = Path(single_file)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("-single only accepts a filename inside the Input folder")
    target = (Path(input_dir) / candidate.name).resolve()
    root = Path(input_dir).resolve()
    if root not in target.parents and target != root:
        raise ValueError("Invalid input path")
    return target
