
# Release Notes v1.3.6

## New Features

* **Full GUI implemented for Offline Transcriber** – users can now interact with the app via an intuitive interface instead of command-line.
* Added **“Translate without transcription”** option with safe toggle logic.
* Favorite Config can now be saved and loaded correctly.
* Reset Default Config restores all settings to initial defaults.
* Checkboxes visually indicate disabled state with dimmed text for clarity.

## Fixed

* Fixed missing `get_current_config` issue that caused crashes when saving favorite config.
* Corrected f-string and syntax issues in logging Favorite Config path.
* GUI logic corrected to prevent conflicting translation options from being active simultaneously.

## Improvements

* Color and style updates to better indicate active/inactive options.
* Translation options now follow logical rules for SRT/VTT and translation checkboxes.
* Code refactored for safer and more maintainable configuration management.


