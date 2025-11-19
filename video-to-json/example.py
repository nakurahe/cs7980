"""
Example usage of the slide extraction module

This script demonstrates how to use the extract_slides function
to process an educational video and extract slides.
"""

import sys
import os

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src import extract_slides


def main():
    """Main example function"""
    
    # Configuration
    VIDEO_PATH = "test_video.mp4"  # Update this path
    OUTPUT_DIR = "./output"
    
    # Check if video exists
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Error: Video file not found: {VIDEO_PATH}")
        print(f"\n💡 Please update VIDEO_PATH in example.py to point to your video file")
        return
    
    print("Starting slide extraction...\n")
    
    # Extract slides with custom settings
    result = extract_slides(
        video_path=VIDEO_PATH,
        output_dir=OUTPUT_DIR,
        
        # Detection settings
        text_similarity_threshold=0.75,  # How different slides must be (0-1)
        min_slide_duration=3.0,          # Minimum seconds per slide
        ocr_confidence_threshold=0.70,   # Minimum OCR quality (0-1)
        
        # Sampling
        sample_rate=1.0,                 # Frames per second to analyze
        
        # Output format
        image_format="jpg",              # jpg, png, or webp
        image_quality=85,                # Quality for jpg/webp (1-100)
        include_text_in_json=True,       # Include extracted text in metadata
        
        # Advanced options
        incremental_merge=True,          # Merge incremental slides (bullets appearing)
        remove_duplicates=True,          # Remove consecutive duplicates (keeps revisited slides)
        progress_callback=None           # Optional: function for progress updates
    )
    
    # Check result
    if result["status"] == "success":
        print(f"\n✅ Success!")
        print(f"   Slides extracted: {result['slides_count']}")
        print(f"   Output directory: {result['output_dir']}")
        print(f"   Metadata file: {result['metadata_file']}")
        print(f"   Processing time: {result['processing_time']}s")
        
        # Display first few slides
        print(f"\n📋 First 3 slides:")
        for slide in result['slides'][:3]:
            print(f"\n   🖼️  {slide['imageFile']}")
            print(f"      Time: {slide['startTime']} → {slide['endTime']}")
            print(f"      Duration: {slide['duration']}s")
            if 'extractedText' in slide:
                preview = slide['extractedText'][:100]
                print(f"      Text: {preview}...")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")


def example_with_progress():
    """Example with progress callback"""
    
    VIDEO_PATH = "path/to/your/lecture.mp4"
    OUTPUT_DIR = "./output"
    
    def progress_handler(progress_data):
        """Custom progress handler"""
        print(f"\r⏳ Progress: {progress_data['progress']:.1f}% - "
              f"Slides found: {progress_data['slides_found']}", end='')
    
    result = extract_slides(
        video_path=VIDEO_PATH,
        output_dir=OUTPUT_DIR,
        progress_callback=progress_handler
    )
    
    return result


def example_server_integration():
    """
    Example of how to integrate with a server/API
    
    This shows how you might use this in a Flask/FastAPI endpoint
    """
    
    # Pseudo-code for server integration
    """
    from flask import Flask, request, jsonify
    from src import extract_slides
    
    app = Flask(__name__)
    
    @app.route('/api/extract-slides', methods=['POST'])
    def extract_slides_endpoint():
        # Get uploaded file
        video_file = request.files['video']
        video_path = f"./uploads/{video_file.filename}"
        video_file.save(video_path)
        
        # Process video
        result = extract_slides(
            video_path=video_path,
            output_dir=f"./output/{video_file.filename}",
            progress_callback=lambda p: socketio.emit('progress', p)
        )
        
        # Return result
        return jsonify(result)
    """
    
    pass


if __name__ == "__main__":
    main()
