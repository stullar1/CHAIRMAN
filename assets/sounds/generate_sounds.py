"""
Generate simple UI sound effects using wave module.
Run this script once to create the sound files.
"""
import wave
import struct
import math
import os

def generate_tone(filename, frequency, duration, volume=0.3, fade=True):
    """Generate a simple tone sound."""
    sample_rate = 44100
    num_samples = int(sample_rate * duration)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = i / sample_rate
            # Basic sine wave
            value = math.sin(2 * math.pi * frequency * t)

            # Apply fade in/out
            if fade:
                fade_samples = int(num_samples * 0.1)
                if i < fade_samples:
                    value *= i / fade_samples
                elif i > num_samples - fade_samples:
                    value *= (num_samples - i) / fade_samples

            # Apply volume and convert to 16-bit
            sample = int(value * volume * 32767)
            wav_file.writeframes(struct.pack('h', sample))

def generate_click(filename):
    """Generate a short click sound."""
    sample_rate = 44100
    duration = 0.05
    num_samples = int(sample_rate * duration)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = i / sample_rate
            # Quick decay
            decay = math.exp(-t * 50)
            # Mix of frequencies for click
            value = (math.sin(2 * math.pi * 1000 * t) +
                    math.sin(2 * math.pi * 2000 * t) * 0.5) * decay
            sample = int(value * 0.2 * 32767)
            wav_file.writeframes(struct.pack('h', sample))

def generate_hover(filename):
    """Generate a soft hover sound."""
    sample_rate = 44100
    duration = 0.03
    num_samples = int(sample_rate * duration)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = i / sample_rate
            decay = math.exp(-t * 80)
            value = math.sin(2 * math.pi * 800 * t) * decay
            sample = int(value * 0.1 * 32767)
            wav_file.writeframes(struct.pack('h', sample))

def generate_success(filename):
    """Generate a pleasant success sound (ascending)."""
    sample_rate = 44100
    duration = 0.3
    num_samples = int(sample_rate * duration)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = i / sample_rate
            # Two-tone ascending
            if t < 0.15:
                freq = 523  # C5
            else:
                freq = 659  # E5

            decay = math.exp(-t * 5)
            value = math.sin(2 * math.pi * freq * t) * decay
            sample = int(value * 0.25 * 32767)
            wav_file.writeframes(struct.pack('h', sample))

def generate_error(filename):
    """Generate an error sound (descending)."""
    sample_rate = 44100
    duration = 0.25
    num_samples = int(sample_rate * duration)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = i / sample_rate
            # Descending tone
            freq = 400 - t * 200
            decay = math.exp(-t * 8)
            value = math.sin(2 * math.pi * freq * t) * decay
            sample = int(value * 0.25 * 32767)
            wav_file.writeframes(struct.pack('h', sample))

def generate_warning(filename):
    """Generate a warning beep."""
    sample_rate = 44100
    duration = 0.2
    num_samples = int(sample_rate * duration)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = i / sample_rate
            # Pulsing warning
            pulse = 1 if (int(t * 20) % 2 == 0) else 0.5
            decay = math.exp(-t * 5)
            value = math.sin(2 * math.pi * 440 * t) * decay * pulse
            sample = int(value * 0.2 * 32767)
            wav_file.writeframes(struct.pack('h', sample))

def generate_popup(filename):
    """Generate a soft popup sound."""
    sample_rate = 44100
    duration = 0.15
    num_samples = int(sample_rate * duration)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = i / sample_rate
            # Soft ascending pop
            freq = 600 + t * 400
            decay = math.exp(-t * 15)
            value = math.sin(2 * math.pi * freq * t) * decay
            sample = int(value * 0.15 * 32767)
            wav_file.writeframes(struct.pack('h', sample))

def generate_notification(filename):
    """Generate a notification chime."""
    sample_rate = 44100
    duration = 0.4
    num_samples = int(sample_rate * duration)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = i / sample_rate
            # Three-note chime
            if t < 0.13:
                freq = 523  # C5
            elif t < 0.26:
                freq = 659  # E5
            else:
                freq = 784  # G5

            decay = math.exp(-((t % 0.13) * 10))
            value = math.sin(2 * math.pi * freq * t) * decay
            sample = int(value * 0.2 * 32767)
            wav_file.writeframes(struct.pack('h', sample))

def generate_toggle(filename):
    """Generate a toggle switch sound."""
    sample_rate = 44100
    duration = 0.08
    num_samples = int(sample_rate * duration)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = i / sample_rate
            decay = math.exp(-t * 40)
            value = math.sin(2 * math.pi * 1200 * t) * decay
            sample = int(value * 0.15 * 32767)
            wav_file.writeframes(struct.pack('h', sample))

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("Generating UI sounds...")

    generate_click(os.path.join(script_dir, "click.wav"))
    print("  - click.wav")

    generate_hover(os.path.join(script_dir, "hover.wav"))
    print("  - hover.wav")

    generate_success(os.path.join(script_dir, "success.wav"))
    print("  - success.wav")

    generate_error(os.path.join(script_dir, "error.wav"))
    print("  - error.wav")

    generate_warning(os.path.join(script_dir, "warning.wav"))
    print("  - warning.wav")

    generate_popup(os.path.join(script_dir, "popup.wav"))
    print("  - popup.wav")

    generate_notification(os.path.join(script_dir, "notification.wav"))
    print("  - notification.wav")

    generate_toggle(os.path.join(script_dir, "toggle.wav"))
    print("  - toggle.wav")

    print("\nDone! All sounds generated.")
