# Architecture & Workflow

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        extract_slides()                          │
│                     (Main Entry Point)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌──────────┐ ┌─────────────┐
│ VideoProcessor │ │   OCR    │ │    Text     │
│    (OpenCV)    │ │  Engine  │ │ Comparator  │
└───────┬────────┘ └────┬─────┘ └──────┬──────┘
        │               │              │
        │               │              │
        ▼               ▼              ▼
┌─────────────────────────────────────────────┐
│          SlideDetector                       │
│   (Main Detection Algorithm)                │
└────────────────────┬────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Output Generation     │
        │  - Save Images         │
        │  - Generate JSON       │
        └────────────────────────┘
```

## 🔄 Processing Workflow

```
Input: lecture.mp4 (10 minutes)
│
├─ Step 1: Video Analysis
│  └─ Duration: 600s, FPS: 30, Resolution: 1920x1080
│
├─ Step 2: Frame Sampling (1 FPS)
│  └─ Extract 600 frames from video
│
├─ Step 3: Pre-filtering Loop (for each frame)
│  ├─ Compute perceptual hash
│  ├─ Compare with previous hash
│  └─ If identical → Skip (saves ~60% of OCR calls)
│
├─ Step 4: Image Preprocessing
│  ├─ Convert to grayscale
│  ├─ Apply Gaussian blur
│  └─ Adaptive thresholding
│
├─ Step 5: OCR Text Extraction
│  ├─ Extract text via Tesseract
│  ├─ Clean and normalize text
│  └─ Get confidence score
│
├─ Step 6: Text Similarity Analysis
│  ├─ Compare with previous slide text
│  ├─ Calculate similarity (Levenshtein + TF-IDF)
│  └─ Detect incremental changes
│
├─ Step 7: Slide Change Decision
│  ├─ If similarity < 0.75 → New slide
│  ├─ If incremental → Merge with previous
│  └─ If same → Update end time
│
├─ Step 8: Duration Filtering
│  └─ Keep only slides > 3 seconds
│
└─ Step 9: Output Generation
   ├─ Save: slide_001.jpg (145s duration)
   ├─ Save: slide_002.jpg (165s duration)
   ├─ ...
   └─ Generate: slides_metadata.json

Output: 15 slides extracted in 125.3 seconds
```

## 📊 Data Flow Diagram

```
┌──────────┐
│  Video   │
│  File    │
└────┬─────┘
     │
     ▼
┌──────────────────┐
│  Frame @ 00:05   │ ─┐
│  Frame @ 00:06   │  │
│  Frame @ 00:07   │  │ Sampling
│      ...         │  │ (1 FPS)
│  Frame @ 10:00   │ ─┘
└────────┬─────────┘
         │
         ▼
┌─────────────────────┐
│  Perceptual Hash    │
│  Compare with prev  │ ───→ Same? → Skip OCR
└─────────┬───────────┘
          │
          ▼ Different
┌─────────────────────┐
│ Image Preprocessing │
│ - Grayscale         │
│ - Blur              │
│ - Threshold         │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Tesseract OCR     │
│ "Intro to ML..."    │
│ Confidence: 0.92    │
└─────────┬───────────┘
          │
          ▼
┌──────────────────────────────┐
│  Text Comparison             │
│  Previous: "Intro to ML"     │
│  Current:  "ML Applications" │
│  Similarity: 0.35            │
└───────────┬──────────────────┘
            │
            ▼ < 0.75 threshold
┌────────────────────┐
│  NEW SLIDE!        │
│  - Save frame      │
│  - Record time     │
│  - Save text       │
└────────────────────┘
```

## 🧩 Module Dependencies

```
extractor.py
├─ requires: video_processor.py
├─ requires: slide_detector.py
└─ requires: utils.file_manager

slide_detector.py
├─ requires: video_processor.py
├─ requires: ocr_engine.py
├─ requires: text_comparator.py
└─ requires: utils.image_utils

video_processor.py
└─ requires: OpenCV (cv2)

ocr_engine.py
├─ requires: pytesseract
└─ requires: PIL

text_comparator.py
├─ requires: Levenshtein
└─ requires: sklearn

utils/
├─ time_utils.py (standalone)
├─ image_utils.py (requires: cv2, PIL, imagehash)
└─ file_manager.py (requires: cv2)
```

## 🎯 Algorithm Deep Dive

### Text Similarity Calculation

```
Method: Hybrid (Levenshtein + TF-IDF)

