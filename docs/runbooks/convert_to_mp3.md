# Runbook: convert-to-mp3

## Description
Batch converts `.mp4` video files to high-quality `.mp3` audio files. It also embeds the video's thumbnail as album art in the resulting audio file.

## Prerequisites
- **zsh:** Must be installed.
- **FFmpeg:** Must be installed and available in the PATH.

## Usage
1. Navigate to the directory containing the `.mp4` files.
2. Execute the script:
   ```bash
   zsh path/to/convert-to-mp3
   ```

## Details
- **Audio Quality:** Variable bitrate (~192kbps) using `libmp3lame`.
- **Album Art:** Extracts the first video frame and attaches it as `attached_pic`.
- **Recursion:** Processes all `.mp4` files in the current directory and subdirectories.
- **Safety:** Skips files if an `.mp3` with the same name already exists.
