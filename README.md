# 🎓 Slide Extractor - Educational Video Processing

Extract slides from educational videos automatically using OCR (Optical Character Recognition). This module intelligently detects slide changes based on text content, perfect for processing lecture recordings where slides are displayed alongside instructor video.

## ✨ Features

- 🔍 **OCR-Based Detection**: Uses text comparison instead of pixel comparison
- 🎯 **Smart Filtering**: Ignores instructor video, cursor movements, and minor changes
- 📊 **Incremental Slide Merging**: Combines bullet points that appear one-by-one
- ⚡ **Optimized Processing**: Pre-filtering with perceptual hashing before OCR
- 📝 **Rich Metadata**: Outputs JSON with timestamps, extracted text, and confidence scores
- 🔧 **Highly Configurable**: Adjust thresholds, sampling rate, and output format
- 💻 **Server-Ready**: Designed for integration with backend services

## 📋 Requirements

- Python 3.8+
- Tesseract OCR (must be installed separately)
- OpenCV
- pytesseract

## 🚀 Quick Start

### 1. Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

### 2. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run OpenAI Whisper
## Setup

We used Python 3.9.9 and [PyTorch](https://pytorch.org/) 1.10.1 to train and test our models, but the codebase is expected to be compatible with Python 3.8-3.11 and recent PyTorch versions. The codebase also depends on a few Python packages, most notably [OpenAI's tiktoken](https://github.com/openai/tiktoken) for their fast tokenizer implementation. You can download and install (or update to) the latest release of Whisper with the following command:

    pip install -U openai-whisper

Alternatively, the following command will pull and install the latest commit from this repository, along with its Python dependencies:

    pip install git+https://github.com/openai/whisper.git 

To update the package to the latest version of this repository, please run:

    pip install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git

It also requires the command-line tool [`ffmpeg`](https://ffmpeg.org/) to be installed on your system, which is available from most package managers:

```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```
### 4. Run Example

```python
from src import extract_slides

result = extract_slides(
    video_path="lecture.mp4",
    output_dir="./output"
)

print(f"Extracted {result['slides_count']} slides!")
```

## 📖 Usage

### Basic Usage

```python
from src import extract_slides

result = extract_slides(
    video_path="path/to/lecture.mp4",
    output_dir="./slides_output"
)
```

### Advanced Configuration

```python
result = extract_slides(
    video_path="lecture.mp4",
    output_dir="./output",
    
    # Detection settings
    text_similarity_threshold=0.75,  # Lower = more sensitive (0-1)
    min_slide_duration=3.0,          # Minimum seconds per slide
    ocr_confidence_threshold=0.70,   # Skip low-quality OCR (0-1)
    
    # Sampling
    sample_rate=1.0,                 # Frames per second to analyze
    
    # Output
    image_format="jpg",              # jpg, png, or webp
    image_quality=85,                # Quality for jpg/webp (1-100)
    include_text_in_json=True,       # Include extracted text
    
    # Advanced
    incremental_merge=True,          # Merge incremental slides
    progress_callback=None           # Function for progress updates
)
```

### With Progress Tracking

```python
def progress_handler(data):
    print(f"Progress: {data['progress']:.1f}% - Slides: {data['slides_found']}")

result = extract_slides(
    video_path="lecture.mp4",
    output_dir="./output",
    progress_callback=progress_handler
)
```

## 📂 Output Structure

```
output/
├── slide_001.jpg          # First slide image
├── slide_002.jpg          # Second slide image
├── slide_003.jpg          # Third slide image
└── slides_metadata.json   # Metadata for all slides
```

### Metadata JSON Format

```json
{
  "videoFile": "lecture.mp4",
  "totalSlides": 15,
  "processingTime": 125.3,
  "extractionDate": "2025-11-04T10:30:00Z",
  "slides": [
    {
      "imageFile": "slide_001.jpg",
      "startTime": "00:00:05",
      "endTime": "00:02:30",
      "startTimeMs": 5000,
      "endTimeMs": 150000,
      "duration": 145.0,
      "extractedText": "Introduction to Machine Learning\n• Definition\n• Applications",
      "ocrConfidence": 0.92
    }
  ]
}
```

## ⚙️ Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `video_path` | str | *required* | Path to input video file |
| `output_dir` | str | `"./output"` | Output directory for slides |
| `text_similarity_threshold` | float | `0.75` | Slides must differ by this much (0-1) |
| `min_slide_duration` | float | `3.0` | Minimum slide duration in seconds |
| `ocr_confidence_threshold` | float | `0.70` | Minimum OCR confidence (0-1) |
| `sample_rate` | float | `1.0` | Frames per second to sample |
| `image_format` | str | `"jpg"` | Output format: jpg, png, webp |
| `image_quality` | int | `85` | JPEG/WebP quality (1-100) |
| `include_text_in_json` | bool | `True` | Include extracted text in JSON |
| `incremental_merge` | bool | `True` | Merge incremental slides |

## 🔧 Algorithm Overview

1. **Frame Sampling**: Extract frames at specified rate (default 1 FPS)
2. **Pre-filtering**: Quick perceptual hash comparison to skip identical frames
3. **Image Preprocessing**: Apply adaptive thresholding for better OCR
4. **OCR Extraction**: Extract text using Tesseract OCR
5. **Text Comparison**: Compare with previous slide using hybrid similarity
6. **Slide Detection**: Identify new slides based on text differences
7. **Incremental Merging**: Combine slides that are progressive versions
8. **Duration Filtering**: Remove slides shorter than minimum duration
9. **Output Generation**: Save images and generate JSON metadata

## 🎯 How It Works

### Text-Based Detection vs Pixel Comparison

This module uses **OCR-based text comparison** rather than pixel comparison, which has several advantages:

✅ **Ignores instructor video window** - No need to crop or mask
✅ **Robust to minor changes** - Cursor movements, slight video quality changes
✅ **Semantic accuracy** - Detects actual content changes, not visual artifacts
✅ **Handles animations** - Ignores transitions and effects

### Incremental Slide Handling

Educational videos often show bullet points appearing one by one:

```
Slide State 1:           Slide State 2:           Slide State 3:
• Point 1                • Point 1                • Point 1
                         • Point 2                • Point 2
                                                  • Point 3
```

With `incremental_merge=True` (default), these are combined into a single slide showing the final state.

## 🔗 Server Integration Example

```python
from flask import Flask, request, jsonify
from src import extract_slides

app = Flask(__name__)

@app.route('/api/process-video', methods=['POST'])
def process_video():
    video_file = request.files['video']
    video_path = f"./uploads/{video_file.filename}"
    video_file.save(video_path)
    
    result = extract_slides(
        video_path=video_path,
        output_dir=f"./output/{video_file.filename}",
        progress_callback=lambda p: socketio.emit('progress', p)
    )
    
    return jsonify(result)
```

## 🐛 Troubleshooting

### Tesseract Not Found

```
RuntimeError: Tesseract OCR not found
```

**Solution**: Install Tesseract (see Quick Start section)

### Low Slide Count

If too few slides are detected:
- Lower `text_similarity_threshold` (e.g., 0.65)
- Lower `min_slide_duration` (e.g., 2.0)
- Lower `ocr_confidence_threshold` (e.g., 0.60)

### Too Many Slides

If too many slides are detected:
- Increase `text_similarity_threshold` (e.g., 0.85)
- Increase `min_slide_duration` (e.g., 5.0)
- Enable `incremental_merge=True`

### Poor OCR Quality

- Increase `sample_rate` for better frame selection
- Check video resolution (higher is better)
- Ensure slides have good contrast

## 📦 Project Structure

```
extract-slides-from-video/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── extractor.py             # Main extract_slides() function
│   ├── video_processor.py       # Video frame extraction
│   ├── ocr_engine.py            # Tesseract OCR wrapper
│   ├── text_comparator.py       # Text similarity algorithms
│   ├── slide_detector.py        # Slide detection logic
│   └── utils/
│       ├── time_utils.py        # Timestamp conversions
│       ├── image_utils.py       # Image preprocessing
│       └── file_manager.py      # File I/O operations
├── example.py                   # Usage examples
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🤝 Contributing

This is part of the CS7980 Smart Video Quiz Generator project.

## 📄 License

ISC License

## 🔮 Future Enhancements

- [ ] Diagram/image detection alongside text
- [ ] Docker containerization
- [ ] Batch processing support
- [ ] Web UI for configuration
