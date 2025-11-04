"""Main extractor module - primary entry point"""

import os
import time
from typing import Dict, Any, Optional, Callable

from .video_processor import VideoProcessor
from .slide_detector import SlideDetector
from .utils.file_manager import save_slide_image, save_metadata_json, get_video_info


def extract_slides(
    video_path: str,
    output_dir: str = "./output",
    text_similarity_threshold: float = 0.75,
    min_slide_duration: float = 3.0,
    ocr_confidence_threshold: float = 0.70,
    sample_rate: float = 1.0,
    image_format: str = "jpg",
    image_quality: int = 85,
    include_text_in_json: bool = True,
    incremental_merge: bool = True,
    remove_duplicates: bool = True,
    progress_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Extract slides from educational video using OCR-based detection
    
    This function processes a video file, detects slide changes based on text content,
    and outputs individual slide images along with metadata in JSON format.
    
    Args:
        video_path: Path to input MP4 video file
        output_dir: Directory for output files (default: "./output")
        text_similarity_threshold: Threshold for considering slides different, 0-1 (default: 0.75)
                                   Lower = more sensitive to changes
        min_slide_duration: Minimum duration for a slide in seconds (default: 3.0)
                           Filters out brief transitions
        ocr_confidence_threshold: Minimum OCR confidence to accept, 0-1 (default: 0.70)
                                 Skip frames with low quality text detection
        sample_rate: Frames per second to sample (default: 1.0)
                    Higher = more accurate but slower
        image_format: Output image format - "jpg", "png", or "webp" (default: "jpg")
        image_quality: JPEG/WebP quality, 1-100 (default: 85)
        include_text_in_json: Include extracted text in JSON output (default: True)
        incremental_merge: Merge incremental slides into one (default: True)
                          E.g., bullet points appearing one by one
        remove_duplicates: Remove consecutive duplicate slides (default: True)
                          Removes same slide during continuous time span,
                          but keeps it when instructor revisits later
        progress_callback: Optional callback function for progress updates
                          Receives dict with keys: frame_count, total_frames, progress, slides_found
    
    Returns:
        Dictionary with:
            - status: "success" or "error"
            - slides_count: Number of slides extracted
            - output_dir: Path to output directory
            - metadata_file: Path to JSON metadata file
            - slides: List of slide metadata
            - processing_time: Time taken in seconds
            - video_info: Information about input video
    
    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If invalid parameters provided
        RuntimeError: If Tesseract OCR is not installed
    
    Example:
        >>> result = extract_slides(
        ...     video_path="lecture.mp4",
        ...     output_dir="./slides_output",
        ...     text_similarity_threshold=0.75,
        ...     min_slide_duration=3.0
        ... )
        >>> print(f"Extracted {result['slides_count']} slides")
        >>> print(f"Metadata saved to: {result['metadata_file']}")
    """
    
    print("=" * 70)
    print("🎓 SLIDE EXTRACTOR - Educational Video Processing")
    print("=" * 70)
    
    start_time = time.time()
    
    # Validate inputs
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not video_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise ValueError("Video must be MP4, AVI, MOV, or MKV format")
    
    if not (0 < text_similarity_threshold <= 1):
        raise ValueError("text_similarity_threshold must be between 0 and 1")
    
    if min_slide_duration < 0:
        raise ValueError("min_slide_duration must be positive")
    
    print(f"\n📁 Input: {video_path}")
    print(f"📂 Output: {output_dir}")
    
    try:
        # Get video info
        video_info = get_video_info(video_path)
        print(f"\n📹 Video Info:")
        print(f"   Duration: {video_info['duration_seconds']:.1f}s")
        print(f"   Resolution: {video_info['width']}x{video_info['height']}")
        print(f"   FPS: {video_info['fps']:.1f}")
        
        # Initialize video processor
        with VideoProcessor(video_path) as video_processor:
            
            # Initialize slide detector
            slide_detector = SlideDetector(
                text_similarity_threshold=text_similarity_threshold,
                min_slide_duration=min_slide_duration,
                ocr_confidence_threshold=ocr_confidence_threshold,
                incremental_merge=incremental_merge,
                remove_duplicates=remove_duplicates
            )
            
            # Detect slides
            print(f"\n🔍 Detecting slides...")
            detected_slides = slide_detector.detect_slides(
                video_processor,
                sample_rate=sample_rate,
                progress_callback=progress_callback
            )
            
            # Finalize slide metadata
            detected_slides = slide_detector.finalize_slides(detected_slides)
            
            # Save slide images
            print(f"\n💾 Saving slide images...")
            slides_metadata = []
            
            for idx, slide in enumerate(detected_slides, start=1):
                # Save image
                image_filename = save_slide_image(
                    slide["frame"],
                    output_dir,
                    idx,
                    image_format=image_format,
                    quality=image_quality
                )
                
                # Build metadata (without frame data)
                slide_meta = {
                    "imageFile": image_filename,
                    "startTime": slide["start_time"],
                    "endTime": slide["end_time"],
                    "startTimeMs": int(slide["start_time_ms"]),
                    "endTimeMs": int(slide["end_time_ms"]),
                    "duration": round(slide["duration"], 2)
                }
                
                # Optionally include extracted text
                if include_text_in_json:
                    slide_meta["extractedText"] = slide["extracted_text"]
                    slide_meta["ocrConfidence"] = slide["ocr_confidence"]
                
                slides_metadata.append(slide_meta)
                
                print(f"   ✓ Slide {idx:03d}: {slide['start_time']} - {slide['end_time']} "
                      f"({slide['duration']:.1f}s)")
            
            # Save metadata JSON
            print(f"\n📄 Saving metadata...")
            metadata_file = save_metadata_json(
                slides_metadata,
                output_dir,
                video_info['filename'],
                processing_time=time.time() - start_time
            )
            
            print(f"   ✓ Metadata: {metadata_file}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        print(f"\n{'=' * 70}")
        print(f"✅ SUCCESS!")
        print(f"{'=' * 70}")
        print(f"📊 Slides extracted: {len(slides_metadata)}")
        print(f"⏱️  Processing time: {processing_time:.1f}s")
        print(f"📁 Output directory: {output_dir}")
        print(f"{'=' * 70}\n")
        
        return {
            "status": "success",
            "slides_count": len(slides_metadata),
            "output_dir": output_dir,
            "metadata_file": metadata_file,
            "slides": slides_metadata,
            "processing_time": round(processing_time, 2),
            "video_info": video_info
        }
    
    except Exception as e:
        print(f"\n{'=' * 70}")
        print(f"❌ ERROR: {str(e)}")
        print(f"{'=' * 70}\n")
        
        return {
            "status": "error",
            "error": str(e),
            "slides_count": 0,
            "processing_time": round(time.time() - start_time, 2)
        }
