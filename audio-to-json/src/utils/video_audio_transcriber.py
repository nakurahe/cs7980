from faster_whisper import WhisperModel
import os
import json

# 🔧 Change this constant to the input video file you want to process
INPUT_FILE = "test_video.mp4"


def main():
    input_file = INPUT_FILE

    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return

    # Step 1: Auto-generate output filename
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    json_output = f"{base_name}_segments.json"

    # Step 2: Transcribe directly from video with faster-whisper
    model = WhisperModel("base", device="auto", compute_type="auto")
    segments, info = model.transcribe(input_file, beam_size=5)

    # Step 3: Extract timestamped segments
    segments_data = [
        {
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        }
        for segment in segments
    ]

    # Step 4: Save transcription data to JSON
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(segments_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Transcription saved to: {json_output}")


if __name__ == "__main__":
    main()
