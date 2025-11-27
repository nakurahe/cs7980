# Smart Video Quiz Generator

End-to-end pipeline for automatically generating quizzes from educational videos using multimodal AI.

## 📁 Project Structure

| Folder | Description |
|--------|-------------|
| `video-to-json/` | Slide extraction from lecture videos using OCR |
| `audio-to-json/` | Audio transcription using OpenAI Whisper |
| `quiz-generator-LLM/` | Quiz generation using Groq LLM API |
| `evaluation/` | Evaluation pipeline comparing multimodal vs baseline |

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

### 🤖 quiz-generator-LLM
Generates quizzes from extracted content using LLMs.
- **Features**: Multimodal (slides + transcript) & baseline (transcript-only) modes
- **Tech**: Groq API, Python 3.8+
- **Output**: Quiz JSON with questions, answers, explanations, and references

### 📊 evaluation
Compares multimodal vs transcript-only quiz generation quality.
- **Metrics**: BERTScore, ROUGE-1, ROUGE-L, BLEU
- **Data**: Human reference questions for validation

## Quick Start

```bash
# Install system dependencies (macOS)
brew install tesseract ffmpeg

# Setup each component
cd video-to-json && pip install -r requirements.txt
cd ../audio-to-json && pip install -r requirements.txt
cd ../quiz-generator-LLM && pip install -r requirements.txt
```

## Requirements
- Python 3.8+
- Tesseract OCR
- ffmpeg
- Groq API key (for quiz generation)
