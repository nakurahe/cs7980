import subprocess
import whisper
import os
import json

# 🔧 Change this constant to the input video file you want to process
INPUT_FILE = "input_video.mp4"


def main():
    input_file = INPUT_FILE

    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return

    # Step 1: Auto-generate related filenames
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    audio_file = f"{base_name}_audio.mp3"
    json_output = f"{base_name}_segments.json"

    # Step 2: Convert MP4 → MP3 using ffmpeg
    subprocess.run([
        "ffmpeg",
        "-i", input_file,
        "-q:a", "0",
        "-map", "a",
        audio_file,
        "-y"
    ], check=True)

    # Step 3: Transcribe with Whisper
    model = whisper.load_model("turbo")
    result = model.transcribe(audio_file, verbose=False)

    # Step 4: Extract timestamped segments
    segments_data = [
        {
            "start": round(segment["start"], 2),
            "end": round(segment["end"], 2),
            "text": segment["text"].strip()
        }
        for segment in result["segments"]
    ]

    # Step 5: Save transcription data to JSON
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(segments_data, f, ensure_ascii=False, indent=2)

    # Step 6: Delete original video and temporary audio
    for f in [input_file, audio_file]:
        try:
            os.remove(f)
            print(f"🗑️ Deleted file: {f}")
        except OSError as e:
            print(f"⚠️ Could not delete {f}: {e}")


if __name__ == "__main__":
    main()
