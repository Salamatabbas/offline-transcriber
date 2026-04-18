import sys
import json
import time
import shutil
import subprocess
import shutil as _shutil
from pathlib import Path
from faster_whisper import WhisperModel

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma", ".mp4", ".m4b"}
LANGUAGE_CODES = {"de", "en", "fr", "fa", "ar", "tr", "es", "it", "nl", "pt", "ru", "zh", "ja", "ko", "auto"}
MODELS = {"small", "medium", "large"}

DEFAULT_CONFIG = {
    "source_language": "auto",
    "target_language": "en",
    "model": "medium",
    "profile": "balanced",
    "mode": "transcribe",
    "outputs": ["txt"],
    "clean": True,
    "archive": False,
    "skip_existing": True,
    "single_file": None,
    "paragraph_mode": True,
    "paragraph_pause_threshold": 2.5,
    "paragraph_max_sentences": 5,
    "dynamic_paragraph_threshold": True,
    "vad_filter": True,
    "condition_on_previous_text": False,
    "chunking_enabled": True,
    "chunk_minutes": 15,
    "chunk_overlap_seconds": 10,
    "chunk_threshold_minutes": 20,
    "resume_chunks": True,
    "preprocess_audio": False,
    "cleanup_work_files": True
}

DEVICE = "cpu"
COMPUTE_TYPE = "int8"

def usage():
    return """
Usage:
  python transcribe.py --init
  python transcribe.py -config
  python transcribe.py
  python transcribe.py -single lecture1.m4a
  python transcribe.py -translate
  python transcribe.py -large
  python transcribe.py -accurate
  python transcribe.py -preprocess
  python transcribe.py -force

Model upgrades:
  upgrade_models_mac.sh -small|-medium|-large
  upgrade_models.bat -small|-medium|-large
""".strip()

def project_paths():
    scripts_dir = Path(__file__).resolve().parent
    project_dir = scripts_dir.parent
    return {
        "project": project_dir,
        "input": project_dir / "Input",
        "done": project_dir / "Done",
        "logs": project_dir / "Logs",
        "archive": project_dir / "Archive",
        "work": project_dir / "Work",
        "chunks": project_dir / "Work" / "chunks",
        "preprocessed": project_dir / "Work" / "preprocessed",
        "state": project_dir / "Work" / "state",
        "config": project_dir / "config.json",
    }

def ensure_dirs(paths):
    for key, value in paths.items():
        if key != "config":
            value.mkdir(parents=True, exist_ok=True)

def load_config(config_path):
    if not config_path.exists():
        return dict(DEFAULT_CONFIG)
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        merged = dict(DEFAULT_CONFIG)
        merged.update(data)
        if not isinstance(merged.get("outputs"), list):
            merged["outputs"] = list(DEFAULT_CONFIG["outputs"])
        return merged
    except Exception:
        return dict(DEFAULT_CONFIG)

def save_config(config_path, config):
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

def init_project(paths):
    ensure_dirs(paths)
    if not paths["config"].exists():
        save_config(paths["config"], DEFAULT_CONFIG)
    print("Project initialized at:", paths["project"])
    print("Created/verified:")
    for key in ("input", "done", "logs", "archive", "work", "chunks", "preprocessed", "state", "config"):
        print(" -", paths[key])

