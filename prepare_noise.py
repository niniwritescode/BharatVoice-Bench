
import subprocess
from pathlib import Path

INPUT_DIR = Path("data/ambient")
OUTPUT_DIR = Path("data/processed/ambient")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for audio_file in INPUT_DIR.glob("*"):
    if not audio_file.is_file():
        continue

    output_file = OUTPUT_DIR / f"{audio_file.stem}.wav"

    command = [
        "ffmpeg",
        "-y",
        "-i", str(audio_file),
        "-t", "60",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(output_file)
    ]

    print(f"\nProcessing: {audio_file.name}")

    try:
        subprocess.run(command, check=True)
        print(f"Saved: {output_file}")
    except subprocess.CalledProcessError:
        print(f"Failed: {audio_file.name}")

print("\nAll noise files processed!")
