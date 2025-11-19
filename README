# Smart Video Quiz Generator

Automated pipeline for extracting structured content from educational videos to generate quizzes.

## Components

### 🎬 video-to-json
Extracts slides from lecture videos using OCR-based detection.
- **Features**: Smart slide detection, incremental merging, text extraction
- **Tech**: OpenCV, Tesseract OCR, Python 3.8+
- **Output**: Slide images + JSON metadata with timestamps

### 🎙️ audio-to-json
Transcribes video audio to text using OpenAI Whisper.
- **Features**: Speech-to-text transcription
- **Tech**: OpenAI Whisper, PyTorch, ffmpeg
- **Output**: Timestamped transcription JSON

## Quick Start

```bash
# Install Tesseract OCR (macOS)
brew install tesseract ffmpeg

# Setup video processing
cd video-to-json
pip install -r requirements.txt

# Setup audio transcription
cd audio-to-json
pip install -r requirements.txt
```

## Usage

```python
# Extract slides
from video_to_json import extract_slides
slides = extract_slides("lecture.mp4", output_dir="./output")

# Transcribe audio
from audio_to_json import transcribe_video
transcript = transcribe_video("lecture.mp4")
```

## Requirements
- Python 3.8+
- Tesseract OCR
- ffmpeg
- PyTorch (for Whisper)
