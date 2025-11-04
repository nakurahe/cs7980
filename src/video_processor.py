"""Video processing module for frame extraction"""

import cv2
from typing import Generator, Tuple
import numpy as np


class VideoProcessor:
    """Handles video file operations and frame extraction"""
    
    def __init__(self, video_path: str):
        """
        Initialize video processor
        
        Args:
            video_path: Path to video file
        """
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    def get_info(self) -> dict:
        """
        Get video information
        
        Returns:
            Dictionary with video metadata
        """
        return {
            "fps": self.fps,
            "total_frames": self.total_frames,
            "duration": self.duration,
            "width": self.width,
            "height": self.height
        }
    
    def extract_frames(
        self, 
        sample_rate: float = 1.0
    ) -> Generator[Tuple[np.ndarray, float], None, None]:
        """
        Extract frames from video at specified sample rate
        
        Args:
            sample_rate: Frames per second to extract
            
        Yields:
            Tuple of (frame, timestamp_ms)
        """
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        # Calculate frame interval
        frame_interval = int(self.fps / sample_rate) if sample_rate < self.fps else 1
        
        frame_count = 0
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                break
            
            # Only yield frames at the specified interval
            if frame_count % frame_interval == 0:
                timestamp_ms = (frame_count / self.fps) * 1000
                yield frame, timestamp_ms
            
            frame_count += 1
    
    def get_frame_at_time(self, timestamp_ms: float) -> np.ndarray:
        """
        Get frame at specific timestamp
        
        Args:
            timestamp_ms: Timestamp in milliseconds
            
        Returns:
            Frame at specified timestamp
        """
        self.cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
        ret, frame = self.cap.read()
        
        if not ret:
            raise ValueError(f"Could not read frame at timestamp {timestamp_ms}ms")
        
        return frame
    
    def release(self):
        """Release video capture resources"""
        if self.cap is not None:
            self.cap.release()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.release()
