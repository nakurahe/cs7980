"""File management utilities"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
import cv2


def ensure_output_directory(output_dir: str) -> None:
    """
    Create output directory if it doesn't exist
    
    Args:
        output_dir: Path to output directory
    """
    os.makedirs(output_dir, exist_ok=True)


def save_slide_image(
    frame, 
    output_dir: str, 
    slide_number: int, 
    image_format: str = "jpg",
    quality: int = 85
) -> str:
    """
    Save slide image to file
    
    Args:
        frame: Frame to save (numpy array)
        output_dir: Output directory path
        slide_number: Slide number for filename
        image_format: Image format (jpg, png, webp)
        quality: JPEG/WebP quality (1-100)
        
    Returns:
        Filename of saved image
    """
    ensure_output_directory(output_dir)
    
    # Generate filename
    filename = f"slide_{slide_number:03d}.{image_format}"
    filepath = os.path.join(output_dir, filename)
    
    # Save image with appropriate settings
    if image_format.lower() in ["jpg", "jpeg"]:
        cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    elif image_format.lower() == "png":
        cv2.imwrite(filepath, frame, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    elif image_format.lower() == "webp":
        cv2.imwrite(filepath, frame, [cv2.IMWRITE_WEBP_QUALITY, quality])
    else:
        cv2.imwrite(filepath, frame)
    
    return filename


def save_metadata_json(
    slides_data: List[Dict[str, Any]], 
    output_dir: str, 
    video_filename: str,
    processing_time: float
) -> str:
    """
    Save slide metadata to JSON file
    
    Args:
        slides_data: List of slide metadata dictionaries
        output_dir: Output directory path
        video_filename: Original video filename
        processing_time: Total processing time in seconds
        
    Returns:
        Path to saved JSON file
    """
    ensure_output_directory(output_dir)
    
    # Create metadata structure
    metadata = {
        "videoFile": video_filename,
        "totalSlides": len(slides_data),
        "processingTime": round(processing_time, 2),
        "extractionDate": datetime.now().isoformat(),
        "slides": slides_data
    }
    
    # Save to JSON file
    json_path = os.path.join(output_dir, "slides_metadata.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return json_path


def get_video_info(video_path: str) -> Dict[str, Any]:
    """
    Get basic information about video file
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with video information
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    
    info = {
        "filename": os.path.basename(video_path),
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "duration_seconds": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    }
    
    cap.release()
    
    return info
