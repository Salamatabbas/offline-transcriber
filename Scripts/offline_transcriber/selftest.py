from pathlib import Path


def run_self_tests(project_paths, helpers):
    tests = []
    srt_timestamp = helpers["srt_timestamp"]
    vtt_timestamp = helpers["vtt_timestamp"]
    build_output_paths = helpers["build_output_paths"]

    tests.append(("srt timestamp", srt_timestamp(3661.234) == "01:01:01,234"))
    tests.append(("vtt timestamp", vtt_timestamp(1.5) == "00:00:01.500"))
    paths = build_output_paths(Path("Done"), "sample", {"txt", "srt", "vtt"}, "both", "en")
    tests.append(("transcript srt path", str(paths["transcript_srt"]).endswith("sample.srt")))
    tests.append(("translation txt path", str(paths["translation_txt"]).endswith("sample.en.txt")))
    for key in ("input", "done", "logs", "work"):
        tests.append((f"path exists: {key}", project_paths[key].exists()))

    failed = [name for name, ok in tests if not ok]
    print("Self-test results:")
    for name, ok in tests:
        print((" OK  " if ok else "FAIL ") + name)
    if failed:
        raise SystemExit(1)
    print("All self-tests passed.")
