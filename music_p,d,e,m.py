import librosa
import numpy as np
import whisper

# =========================
# LOAD SONG
# =========================
def load_song(file):
    audio, sr = librosa.load(file, sr=None)
    return audio, sr

# =========================
# TRANSCRIBE SONG (LYRICS)
# =========================
def get_lyrics(song_file):
    model = whisper.load_model("base")  # you can use "small", "medium", "large"
    result = model.transcribe(song_file)
    return result["segments"]

# =========================
# EMOTION DETECTION
# =========================
def detect_emotion(avg_pitch, loudness, pitch_var):
    if avg_pitch > 250 and loudness > 0.02:
        return "Energetic / Excited"
    elif avg_pitch < 150 and loudness < 0.01:
        return "Sad / Calm"
    elif pitch_var > 40:
        return "Emotional / Expressive"
    else:
        return "Neutral / Balanced"

# =========================
# MODULATION INTERPRETATION
# =========================
def interpret_modulation(pitch_trend, pitch_var):
    if abs(pitch_trend) < 5:
        return "Stable tone"
    elif pitch_trend > 15:
        return "Rising modulation"
    elif pitch_trend < -15:
        return "Falling modulation"
    elif pitch_var > 50:
        return "Strong expressive modulation"
    else:
        return "Smooth vocal glide"

# =========================
# ANALYZE SONG LINE BY LINE
# =========================
def analyze_song_with_lyrics(song_file):
    audio, sr = load_song(song_file)
    lyrics_segments = get_lyrics(song_file)

    print("\n🎶 AI LYRIC-BY-LYRIC VOCAL ANALYSIS\n")

    for seg in lyrics_segments:
        start = seg["start"]
        end = seg["end"]
        text = seg["text"].strip()

        start_sample = int(start * sr)
        end_sample = int(end * sr)
        segment = audio[start_sample:end_sample]

        if len(segment) == 0:
            continue

        pitches = librosa.yin(segment, fmin=50, fmax=500)
        pitches = pitches[pitches > 0]

        if len(pitches) == 0:
            continue

        avg_pitch = np.mean(pitches)
        pitch_var = np.std(pitches)

        rms = librosa.feature.rms(y=segment)[0]
        loudness = np.mean(rms)

        pitch_trend = pitches[-1] - pitches[0]

        emotion = detect_emotion(avg_pitch, loudness, pitch_var)
        modulation = interpret_modulation(pitch_trend, pitch_var)

        if avg_pitch < 150:
            pitch_desc = "Low pitch"
        elif avg_pitch < 250:
            pitch_desc = "Medium pitch"
        else:
            pitch_desc = "High pitch"

        if loudness < 0.01:
            dyn_desc = "Soft dynamics"
        elif loudness < 0.02:
            dyn_desc = "Moderate dynamics"
        else:
            dyn_desc = "Strong dynamics"

        print(f"🎤 Lyric: {text}")
        print(f"  → Pitch: {pitch_desc} ({avg_pitch:.1f} Hz)")
        print(f"  → Dynamics: {dyn_desc}")
        print(f"  → Modulation: {modulation}")
        print(f"  → Emotion: {emotion}")
        print("-" * 60)

# =========================
# RUN PROGRAM
# =========================
if __name__ == "__main__":
    song = input("Enter song file path: ").strip()
    song = song.replace("\\", "/")

    analyze_song_with_lyrics(song)