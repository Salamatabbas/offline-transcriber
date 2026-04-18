# Audio Transcriber v1.2.0

Offline multilingual audio transcription and optional translation pipeline.

## Privacy & Data Handling

All processing is performed fully offline on the user's local machine.

This software does **not**:
- upload audio files
- transmit transcripts
- send translations
- share metadata
- collect analytics
- communicate with external servers during transcription or translation

No user data is stored, shared, or transmitted beyond the user's own device.

Model downloads may occur only during installation or first-time setup if selected models are not already cached locally.

## About This Project

This project was developed using a **Vibe Coding** workflow with extensive human supervision, iterative refinement, and multi-phase testing.

Every major component has been manually reviewed, repeatedly tested, and improved over multiple development phases.

## Features

- Fully offline processing after setup
- Optional translation (`-translate`)
- Multi-model support (`small`, `medium`, `large`)
- Smart paragraphing
- Dynamic paragraph threshold by model
- Long-file chunking
- Resume support
- Cross-platform Windows / macOS
- Detailed run logs with RTF metrics
- Interactive installer with model selection
- MIT License

## Installation

### macOS
```bash
cd /path/to/project/Scripts
chmod +x *.sh
./install_transcriber_mac.sh
```

### Windows
Run:
```bat
install_transcriber.bat
```

## Usage Examples

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

## Parameters

- `-translate` enable translation
- `-small` use the small model
- `-medium` use the medium model
- `-large` use the large model
- `-accurate` alias for large model
- `-archive` move processed files to Archive
- `-force` reprocess even if outputs already exist
- `-single <file>` process one specific file from Input
- `-preprocess` enable audio preprocessing
- `--init` create project folders and config
- `-config` show current config

## Accuracy Disclaimer

Transcription and translation quality depend heavily on:
- audio quality
- speaker clarity
- accent / dialect
- background noise
- speaking speed
- recording compression
- conversational vs. formal speech

While this software has been extensively tested and refined, no automated transcription or translation system can guarantee perfect accuracy.

Users are encouraged to review generated outputs before relying on them for important, professional, academic, legal, or medical purposes.

## License

MIT License

## Author

**Abbas SALAMAT**  
Abbas.salamat@edu.donau-uni.ac.at

Suggestions, improvements, bug reports, and contributions are welcome.


## Notes for Windows / Parallels

If you run the Windows version inside Parallels or another VM, performance may be slower than native macOS.
This release includes a compatibility workaround for common OpenMP runtime conflicts on Windows.

## Log Wording

The run summary shows:
- **Source setting** = what you asked the program to do (`auto` means automatic detection)
- **Target language** = only shown when translation is enabled


## Installing Additional Models Later

If you initially installed only one model and later need another one, you can use the upgrade scripts while connected to the internet.

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

If a requested model is not installed locally, the transcriber will show a message telling you which upgrade command to run.


## Offline-Safe Model Loading

During normal transcription runs, the tool will **not** download missing models automatically.
If a requested model is not already installed locally, the program will stop and tell you to run the appropriate upgrade script while connected to the internet.

This behavior is intentional and helps preserve the project's offline-first privacy model.
