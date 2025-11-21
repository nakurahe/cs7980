# Educational Video Quiz Generator

Automatically generate comprehensive quizzes from educational video content using AI. This tool supports two generation modes for comparison: **multimodal** (transcript + slides) and **baseline** (transcript only).

## Features

- Two generation modes for A/B comparison
  - Multimodal: Uses both transcript and slides data
  - Baseline: Uses transcript only
- Batch processing for multiple videos
- Powered by Groq's high-performance LLM API
- Customizable difficulty levels (easy, medium, hard, mixed)
- Includes timestamp and slide references
- Detailed explanations for each answer
- Easy configuration via environment variables

## Prerequisites

- Python 3.8 or higher
- Groq API key (get one at [console.groq.com](https://console.groq.com))

## Installation

### 1. Clone the Repository

```bash
git clone
cd quiz-generator
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root:

```bash
# For multimodal quiz generation
GROQ_API_KEY=your_groq_api_key_here

# For baseline quiz generation (can be same as above)
BASELINE_API_KEY=your_groq_api_key_here

# Optional: specify different models
# GROQ_MODEL=llama-3.3-70b-versatile
# BASELINE_MODEL=llama-3.3-70b-versatile
```

**Note:** You can use the same API key for both if you're using the same Groq account.

## Usage

### Batch Mode (Recommended for Multiple Videos)

Generate all quizzes at once from your data folder:

```bash
# Generate all quizzes (quiz0-9 and baseline0-9)
python main.py --batch

# Process only first 5 videos
python main.py --batch --num-videos 5

# Generate quizzes for videos 10-12 only (useful when adding new videos)
python main.py --batch --start-index 10 --num-videos 3

# Process videos 5-9
python main.py --batch --start-index 5 --num-videos 5

# Generate 15 questions per quiz with hard difficulty
python main.py --batch --questions 15 --difficulty hard
```

**Expected file structure in `data/` folder:**

```
data/
├── transcript0.json
├── slides0.json
├── transcript1.json
├── slides1.json
├── ...
├── transcript9.json
└── slides9.json
```

**Generated output in `output/` folder:**

```
output/
├── quiz0.json          # Multimodal (transcript + slides)
├── baseline0.json      # Baseline (transcript only)
├── quiz1.json
├── baseline1.json
├── ...
├── quiz9.json
└── baseline9.json
```

### Single Quiz Mode

Generate a single quiz for testing:

```bash
# Multimodal mode (transcript + slides)
python main.py --transcript data/transcript0.json \
               --slides data/slides0.json \
               --output output/test_quiz.json

# Baseline mode (transcript only)
python main.py --transcript data/transcript0.json \
               --baseline \
               --output output/test_baseline.json
```

### Command Line Arguments

| Argument        | Description                           | Default        |
| --------------- | ------------------------------------- | -------------- |
| `--batch`       | Enable batch processing mode          | False          |
| `--num-videos`  | Number of videos to process           | 10             |
| `--start-index` | Starting video index (batch mode)     | 0              |
| `--transcript`  | Path to transcript JSON (single mode) | None           |
| `--slides`      | Path to slides JSON (single mode)     | None           |
| `--output`      | Output path for quiz                  | Auto-generated |
| `--baseline`    | Use baseline mode (transcript only)   | False          |
| `--questions`   | Number of questions                   | 10             |
| `--difficulty`  | Difficulty level                      | medium         |

## Generation Modes Comparison

### Multimodal Mode (transcript + slides)

- Uses both transcript text and slide content
- Richer context for question generation
- Can reference specific slides
- Output files: `quiz0.json` to `quiz9.json`

### Baseline Mode (transcript only)

- Uses only transcript text
- Serves as comparison baseline
- Faster generation (less context)
- Output files: `baseline0.json` to `baseline9.json`

This allows you to compare quiz quality between the two approaches!

## Input File Format

### transcript.json

```json
[
  {
    "start": 0.0,
    "end": 14.0,
    "text": "Transcript text here..."
  }
]
```

### slides.json

```json
{
  "videoFile": "video.mp4",
  "totalSlides": 10,
  "slides": [
    {
      "imageFile": "slide_001.jpg",
      "startTime": "00:00:00",
      "endTime": "00:00:15",
      "extractedText": "Slide content..."
    }
  ]
}
```

## Output Format

The generated quiz JSON includes:

```json
{
  "quiz_metadata": {
    "title": "Quiz Title",
    "description": "Quiz description",
    "total_questions": 10,
    "difficulty": "mixed"
  },
  "questions": [
    {
      "question_number": 1,
      "question_text": "Question text?",
      "options": [
        { "id": "A", "text": "Option A" },
        { "id": "B", "text": "Option B" },
        { "id": "C", "text": "Option C" },
        { "id": "D", "text": "Option D" }
      ],
      "correct_answer": "A",
      "explanation": "Explanation...",
      "difficulty": "medium",
      "topic": "Topic covered",
      "reference": "00:05:30 or Slide 3"
    }
  ]
}
```

## Project Structure

```
quiz-generator/
├── .env                    # API keys (not in git)
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── config.py             # Configuration management
├── quiz_generator.py     # Core quiz generation logic
├── main.py               # CLI entry point
├── data/                 # Input data
│   ├── transcript0.json
│   ├── slides0.json
│   ├── transcript1.json
│   ├── slides1.json
│   └── ...
└── output/               # Generated quizzes
    ├── quiz0.json
    ├── baseline0.json
    └── ...
```

## Troubleshooting

### API Key Issues

Make sure your `.env` file has both keys:

```
GROQ_API_KEY=your_key_here
BASELINE_API_KEY=your_key_here
```

### Missing Files in Batch Mode

The system will skip videos with missing files and continue processing others. Check the summary at the end for success/failure counts.

### File Naming

- Files must be named exactly: `transcript0.json`, `slides0.json`, etc.
- Numbers should be consecutive (but can have gaps - the system will skip missing ones)
- Both transcript and slides needed for multimodal mode
- Only transcript needed for baseline mode

### Processing Specific Video Ranges

If you want to regenerate quizzes for specific videos (e.g., after updating their content):

```bash
# Regenerate only videos 3, 4, 5
python main.py --batch --start-index 3 --num-videos 3
```

## Examples

### Generate All Quizzes (Default Settings)

```bash
# Generate quizzes for videos 0-9
python main.py --batch
```

### Add New Videos and Generate Only New Quizzes

```bash
# After adding transcript10.json, slides10.json, transcript11.json, slides11.json
# Generate only the new quizzes without regenerating existing ones
python main.py --batch --start-index 10 --num-videos 2
```

### Generate Specific Range of Videos

```bash
# Generate quizzes for videos 3-7
python main.py --batch --start-index 3 --num-videos 5
```

### Generate with Custom Settings

```bash
# Videos 0-4 with 15 questions each, hard difficulty
python main.py --batch --start-index 0 --num-videos 5 --questions 15 --difficulty hard
```

### Test Single Video

```bash
python main.py --transcript data/transcript0.json \
               --slides data/slides0.json \
               --output output/test.json \
               --questions 5 \
               --difficulty easy
```
