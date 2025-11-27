#!/usr/bin/env python3
"""
Smart Video Quiz Generator - CLI Pipeline Orchestrator

This script orchestrates the entire pipeline:
1. Extract slides from video (video-to-json) 
2. Transcribe audio from video (audio-to-json)  [run in parallel with step 1]
3. Generate quizzes using LLM (quiz-generator-LLM)

Usage:
    python run_pipeline.py path/to/video.mp4
    python run_pipeline.py path/to/video.mp4 --output ./my_output
    python run_pipeline.py path/to/video.mp4 --questions 15 --difficulty hard
"""

import os
import sys
import json
import argparse
import asyncio
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add module paths
ROOT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT_DIR / "video-to-json"))
sys.path.insert(0, str(ROOT_DIR / "audio-to-json" / "src" / "utils"))
sys.path.insert(0, str(ROOT_DIR / "quiz-generator-LLM"))


def extract_slides(video_path: str, output_dir: str) -> dict:
    """
    Extract slides from video using OCR-based detection.
    
    Returns:
        dict with slides metadata and output file path
    """
    from src.extractor import extract_slides as _extract_slides
    
    print("\n" + "=" * 50)
    print("🎬 STEP 1a: Extracting slides from video...")
    print("=" * 50)
    
    slides_output_dir = os.path.join(output_dir, "slides")
    os.makedirs(slides_output_dir, exist_ok=True)
    
    result = _extract_slides(
        video_path=video_path,
        output_dir=slides_output_dir,
        text_similarity_threshold=0.75,
        min_slide_duration=3.0,
        sample_rate=1.0,
        image_format="jpg",
        include_text_in_json=True,
    )
    
    # Copy metadata to standard location
    slides_json_path = os.path.join(output_dir, "slides.json")
    if result.get("status") == "success":
        # Read the generated metadata and save to output dir
        with open(result["metadata_file"], "r") as f:
            slides_data = json.load(f)
        with open(slides_json_path, "w") as f:
            json.dump(slides_data, f, indent=2)
        print(f"✅ Slides extracted: {result['slides_count']} slides")
        print(f"   Output: {slides_json_path}")
    
    return {
        "status": result.get("status"),
        "slides_count": result.get("slides_count", 0),
        "output_file": slides_json_path,
        "slides_dir": slides_output_dir
    }


