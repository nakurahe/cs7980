import subprocess
import whisper
import os
import json
import sys


def main():
    # Step 1: Get input file dynamically
    if len(sys.argv) > 1:
        input_file = sys.argv[1]  # allow running via command line: python script.py yourfile.mp4
    else:
        input_file = input("Enter the path to the video file: ").strip()

    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return

    # Step 2: Auto-generate related filenames
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    audio_file = f"{base_name}_audio.mp3"
    json_output = f"{base_name}_segments.json"


    # Step 3: Convert MP4 → MP3 using ffmpeg
    subprocess.run([
        "ffmpeg",
        "-i", input_file,
        "-q:a", "0",
        "-map", "a",
        audio_file,
        "-y"  # overwrite if exists
    ], check=True)

    # Step 4: Transcribe with Whisper
    model = whisper.load_model("turbo")
    result = model.transcribe(audio_file, verbose=False)

    # Step 5: Extract segment data
    segments_data = [
        {
            "start": round(segment["start"], 2),
            "end": round(segment["end"], 2),
            "text": segment["text"].strip()
        }
        for segment in result["segments"]
    ]

    # Step 6: Save to JSON file
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(segments_data, f, ensure_ascii=False, indent=2)


    # Step 7: Delete original video and temporary audio
    for f in [input_file, audio_file]:
        try:
            os.remove(f)
            print(f"🗑️ Deleted file: {f}")
        except OSError as e:
            print(f"⚠️ Could not delete {f}: {e}")



if __name__ == "__main__":
    main()