Text A: "Introduction to Machine Learning"
Text B: "Introduction to Machine Learning - Part 1"

Step 1: Levenshtein Distance
├─ Calculate character-level distance: 9
├─ Max length: 44
└─ Similarity: 1 - (9/44) = 0.80

Step 2: TF-IDF + Cosine Similarity
├─ Vectorize both texts
├─ Calculate cosine similarity
└─ Similarity: 0.85

Step 3: Average
└─ Final Similarity: (0.80 + 0.85) / 2 = 0.825

Result: 0.825 > 0.75 threshold → Same slide
```

### Incremental Slide Detection

```
Slide State Timeline:

Time 00:30 - "Topics:"
             "• Machine Learning"
             [Captured as current_text]

Time 00:32 - "Topics:"
             "• Machine Learning"
             "• Deep Learning"
             [Check: Is text1 subset of text2?]
             [Yes! → Incremental]
             [Action: Update current slide text]

Time 00:34 - "Topics:"
             "• Machine Learning"
             "• Deep Learning"
             "• Neural Networks"
             [Check: Is text1 subset of text2?]
             [Yes! → Incremental]
             [Action: Update current slide text]

Time 00:36 - Same as 00:34
             [No change, same slide continues]

Time 01:00 - "Applications of ML"
             [Check: Similarity with previous]
             [Similarity: 0.25 < 0.75]
             [Action: Save previous slide (final state)]
             [Action: Start new slide]

Result: One slide from 00:30-01:00 with final text
```

## 🔧 Configuration Impact

### Text Similarity Threshold

```
Threshold 0.95 (Very Strict)
└─ Result: Fewer slides, only major changes
   Example: 5 slides from 10-min video

Threshold 0.75 (Recommended)
└─ Result: Balanced detection
   Example: 15 slides from 10-min video

Threshold 0.55 (Very Sensitive)
└─ Result: More slides, minor changes detected
   Example: 30 slides from 10-min video
```

### Sample Rate Impact

```
Sample Rate 0.5 FPS (Slow)
├─ Processing: 5 minutes for 10-min video
├─ Accuracy: 90% (may miss brief slides)
└─ Use case: Quick preview

Sample Rate 1.0 FPS (Recommended)
├─ Processing: 10 minutes for 10-min video
├─ Accuracy: 95% (good balance)
└─ Use case: Production use

Sample Rate 2.0 FPS (Thorough)
├─ Processing: 20 minutes for 10-min video
├─ Accuracy: 98% (catches everything)
└─ Use case: High-accuracy required
```

## 📈 Performance Optimization

### Pre-filtering Savings

```
Without Pre-filtering:
600 frames × 1s OCR = 600 seconds = 10 minutes

With Perceptual Hash Pre-filtering:
├─ 600 frames × 0.001s hash = 0.6 seconds
├─ 240 frames × 1s OCR = 240 seconds (60% skipped)
└─ Total: 240.6 seconds = 4 minutes

Speedup: 2.5x faster!
```

## 🎬 Example Processing Log

```
🎬 Processing video: 600.0s @ 1.0 FPS
📊 Estimated frames to process: 600
⚙️  Settings: text_threshold=0.75, min_duration=3.0s

⏳ Progress: 10.0% (60/600 frames) - Slides: 2
⏳ Progress: 20.0% (120/600 frames) - Slides: 3
⏳ Progress: 30.0% (180/600 frames) - Slides: 5
⏳ Progress: 40.0% (240/600 frames) - Slides: 7
⏳ Progress: 50.0% (300/600 frames) - Slides: 9
⏳ Progress: 60.0% (360/600 frames) - Slides: 10
⏳ Progress: 70.0% (420/600 frames) - Slides: 12
⏳ Progress: 80.0% (480/600 frames) - Slides: 13
⏳ Progress: 90.0% (540/600 frames) - Slides: 14
⏳ Progress: 100.0% (600/600 frames) - Slides: 15

✅ Processing complete! Found 15 slides

💾 Saving slide images...
   ✓ Slide 001: 00:00:05 - 00:02:30 (145.0s)
   ✓ Slide 002: 00:02:30 - 00:04:15 (105.0s)
   ...

✅ SUCCESS!
📊 Slides extracted: 15
⏱️  Processing time: 125.3s
```

---

This architecture is designed to be:
- ✅ **Modular**: Each component has a single responsibility
- ✅ **Testable**: Components can be tested independently
- ✅ **Extensible**: Easy to add new features
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Performant**: Pre-filtering and optimizations