def transcribe_audio(video_path: str, output_dir: str) -> dict:
    """
    Transcribe audio from video using Whisper.
    
    Returns:
        dict with transcription data and output file path
    """
    from faster_whisper import WhisperModel
    
    print("\n" + "=" * 50)
    print("🎙️ STEP 1b: Transcribing audio from video...")
    print("=" * 50)
    
    os.makedirs(output_dir, exist_ok=True)
    transcript_json_path = os.path.join(output_dir, "transcript.json")
    
    # Transcribe using faster-whisper
    model = WhisperModel("base", device="auto", compute_type="auto")
    segments, info = model.transcribe(video_path, beam_size=5)
    
    # Extract timestamped segments
    segments_data = [
        {
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        }
        for segment in segments
    ]
    
    # Save transcription to JSON
    with open(transcript_json_path, "w", encoding="utf-8") as f:
        json.dump(segments_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Audio transcribed: {len(segments_data)} segments")
    print(f"   Output: {transcript_json_path}")
    
    return {
        "status": "success",
        "segments_count": len(segments_data),
        "output_file": transcript_json_path
    }


async def run_extraction_parallel(video_path: str, output_dir: str) -> tuple:
    """
    Run slide extraction and audio transcription in parallel.
    
    Returns:
        Tuple of (slides_result, transcript_result)
    """
    loop = asyncio.get_event_loop()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both tasks
        slides_future = loop.run_in_executor(
            executor, extract_slides, video_path, output_dir
        )
        transcript_future = loop.run_in_executor(
            executor, transcribe_audio, video_path, output_dir
        )
        
        # Wait for both to complete
        slides_result, transcript_result = await asyncio.gather(
            slides_future, transcript_future
        )
    
    return slides_result, transcript_result


def generate_quizzes(
    transcript_path: str,
    slides_path: str,
    output_dir: str,
    num_questions: int = 10,
    difficulty: str = "medium"
) -> dict:
    """
    Generate quizzes using LLM (both multimodal and baseline).
    
    Returns:
        dict with paths to generated quiz files
    """
    from quiz_generator import QuizGenerator
    
    print("\n" + "=" * 50)
    print("🤖 STEP 2: Generating quizzes with LLM...")
    print("=" * 50)
    
    results = {
        "multimodal": None,
        "baseline": None
    }
    
    # Generate multimodal quiz (transcript + slides)
    print("\n--- Generating Multimodal Quiz (transcript + slides) ---")
    try:
        multimodal_output = os.path.join(output_dir, "quiz_multimodal.json")
        multimodal_generator = QuizGenerator(use_baseline=False)
        multimodal_quiz = multimodal_generator.generate_quiz(
            transcript_path=transcript_path,
            slides_path=slides_path,
            num_questions=num_questions,
            difficulty=difficulty
        )
        multimodal_generator.save_quiz(multimodal_quiz, multimodal_output)
        results["multimodal"] = multimodal_output
        print(f"✅ Multimodal quiz generated: {multimodal_output}")
    except Exception as e:
        print(f"❌ Multimodal quiz generation failed: {e}")
    
    # Generate baseline quiz (transcript only)
    print("\n--- Generating Baseline Quiz (transcript only) ---")
    try:
        baseline_output = os.path.join(output_dir, "quiz_baseline.json")
        baseline_generator = QuizGenerator(use_baseline=True)
        baseline_quiz = baseline_generator.generate_quiz(
            transcript_path=transcript_path,
            slides_path=None,
            num_questions=num_questions,
            difficulty=difficulty
        )
        baseline_generator.save_quiz(baseline_quiz, baseline_output)
        results["baseline"] = baseline_output
        print(f"✅ Baseline quiz generated: {baseline_output}")
    except Exception as e:
        print(f"❌ Baseline quiz generation failed: {e}")
    
    return results


def run_pipeline(
    video_path: str,
    output_dir: str = "./output",
    num_questions: int = 10,
    difficulty: str = "medium",
    skip_extraction: bool = False
) -> dict:
    """
    Run the complete pipeline.
    
    Args:
        video_path: Path to input video file
        output_dir: Directory for all outputs
        num_questions: Number of quiz questions to generate
        difficulty: Quiz difficulty (easy, medium, hard, mixed)
        skip_extraction: Skip extraction if JSON files already exist
        
    Returns:
        dict with all results and output paths
    """
    start_time = time.time()
    
    print("\n" + "=" * 70)
    print("🎓 SMART VIDEO QUIZ GENERATOR - Pipeline Started")
    print("=" * 70)
    print(f"\n📁 Input video: {video_path}")
    print(f"📂 Output directory: {output_dir}")
    print(f"❓ Questions: {num_questions}")
    print(f"📊 Difficulty: {difficulty}")
    
    # Validate input
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if we can skip extraction
    slides_json = os.path.join(output_dir, "slides.json")
    transcript_json = os.path.join(output_dir, "transcript.json")
    
    if skip_extraction and os.path.exists(slides_json) and os.path.exists(transcript_json):
        print("\n⏭️ Skipping extraction (JSON files already exist)")
        slides_result = {"status": "skipped", "output_file": slides_json}
        transcript_result = {"status": "skipped", "output_file": transcript_json}
    else:
        # Step 1: Run extraction in parallel
        print("\n" + "-" * 70)
        print("PHASE 1: Content Extraction (parallel processing)")
        print("-" * 70)
        
        slides_result, transcript_result = asyncio.run(
            run_extraction_parallel(video_path, output_dir)
        )
    
    # Step 2: Generate quizzes
    print("\n" + "-" * 70)
    print("PHASE 2: Quiz Generation")
    print("-" * 70)
    
    quiz_results = generate_quizzes(
        transcript_path=transcript_json,
        slides_path=slides_json,
        output_dir=output_dir,
        num_questions=num_questions,
        difficulty=difficulty
    )
    
    # Summary
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\n⏱️ Total time: {elapsed_time:.1f} seconds")
    print(f"\n📂 Output files in: {output_dir}/")
    print(f"   ├── slides.json          (slide metadata)")
    print(f"   ├── slides/              (slide images)")
    print(f"   ├── transcript.json      (audio transcription)")
    print(f"   ├── quiz_multimodal.json (transcript + slides quiz)")
    print(f"   └── quiz_baseline.json   (transcript-only quiz)")
    print("=" * 70)
    
    return {
        "status": "success",
        "video_path": video_path,
        "output_dir": output_dir,
        "slides": slides_result,
        "transcript": transcript_result,
        "quizzes": quiz_results,
        "processing_time": elapsed_time
    }


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate educational quizzes from video content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py lecture.mp4
  python run_pipeline.py lecture.mp4 --output ./my_output
  python run_pipeline.py lecture.mp4 --questions 15 --difficulty hard
  python run_pipeline.py lecture.mp4 --skip-extraction  # reuse existing JSONs
        """
    )
    
    parser.add_argument(
        "video",
        type=str,
        help="Path to input video file (MP4, AVI, MOV, MKV)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./output",
        help="Output directory (default: ./output)"
    )
    parser.add_argument(
        "--questions", "-q",
        type=int,
        default=10,
        help="Number of quiz questions to generate (default: 10)"
    )
    parser.add_argument(
        "--difficulty", "-d",
        type=str,
        choices=["easy", "medium", "hard", "mixed"],
        default="medium",
        help="Quiz difficulty level (default: medium)"
    )
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Skip extraction if slides.json and transcript.json already exist"
    )
    
    args = parser.parse_args()
    
    try:
        result = run_pipeline(
            video_path=args.video,
            output_dir=args.output,
            num_questions=args.questions,
            difficulty=args.difficulty,
            skip_extraction=args.skip_extraction
        )
        sys.exit(0 if result["status"] == "success" else 1)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
