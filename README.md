# Audio Transcriber v1.2.5

Offline multilingual audio transcription and optional translation pipeline.

---

## About This Project

Offline Transcriber is an open-source tool for accurate **offline transcription** of audio recordings into text. It supports a wide range of common audio formats and can optionally translate transcripts into English.

After the initial installation, all transcription runs **fully offline** without requiring an internet connection.

This tool is especially useful for:

* Students and academic researchers transcribing interviews
* Journalists handling sensitive recordings
* Professionals working with confidential audio data
* Anyone who needs privacy-preserving offline speech-to-text transcription

---

## Features

* Fully offline processing after setup
* Optional translation (`-translate`)
* Multi-model support (`small`, `medium`, `large`)
* Smart paragraphing
* Dynamic paragraph threshold by model
* Long-file chunking
* Resume support
* Subtitle export (`.srt`, `.vtt`)
* Cross-platform (Windows / macOS)
* Interactive installer with model selection
* Detailed logs
* MIT License

---

## Privacy & Data Handling

All processing is performed **locally on the user's machine**. No audio, transcript, or metadata is sent, stored, or shared externally.

Internet access is only required:

* during installation
* when downloading models (initial setup or upgrades)

---

## Installation

### macOS

```bash
cd /path/to/project/Scripts
chmod +x *.sh
./install_transcriber_mac.sh
```

### Windows

```bat
install_transcriber.bat
```

---

## Usage

Before running the tool, place your audio files inside the **Input** folder in the project directory.

### macOS

```bash
./transcribe_mac.sh
./transcribe_mac.sh -single audio.mp3
./transcribe_mac.sh -single audio.mp3 -translate
./transcribe_mac.sh -single audio.mp3 -large
./transcribe_mac.sh -archive
./transcribe_mac.sh -force
./transcribe_mac.sh -preprocess
```

### Windows

```bat
transcribe.bat
transcribe.bat -single audio.mp3
transcribe.bat -single audio.mp3 -translate
transcribe.bat -single audio.mp3 -large
transcribe.bat -archive
transcribe.bat -force
transcribe.bat -preprocess
```

---

## Parameters

* `-translate` enable translation
* `-small` use the small model
* `-medium` use the medium model
* `-large` use the large model
* `-accurate` alias for large
* `-archive` move processed files to Archive
* `-force` reprocess existing outputs
* `-single <file>` process one file
* `-preprocess` enable audio preprocessing
* `--init` initialize project structure
* `-config` show current configuration

---

## Subtitle Export

The tool supports subtitle export in `.srt` and `.vtt` formats.

### Examples

```bash
./transcribe_mac.sh -single audio.mp3 -srt
./transcribe_mac.sh -single audio.mp3 -translate -srt
./transcribe_mac.sh -single audio.mp3 -vtt
```

```bat
transcribe.bat -single audio.mp3 -srt
transcribe.bat -single audio.mp3 -translate -srt
transcribe.bat -single audio.mp3 -vtt
```

When `-translate` and `-srt` are used together, both are generated:

* original transcript/subtitle
* English translation

---

## Installing Additional Models Later

If you need additional models after installation, use the upgrade scripts while connected to the internet.

### macOS

```bash
./upgrade_models_mac.sh
./upgrade_models_mac.sh -large
./upgrade_models_mac.sh -medium -large
```

### Windows

```bat
upgrade_models.bat
upgrade_models.bat -large
upgrade_models.bat -medium -large
```

If a required model is missing, the program will show a clear instruction.

---

## Offline-Safe Model Loading

During transcription, the tool will **not download models automatically**.

If a model is not available locally, the program stops and instructs you to run the upgrade script.

This ensures:

* predictable behavior
* full offline operation
* maximum data privacy

---

## Notes for Windows / Parallels

Running inside virtual environments (e.g. Parallels) may reduce performance.

This release includes workarounds for common OpenMP runtime conflicts.

---

## Accuracy Disclaimer

Transcription and translation quality depend on:

* audio quality
* speaker clarity
* accent / dialect
* background noise
* speaking speed

No automated system guarantees perfect accuracy.
Users should review outputs before using them in critical contexts.

---

## License

MIT License

---

## Author

**Abbas SALAMAT**
[Abbas.salamat@edu.donau-uni.ac.at](mailto:Abbas.salamat@edu.donau-uni.ac.at)

Suggestions, improvements, bug reports, and contributions are welcome.
