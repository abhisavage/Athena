import subprocess
import streamlit as st
from faster_whisper import WhisperModel
import os
import shutil
from pathlib import Path

@st.cache_resource
def load_model():
    return WhisperModel("base", compute_type="float32")

def ensure_static_dir():
    """Ensure static directory exists"""
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    return static_dir

@st.cache_data
def generate_transcript(video_url):
    try:
        st.info("Downloading audio from YouTube using yt-dlp...")
        static_dir = ensure_static_dir()
        temp_audio = static_dir / "temp_audio"
        final_audio = static_dir / "audio.mp4"

        # Clean up previous audio files
        if temp_audio.exists():
            temp_audio.unlink()
        if final_audio.exists():
            final_audio.unlink()

        # Download audio using yt-dlp
        subprocess.run(
            ["yt-dlp", "-f", "bestaudio", "-o", str(temp_audio) + ".%(ext)s", video_url],
            check=True
        )

        # Find the downloaded file and rename it
        for ext in ['.webm', '.m4a', '.mp3']:
            temp_file = temp_audio.with_suffix(ext)
            if temp_file.exists():
                shutil.move(str(temp_file), str(final_audio))
                break

        if not final_audio.exists():
            raise FileNotFoundError("Failed to download audio file")

        # Generate transcript
        model = load_model()
        segments, _ = model.transcribe(str(final_audio))
        full_text = " ".join([segment.text for segment in segments])

        return {"text": full_text, "audio_path": str(final_audio)}

    except subprocess.CalledProcessError as e:
        st.error(f"Failed to download audio: {e}")
        return {"text": "", "audio_path": ""}
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return {"text": "", "audio_path": ""}
    finally:
        # Clean up temporary files
        for ext in ['.webm', '.m4a', '.mp3']:
            temp_file = temp_audio.with_suffix(ext)
            if temp_file.exists():
                temp_file.unlink()