def parse_args(argv, config):
    opts = dict(config)
    show_config = False
    init_only = False

    i = 0
    while i < len(argv):
        arg = argv[i].strip()
        lower = arg.lower()
        clean = lower.lstrip("-")

        if lower in {"-h", "--help", "/?"}:
            print(usage())
            sys.exit(0)
        elif lower in {"--init", "-init"}:
            init_only = True
        elif lower in {"-config", "--config"}:
            show_config = True
        elif clean in MODELS:
            opts["model"] = clean
            opts["profile"] = None
        elif lower in {"-fast", "--fast"}:
            opts["profile"] = "fast"
            opts["model"] = "small"
        elif lower in {"-balanced", "--balanced"}:
            opts["profile"] = "balanced"
            opts["model"] = "medium"
        elif lower in {"-accurate", "--accurate"}:
            opts["profile"] = "accurate"
            opts["model"] = "large"
        elif lower in {"-translate", "--translate"}:
            opts["mode"] = "both"
            opts["target_language"] = "en"
        elif lower == "--both":
            opts["mode"] = "both"
            opts["target_language"] = "en"
        elif lower in {"-single", "--single"}:
            if i + 1 >= len(argv):
                print("Missing filename after -single")
                sys.exit(1)
            opts["single_file"] = argv[i + 1].strip()
            i += 1
        elif lower in {"-srt", "--srt"}:
            if "srt" not in opts["outputs"]:
                opts["outputs"].append("srt")
        elif lower in {"-vtt", "--vtt"}:
            if "vtt" not in opts["outputs"]:
                opts["outputs"].append("vtt")
        elif lower in {"-txt", "--txt"}:
            if "txt" not in opts["outputs"]:
                opts["outputs"].append("txt")
        elif lower in {"-clean", "--clean"}:
            opts["clean"] = True
        elif lower in {"-no-clean", "--no-clean"}:
            opts["clean"] = False
        elif lower in {"-archive", "--archive"}:
            opts["archive"] = True
        elif lower in {"-no-archive", "--no-archive"}:
            opts["archive"] = False
        elif lower in {"-force", "--force"}:
            opts["skip_existing"] = False
        elif lower in {"-skip", "--skip"}:
            opts["skip_existing"] = True
        elif lower in {"-preprocess", "--preprocess"}:
            opts["preprocess_audio"] = True
        elif lower in {"-no-preprocess", "--no-preprocess"}:
            opts["preprocess_audio"] = False
        elif clean in LANGUAGE_CODES:
            opts["source_language"] = clean
        else:
            print("Unknown argument:", arg)
            print()
            print(usage())
            sys.exit(1)
        i += 1
    return opts, show_config, init_only

def run_cmd(cmd):
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "Command failed").strip())
    return completed.stdout.strip()

def ffprobe_duration(path):
    out = run_cmd([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ])
    return float(out)

def preflight_check(paths, opts):
    issues = []
    warnings = []
    if sys.version_info < (3, 9):
        issues.append("Python 3.9+ is required.")
    if _shutil.which("ffmpeg") is None:
        issues.append("ffmpeg was not found in PATH.")
    if _shutil.which("ffprobe") is None:
        issues.append("ffprobe was not found in PATH.")
    if opts["model"] not in MODELS:
        issues.append("Invalid model: {}".format(opts["model"]))
    if opts["source_language"] not in LANGUAGE_CODES:
        issues.append("Invalid source language: {}".format(opts["source_language"]))
    audio_files = list(iter_audio_files(paths["input"])) if paths["input"].exists() else []
    if not audio_files:
        warnings.append("No supported audio files found in Input.")
    if issues:
        print("Pre-flight check failed:")
        for item in issues:
            print(" -", item)
        sys.exit(1)
    print("Pre-flight check passed.")
    if warnings:
        print("Warnings:")
        for item in warnings:
            print(" -", item)

def iter_audio_files(folder):
    return sorted(f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS)

def choose_files(input_dir, single_file):
    files = list(iter_audio_files(input_dir))
    if single_file:
        target = input_dir / single_file
        if not target.exists():
            raise FileNotFoundError("Single file not found in Input: {}".format(single_file))
        return [target]
    return files

def print_header(title):
    print()
    print("=" * 84)
    print(title)
    print("=" * 84)

def srt_timestamp(seconds):
    ms = int(round(seconds * 1000))
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return "{:02d}:{:02d}:{:02d},{:03d}".format(h, m, s, ms)

def vtt_timestamp(seconds):
    ms = int(round(seconds * 1000))
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return "{:02d}:{:02d}:{:02d}.{:03d}".format(h, m, s, ms)

def clean_line(line):
    return " ".join(line.split()).strip()

def effective_pause_threshold(opts):
    if not opts.get("dynamic_paragraph_threshold", True):
        return float(opts["paragraph_pause_threshold"])
    model = opts.get("model", "medium")
    if model == "medium":
        return max(float(opts["paragraph_pause_threshold"]), 4.0)
    if model == "small":
        return max(float(opts["paragraph_pause_threshold"]), 4.5)
    return float(opts["paragraph_pause_threshold"])

def smart_paragraphs(entries, pause_threshold=2.5, max_sentences=5):
    if not entries:
        return []
    paragraphs = []
    current = []
    last_end = None
    for entry in entries:
        if last_end is not None:
            gap = float(entry["start"]) - float(last_end)
            if gap > pause_threshold or len(current) >= max_sentences:
                paragraphs.append(" ".join(x["text"] for x in current))
                current = []
        current.append(entry)
        last_end = entry["end"]
    if current:
        paragraphs.append(" ".join(x["text"] for x in current))
    return paragraphs

