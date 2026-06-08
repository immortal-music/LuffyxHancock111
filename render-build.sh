#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Download and install Static FFmpeg locally for Render
if [ ! -d "ffmpeg" ]; then
  echo "Downloading FFmpeg..."
  curl -L -o ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
  tar -xf ffmpeg.tar.xz
  rm ffmpeg.tar.xz
  mv ffmpeg-*-amd64-static ffmpeg
  echo "FFmpeg installed successfully!"
fi
