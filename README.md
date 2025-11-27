# Smart Video Quiz Generator

End-to-end pipeline for automatically generating quizzes from educational videos using multimodal AI.

## 📁 Project Structure

| Folder | Description |
|--------|-------------|
| `video-to-json/` | Slide extraction from lecture videos using OCR |
| `audio-to-json/` | Audio transcription using OpenAI Whisper |
| `quiz-generator-LLM/` | Quiz generation using Groq LLM API |
| `evaluation/` | Evaluation pipeline comparing multimodal vs baseline |

## 🚀 Pipeline Overview

```
                    test_video.mp4
                          │
            ┌─────────────┴─────────────┐
            │  (parallel processing)    │
            ▼                           ▼
    ┌───────────────┐           ┌───────────────┐
    │ video-to-json │           │ audio-to-json │
    └───────┬───────┘           └───────┬───────┘
            │                           │
            ▼                           ▼
      slides.json                transcript.json
            │                           │
            └─────────────┬─────────────┘
                          ▼
               ┌─────────────────────┐
               │  quiz-generator-LLM │
               └──────────┬──────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
    quiz_multimodal.json         quiz_baseline.json
```

## Quick Start

```bash
# 1. Install system dependencies (macOS)
brew install tesseract ffmpeg

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set up Groq API key
export GROQ_API_KEY=your_api_key_here

# 4. Run the pipeline
python run_pipeline.py test_video.mp4
```

## Usage

```bash
# Basic usage
python run_pipeline.py lecture.mp4

# Custom output directory
python run_pipeline.py lecture.mp4 --output ./my_output

# Configure quiz generation
python run_pipeline.py lecture.mp4 --questions 15 --difficulty hard

# Skip extraction (reuse existing JSONs)
python run_pipeline.py lecture.mp4 --skip-extraction
```

## Output

```
output/
├── slides.json           # Slide metadata with timestamps
├── slides/               # Extracted slide images
├── transcript.json       # Audio transcription
├── quiz_multimodal.json  # Quiz using slides + transcript
└── quiz_baseline.json    # Quiz using transcript only
```

## Components

### 🎬 video-to-json
Extracts slides from lecture videos using OCR-based detection.
- **Features**: Smart slide detection, incremental merging, text extraction
- **Tech**: OpenCV, Tesseract OCR, Python 3.8+
- **Output**: Slide images + JSON metadata with timestamps

### 🎙️ audio-to-json
Transcribes video audio to text using OpenAI Whisper.
- **Features**: Speech-to-text transcription
- **Tech**: faster-whisper, PyTorch, ffmpeg
- **Output**: Timestamped transcription JSON

### 🤖 quiz-generator-LLM
Generates quizzes from extracted content using LLMs.
- **Features**: Multimodal (slides + transcript) & baseline (transcript-only) modes
- **Tech**: Groq API, Python 3.8+
- **Output**: Quiz JSON with questions, answers, explanations, and references

### 📊 evaluation
Compares multimodal vs transcript-only quiz generation quality.
- **Metrics**: BERTScore, ROUGE-1, ROUGE-L, BLEU
- **Data**: Human reference questions for validation

## Requirements
- Python 3.8+
- Tesseract OCR
- ffmpeg
- Groq API key (for quiz generation)
