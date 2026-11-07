
import wave
import math
from array import array
from pathlib import Path


# ==================================================
# 1. FOLDER SETTINGS
# ==================================================

SPEECH_DIR = Path("data/processed")
NOISE_DIR = Path("data/processed/ambient")
OUTPUT_DIR = Path("data/noisy")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SNR_LEVELS = [20, 10, 0]

# Only Shakun (_02) and Ram (_03)
SPEAKER_SUFFIXES = ("_02", "_03")


# ==================================================
# 2. READ WAV AUDIO
# ==================================================

def read_audio(path):

    with wave.open(str(path), "rb") as audio:

        if audio.getnchannels() != 1 or audio.getsampwidth() != 2:
            raise ValueError(
                f"{path} must be mono 16-bit WAV"
            )

        rate = audio.getframerate()

        samples = array(
            "h",
            audio.readframes(audio.getnframes())
        )

        if not samples:
            raise ValueError(f"Empty audio file: {path}")

        return [x / 32768.0 for x in samples], rate


# ==================================================
# 3. SAVE WAV AUDIO
# ==================================================

def save_audio(path, samples, rate):

    output = array("h")

    for sample in samples:

        sample = max(-1.0, min(1.0, sample))

        output.append(int(sample * 32767))

    with wave.open(str(path), "wb") as audio:

        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)

        audio.writeframes(output.tobytes())


# ==================================================
# 4. CALCULATE RMS
# ==================================================

def rms(samples):

    if not samples:
        raise ValueError("Audio contains no samples")

    return math.sqrt(
        sum(x * x for x in samples) / len(samples)
    )


# ==================================================
# 5. MIX SPEECH WITH BACKGROUND NOISE
# ==================================================

def mix_audio(speech, noise, snr_db):

    if not speech or not noise:
        raise ValueError("Speech or noise audio is empty")

    # Repeat noise until it matches speech duration
    noise = [
        noise[i % len(noise)]
        for i in range(len(speech))
    ]

    speech_rms = rms(speech)
    noise_rms = rms(noise)

    if speech_rms == 0 or noise_rms == 0:
        raise ValueError("Speech or noise audio is silent")

    # Calculate required noise volume
    target_noise_rms = (
        speech_rms / (10 ** (snr_db / 20))
    )

    factor = target_noise_rms / noise_rms

    mixed = [
        speech[i] + noise[i] * factor
        for i in range(len(speech))
    ]

    # Prevent clipping while preserving the SNR ratio
    peak = max(abs(x) for x in mixed)

    if peak > 0.99:

        scale = 0.99 / peak

        mixed = [
            x * scale
            for x in mixed
        ]

    return mixed


# ==================================================
# 6. FIND ONLY SHAKUN AND RAM RECORDINGS
# ==================================================

speech_files = sorted([
    path
    for path in SPEECH_DIR.glob("*.wav")
    if path.stem.endswith(SPEAKER_SUFFIXES)
])

noise_files = sorted(NOISE_DIR.glob("*.wav"))

if not speech_files:
    raise RuntimeError(
        "No Shakun or Ram speech recordings found!"
    )

if not noise_files:
    raise RuntimeError(
        "No ambient noise files found!"
    )

print("\n========== BHARATVOICE BENCH ==========")
print("       MULTI-SPEAKER NOISE MIXING")
print("=======================================\n")

print("Selected speech recordings:")

for path in speech_files:
    print("-", path.name)

print("\nAvailable noise recordings:")

for path in noise_files:
    print("-", path.name)


# ==================================================
# 7. GENERATE NOISY RECORDINGS
# ==================================================

count = 0

for speech_file in speech_files:

    speech, speech_rate = read_audio(speech_file)

    print(f"\nProcessing: {speech_file.name}")

    for noise_file in noise_files:

        noise, noise_rate = read_audio(noise_file)

        if speech_rate != noise_rate:

            print(
                f"Skipping {noise_file.name}: "
                "sample rate mismatch"
            )

            continue

        for snr in SNR_LEVELS:

            noisy = mix_audio(
                speech,
                noise,
                snr
            )

            filename = (
                f"{speech_file.stem}_"
                f"{noise_file.stem}_"
                f"{snr}dB.wav"
            )

            output_path = OUTPUT_DIR / filename

            save_audio(
                output_path,
                noisy,
                speech_rate
            )

            count += 1

            print(f"Created: {filename}")


# ==================================================
# 8. FINAL SUMMARY
# ==================================================

expected = (
    len(speech_files)
    * len(noise_files)
    * len(SNR_LEVELS)
)

print("\n=======================================")
print("NOISE MIXING COMPLETED!")
print("Speech recordings:", len(speech_files))
print("Noise recordings:", len(noise_files))
print("SNR levels:", SNR_LEVELS)
print("Expected files:", expected)
print("Created files:", count)
print("Output folder:", OUTPUT_DIR)
print("=======================================")

if count != expected:

    print("WARNING: Some files were skipped.")

else:

    print("SUCCESS: All expected files were created!")