def write_srt(entries, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, e in enumerate(entries, start=1):
            f.write(str(i) + "\n")
            f.write("{} --> {}\n".format(srt_timestamp(e["start"]), srt_timestamp(e["end"])))
            f.write(e["text"] + "\n\n")

def write_vtt(entries, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for e in entries:
            f.write("{} --> {}\n".format(vtt_timestamp(e["start"]), vtt_timestamp(e["end"])))
            f.write(e["text"] + "\n\n")

def build_output_paths(done_dir, stem, outputs, mode, target_language):
    paths = {}
    if mode in {"transcribe", "both"}:
        if "txt" in outputs:
            paths["transcript_txt"] = done_dir / (stem + ".txt")
        if "srt" in outputs:
            paths["transcript_srt"] = done_dir / (stem + ".srt")
        if "vtt" in outputs:
            paths["transcript_vtt"] = done_dir / (stem + ".vtt")
        paths["transcript_meta"] = done_dir / (stem + ".meta.json")
    if mode in {"translate", "both"}:
        suffix = "." + target_language
        if "txt" in outputs:
            paths["translation_txt"] = done_dir / (stem + suffix + ".txt")
        if "srt" in outputs:
            paths["translation_srt"] = done_dir / (stem + suffix + ".srt")
        if "vtt" in outputs:
            paths["translation_vtt"] = done_dir / (stem + suffix + ".vtt")
        paths["translation_meta"] = done_dir / (stem + suffix + ".meta.json")
    return paths

def outputs_exist(paths):
    check = [p for k, p in paths.items() if not k.endswith("_meta")]
    return bool(check) and all(p.exists() for p in check)

def preprocess_audio(src, dest):
    run_cmd(["ffmpeg", "-y", "-i", str(src), "-af", "loudnorm", str(dest)])

def make_chunk_manifest(duration_seconds, chunk_minutes, overlap_seconds):
    chunk_len = float(chunk_minutes) * 60.0
    overlap = float(overlap_seconds)
    manifest = []
    idx = 0
    next_start = 0.0
    while next_start < duration_seconds:
        chunk_start = max(0.0, next_start - (overlap if idx > 0 else 0.0))
        chunk_end = min(duration_seconds, next_start + chunk_len)
        chunk_duration = max(0.0, chunk_end - chunk_start)
        ignore_before = 0.0 if idx == 0 else overlap
        manifest.append({"index": idx, "start": round(chunk_start, 3), "duration": round(chunk_duration, 3), "ignore_before": round(ignore_before, 3)})
        idx += 1
        next_start += chunk_len
    return manifest

def extract_chunk(src, chunk_file, start_seconds, duration_seconds):
    run_cmd(["ffmpeg", "-y", "-ss", str(start_seconds), "-t", str(duration_seconds), "-i", str(src), "-vn", "-acodec", "pcm_s16le", str(chunk_file)])

def transcribe_chunk(model, chunk_file, source_language, clean, vad_filter, condition_on_previous_text, task):
    kwargs = {"task": task, "vad_filter": vad_filter, "condition_on_previous_text": condition_on_previous_text}
    if source_language != "auto" and task == "transcribe":
        kwargs["language"] = source_language
    segments, info = model.transcribe(str(chunk_file), **kwargs)
    detected_language = getattr(info, "language", None) or source_language
    entries = []
    last_line = None
    for segment in segments:
        line = segment.text.strip()
        if clean:
            line = clean_line(line)
        if not line:
            continue
        if clean and line == last_line:
            continue
        entries.append({"start": float(segment.start), "end": float(segment.end), "text": line})
        last_line = line
    return entries, detected_language

def merge_chunk_entries(chunk_records):
    merged = []
    seen = set()
    for record in chunk_records:
        ignore_before = float(record["ignore_before"])
        chunk_start = float(record["start"])
        for e in record["entries"]:
            if record["index"] > 0 and float(e["end"]) <= ignore_before:
                continue
            abs_start = chunk_start + float(e["start"])
            abs_end = chunk_start + float(e["end"])
            key = (round(abs_start, 2), e["text"])
            if key in seen:
                continue
            seen.add(key)
            merged.append({"start": abs_start, "end": abs_end, "text": e["text"]})
    merged.sort(key=lambda x: (x["start"], x["end"]))
    return merged

def write_outputs(entries, paths, kind_prefix, opts):
    txt_key = kind_prefix + "_txt"
    srt_key = kind_prefix + "_srt"
    vtt_key = kind_prefix + "_vtt"
    pause_threshold = effective_pause_threshold(opts)
    if txt_key in paths:
        with open(paths[txt_key], "w", encoding="utf-8") as f:
            if opts["paragraph_mode"]:
                for para in smart_paragraphs(entries, pause_threshold=pause_threshold, max_sentences=int(opts["paragraph_max_sentences"])):
                    f.write(para + "\n\n")
            else:
                for e in entries:
                    f.write(e["text"] + "\n")
    if srt_key in paths:
        write_srt(entries, paths[srt_key])
    if vtt_key in paths:
        write_vtt(entries, paths[vtt_key])

def write_metadata(meta_path, payload):
    meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def safe_rmtree(path):
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)

def process_file(model, audio_file, paths, opts, log):
    stem = audio_file.stem
    output_paths = build_output_paths(paths["done"], stem, set(opts["outputs"]), opts["mode"], opts["target_language"])
    if opts["skip_existing"] and outputs_exist(output_paths):
        print("Skipping, outputs already exist.")
        log.write("Skipped existing outputs.\n")
        return "skipped", {"file": audio_file.name}
    duration = ffprobe_duration(audio_file)
    do_chunk = bool(opts["chunking_enabled"]) and duration >= float(opts["chunk_threshold_minutes"]) * 60.0
    working_source = audio_file
    preprocessed_file = paths["preprocessed"] / (stem + ".pre.wav")
    chunk_dir = paths["chunks"] / stem
    state_file = paths["state"] / (stem + ".state.json")
    state = {"chunks": {}} if not state_file.exists() else json.loads(state_file.read_text(encoding="utf-8"))
    chunk_records_transcript = []
    chunk_records_translation = []
    if opts["preprocess_audio"]:
        if not preprocessed_file.exists():
            print("Preprocessing audio...")
            preprocess_audio(audio_file, preprocessed_file)
        working_source = preprocessed_file
    if do_chunk:
        chunk_dir.mkdir(parents=True, exist_ok=True)
        manifest = make_chunk_manifest(duration, opts["chunk_minutes"], opts["chunk_overlap_seconds"])
    else:
        chunk_dir.mkdir(parents=True, exist_ok=True)
        manifest = [{"index": 0, "start": 0.0, "duration": duration, "ignore_before": 0.0}]
    print("Duration: {:.1f}s | Chunking: {} | Chunks: {}".format(duration, do_chunk, len(manifest)))
    log.write("Duration {:.1f}s | chunking={} | chunks={}\n".format(duration, do_chunk, len(manifest)))
    total_chunks = len(manifest)
    file_started = time.time()
    for item in manifest:
        idx = item["index"]
        chunk_file = chunk_dir / ("chunk_{:04d}.wav".format(idx + 1))
        transcript_json = chunk_dir / ("chunk_{:04d}.transcript.json".format(idx + 1))
        translation_json = chunk_dir / ("chunk_{:04d}.translation.json".format(idx + 1))
        if not chunk_file.exists():
            extract_chunk(working_source, chunk_file, item["start"], item["duration"])
        elapsed_chunks = time.time() - file_started
        avg_chunk_time = elapsed_chunks / max(idx, 1) if idx > 0 else 0
        remaining_chunks = total_chunks - idx - 1
        chunk_eta = avg_chunk_time * remaining_chunks if avg_chunk_time > 0 else 0
        print_header("[chunk {}/{}] {} | ETA {:.1f}s".format(idx + 1, total_chunks, audio_file.name, chunk_eta))
        chunk_state = state["chunks"].get(str(idx), {})
        if opts["mode"] in {"transcribe", "both"}:
            if opts["resume_chunks"] and transcript_json.exists() and chunk_state.get("transcript_done"):
                transcript_entries = json.loads(transcript_json.read_text(encoding="utf-8"))
                detected_language = chunk_state.get("detected_language", opts["source_language"])
                print("Loaded transcript chunk from resume state.")
            else:
                transcript_entries, detected_language = transcribe_chunk(model, chunk_file, opts["source_language"], opts["clean"], opts["vad_filter"], opts["condition_on_previous_text"], "transcribe")
                transcript_json.write_text(json.dumps(transcript_entries, ensure_ascii=False, indent=2), encoding="utf-8")
                chunk_state["transcript_done"] = True
                chunk_state["detected_language"] = detected_language
                state["chunks"][str(idx)] = chunk_state
                state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
            chunk_records_transcript.append({"index": idx, "start": item["start"], "ignore_before": item["ignore_before"], "entries": transcript_entries})
        if opts["mode"] in {"translate", "both"}:
            if opts["resume_chunks"] and translation_json.exists() and chunk_state.get("translation_done"):
                translation_entries = json.loads(translation_json.read_text(encoding="utf-8"))
                print("Loaded translation chunk from resume state.")
            else:
                translation_entries, _ = transcribe_chunk(model, chunk_file, "auto", opts["clean"], opts["vad_filter"], opts["condition_on_previous_text"], "translate")
                translation_json.write_text(json.dumps(translation_entries, ensure_ascii=False, indent=2), encoding="utf-8")
                chunk_state["translation_done"] = True
                state["chunks"][str(idx)] = chunk_state
                state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
            chunk_records_translation.append({"index": idx, "start": item["start"], "ignore_before": item["ignore_before"], "entries": translation_entries})
    detected_language = opts["source_language"]
    if opts["mode"] in {"transcribe", "both"}:
        transcript_entries = merge_chunk_entries(chunk_records_transcript)
        if chunk_records_transcript:
            detected_language = state["chunks"].get("0", {}).get("detected_language", detected_language)
        write_outputs(transcript_entries, output_paths, "transcript", opts)
        write_metadata(output_paths["transcript_meta"], {
            "source_file": audio_file.name,
            "mode": "transcript",
            "detected_language": detected_language,
            "requested_source_language": opts["source_language"],
            "model": opts["model"],
            "profile": opts["profile"],
            "duration_seconds": duration,
            "chunking_enabled": do_chunk,
            "chunk_count": total_chunks,
            "chunk_minutes": opts["chunk_minutes"],
            "chunk_overlap_seconds": opts["chunk_overlap_seconds"],
            "preprocess_audio": opts["preprocess_audio"],
            "effective_paragraph_pause_threshold": effective_pause_threshold(opts),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "outputs": {k: str(v.name) for k, v in output_paths.items() if k.startswith("transcript_")}
        })
    if opts["mode"] in {"translate", "both"}:
        translation_entries = merge_chunk_entries(chunk_records_translation)
        write_outputs(translation_entries, output_paths, "translation", opts)
        write_metadata(output_paths["translation_meta"], {
            "source_file": audio_file.name,
            "mode": "translation",
            "target_language": "en",
            "model": opts["model"],
            "profile": opts["profile"],
            "duration_seconds": duration,
            "chunking_enabled": do_chunk,
            "chunk_count": total_chunks,
            "chunk_minutes": opts["chunk_minutes"],
            "chunk_overlap_seconds": opts["chunk_overlap_seconds"],
            "preprocess_audio": opts["preprocess_audio"],
            "effective_paragraph_pause_threshold": effective_pause_threshold(opts),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "outputs": {k: str(v.name) for k, v in output_paths.items() if k.startswith("translation_")}
        })
    if opts["archive"]:
        target = paths["archive"] / audio_file.name
        if not target.exists():
            shutil.move(str(audio_file), str(target))
    if opts["cleanup_work_files"]:
        safe_rmtree(chunk_dir)
        if preprocessed_file.exists():
            preprocessed_file.unlink(missing_ok=True)
        if state_file.exists():
            state_file.unlink(missing_ok=True)
    return "processed", {"file": audio_file.name}

def main():
    paths = project_paths()
    ensure_dirs(paths)
    base_config = load_config(paths["config"])
    opts, show_config, init_only = parse_args(sys.argv[1:], base_config)
    if init_only:
        init_project(paths)
        return
    if show_config:
        print(json.dumps(base_config, ensure_ascii=False, indent=2))
        return
    preflight_check(paths, opts)
    try:
        audio_files = choose_files(paths["input"], opts["single_file"])
    except Exception as e:
        print(str(e))
        sys.exit(1)
    if not audio_files:
        print("No supported audio files found in:", paths["input"])
        print("Drop your audio files into Input and run again.")
        return
    print("=" * 84)
    print("Project folder   :", paths["project"])
    print("Input folder     :", paths["input"])
    print("Done folder      :", paths["done"])
    print("Logs folder      :", paths["logs"])
    print("Archive folder   :", paths["archive"])
    print("Work folder      :", paths["work"])
    print("Config file      :", paths["config"])
    print("Source setting   :", opts["source_language"])
    print("Target language  :", opts["target_language"] if opts["mode"] in {"translate", "both"} else "n/a (translation disabled)")
    print("Model            :", opts["model"])
    print("Profile          :", opts["profile"])
    print("Mode             :", opts["mode"])
    print("Outputs          :", ", ".join(sorted(set(opts["outputs"]))))
    print("Paragraph pause  :", opts["paragraph_pause_threshold"])
    print("Dynamic para thr :", opts["dynamic_paragraph_threshold"])
    print("Effective pause  :", effective_pause_threshold(opts))
    print("Paragraph max    :", opts["paragraph_max_sentences"])
    print("Chunking enabled :", opts["chunking_enabled"])
    print("Chunk minutes    :", opts["chunk_minutes"])
    print("Chunk overlap s  :", opts["chunk_overlap_seconds"])
    print("Chunk threshold  :", opts["chunk_threshold_minutes"])
    print("Resume chunks    :", opts["resume_chunks"])
    print("Preprocess audio :", opts["preprocess_audio"])
    print("Cleanup work     :", opts["cleanup_work_files"])
    print("Files found      :", len(audio_files))
    print("=" * 84)
    start_time = time.time()
    log_file = paths["logs"] / ("run_log_" + time.strftime("%Y%m%d_%H%M%S") + ".txt")
    summary_file = paths["logs"] / "last_run_summary.txt"
    stats = {"found": len(audio_files), "processed": 0, "skipped": 0, "errors": 0, "archived": 0}
    try:
        model = WhisperModel(opts["model"], device=DEVICE, compute_type=COMPUTE_TYPE, local_files_only=True)
    except Exception:
        print()
        print("ERROR: The requested model could not be loaded.")
        print("This usually means the model is not installed locally yet.")
        print("Automatic online model download during transcription is disabled by design.")
        print()
        print("Please connect to the internet and run one of these:")
        print("  macOS   : ./upgrade_models_mac.sh -" + opts["model"])
        print("  Windows : upgrade_models.bat -" + opts["model"])
        print()
        print("Or run the upgrade script without parameters to choose from the menu.")
        print()
        sys.exit(1)
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("Run started: {}\n".format(time.ctime(start_time)))
        log.write(json.dumps(opts, ensure_ascii=False, indent=2) + "\n\n")
        for index, audio_file in enumerate(audio_files, start=1):
            print_header("[{}/{}] Processing file: {}".format(index, len(audio_files), audio_file.name))
            log.write("[{}/{}] {}\n".format(index, len(audio_files), audio_file.name))
            try:
                status, info = process_file(model, audio_file, paths, opts, log)
                if status == "processed":
                    stats["processed"] += 1
                    if opts["archive"]:
                        stats["archived"] += 1
                elif status == "skipped":
                    stats["skipped"] += 1
                log.write("Status: {}\n\n".format(status))
            except Exception as e:
                stats["errors"] += 1
                print("Error while processing {}: {}".format(audio_file.name, e))
                log.write("Error: {}\n\n".format(e))
        elapsed = time.time() - start_time
        audio_total = 0.0
        try:
            for audio_file in audio_files:
                audio_total += ffprobe_duration(audio_file)
        except Exception:
            pass
        rtf = elapsed / audio_total if audio_total > 0 else 0.0
        summary = [
            "Run finished: {}".format(time.ctime()),
            "Files found : {}".format(stats["found"]),
            "Processed   : {}".format(stats["processed"]),
            "Skipped     : {}".format(stats["skipped"]),
            "Errors      : {}".format(stats["errors"]),
            "Archived    : {}".format(stats["archived"]),
            "Elapsed sec : {:.1f}".format(elapsed),
            "Audio sec   : {:.1f}".format(audio_total),
            "RTF         : {:.2f}x".format(rtf),
            "Log file    : {}".format(log_file.name),
        ]
        summary_text = "\n".join(summary)
        print_header("Run summary")
        print(summary_text)
        log.write(summary_text + "\n")
        summary_file.write_text(summary_text + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
