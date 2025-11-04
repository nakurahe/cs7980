"""Slide detection logic"""

from typing import List, Dict, Any, Optional
import numpy as np
from .video_processor import VideoProcessor
from .ocr_engine import OCREngine
from .text_comparator import TextComparator
from .utils.image_utils import preprocess_image, compute_image_hash
from .utils.time_utils import ms_to_timestamp


class SlideDetector:
    """Detects slide changes in educational videos"""
    
    def __init__(
        self,
        text_similarity_threshold: float = 0.75,
        min_slide_duration: float = 3.0,
        ocr_confidence_threshold: float = 0.70,
        incremental_merge: bool = True
    ):
        """
        Initialize slide detector
        
        Args:
            text_similarity_threshold: Threshold for considering slides different (0-1)
            min_slide_duration: Minimum duration for a slide in seconds
            ocr_confidence_threshold: Minimum OCR confidence to accept (0-1)
            incremental_merge: Whether to merge incremental slides
        """
        self.text_similarity_threshold = text_similarity_threshold
        self.min_slide_duration = min_slide_duration
        self.ocr_confidence_threshold = ocr_confidence_threshold
        self.incremental_merge = incremental_merge
        
        self.ocr_engine = OCREngine()
        self.text_comparator = TextComparator()
    
    def detect_slides(
        self,
        video_processor: VideoProcessor,
        sample_rate: float = 1.0,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect all slides in video
        
        Args:
            video_processor: VideoProcessor instance
            sample_rate: Frames per second to sample
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of detected slides with metadata
        """
        slides = []
        current_slide = None
        previous_text = ""
        previous_hash = None
        frame_count = 0
        total_frames = int(video_processor.duration * sample_rate)
        
        print(f"\n🎬 Processing video: {video_processor.duration:.1f}s @ {sample_rate} FPS")
        print(f"📊 Estimated frames to process: {total_frames}")
        print(f"⚙️  Settings: text_threshold={self.text_similarity_threshold}, "
              f"min_duration={self.min_slide_duration}s\n")
        
        for frame, timestamp_ms in video_processor.extract_frames(sample_rate):
            frame_count += 1
            
            # Progress update
            if frame_count % 10 == 0 or frame_count == 1:
                progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
                print(f"⏳ Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)", 
                      end='\r')
                
                if progress_callback:
                    progress_callback({
                        "frame_count": frame_count,
                        "total_frames": total_frames,
                        "progress": progress,
                        "slides_found": len(slides)
                    })
            
            # Quick pre-filter using perceptual hash
            current_hash = compute_image_hash(frame)
            
            if previous_hash and current_hash == previous_hash:
                # Identical frame, skip OCR
                if current_slide:
                    current_slide["end_time_ms"] = timestamp_ms
                continue
            
            previous_hash = current_hash
            
            # Preprocess frame for better OCR
            processed_frame = preprocess_image(frame)
            
            # Extract text with confidence
            ocr_result = self.ocr_engine.extract_text_with_confidence(processed_frame)
            current_text = self.ocr_engine.clean_text(ocr_result["text"])
            confidence = ocr_result["confidence"]
            
            # Skip frames with low OCR confidence or no text
            if confidence < self.ocr_confidence_threshold or not current_text:
                if current_slide:
                    current_slide["end_time_ms"] = timestamp_ms
                continue
            
            # Check if this is a new slide
            if not previous_text:
                # First slide
                current_slide = self._create_slide_entry(
                    frame, timestamp_ms, current_text, confidence
                )
                previous_text = current_text
            else:
                # Compare with previous slide
                similarity = self.text_comparator.calculate_similarity(
                    previous_text, current_text
                )
                
                # Check if it's an incremental slide
                is_incremental = False
                if self.incremental_merge:
                    is_incremental = self.text_comparator.is_incremental_slide(
                        previous_text, current_text
                    )
                
                if similarity < self.text_similarity_threshold and not is_incremental:
                    # New slide detected
                    if current_slide:
                        # Finalize previous slide
                        current_slide["end_time_ms"] = timestamp_ms
                        
                        # Check minimum duration
                        duration = (current_slide["end_time_ms"] - 
                                   current_slide["start_time_ms"]) / 1000
                        
                        if duration >= self.min_slide_duration:
                            slides.append(current_slide)
                    
                    # Start new slide
                    current_slide = self._create_slide_entry(
                        frame, timestamp_ms, current_text, confidence
                    )
                    previous_text = current_text
                else:
                    # Same slide or incremental, update end time
                    if current_slide:
                        current_slide["end_time_ms"] = timestamp_ms
                        
                        # For incremental slides, update with more complete text
                        if is_incremental and len(current_text) > len(previous_text):
                            current_slide["extracted_text"] = current_text
                            current_slide["frame"] = frame
                            previous_text = current_text
        
        # Add final slide
        if current_slide:
            duration = (current_slide["end_time_ms"] - 
                       current_slide["start_time_ms"]) / 1000
            
            if duration >= self.min_slide_duration:
                slides.append(current_slide)
        
        print(f"\n\n✅ Processing complete! Found {len(slides)} slides")
        
        return slides
    
    def _create_slide_entry(
        self, 
        frame: np.ndarray, 
        timestamp_ms: float, 
        text: str, 
        confidence: float
    ) -> Dict[str, Any]:
        """
        Create a slide entry dictionary
        
        Args:
            frame: Video frame
            timestamp_ms: Timestamp in milliseconds
            text: Extracted text
            confidence: OCR confidence
            
        Returns:
            Slide entry dictionary
        """
        return {
            "frame": frame.copy(),  # Store frame for saving later
            "start_time_ms": timestamp_ms,
            "end_time_ms": timestamp_ms,
            "start_time": ms_to_timestamp(timestamp_ms),
            "end_time": ms_to_timestamp(timestamp_ms),
            "extracted_text": text,
            "ocr_confidence": round(confidence, 2)
        }
    
    def finalize_slides(self, slides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Finalize slide metadata (update end times, durations, etc.)
        
        Args:
            slides: List of detected slides
            
        Returns:
            Finalized list of slides
        """
        for slide in slides:
            # Update end time string
            slide["end_time"] = ms_to_timestamp(slide["end_time_ms"])
            
            # Calculate duration
            duration_ms = slide["end_time_ms"] - slide["start_time_ms"]
            slide["duration"] = duration_ms / 1000
        
        return slides
