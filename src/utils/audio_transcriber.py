"""
Audio transcription utility using Groq API.
"""
import os
from typing import Optional, BinaryIO

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class AudioTranscriber:
    """Wrapper for Groq transcription API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = "distil-whisper-large-v3-en"
        self.client = None
        
        if self.api_key and GROQ_AVAILABLE:
            self.client = Groq(api_key=self.api_key)
            
    def transcribe(self, audio_file: BinaryIO) -> Optional[str]:
        """Transcribe audio file object to text."""
        if not self.client:
            return None
            
        try:
            # Ensure we're at start of file
            audio_file.seek(0)
            
            # Groq expects (filename, file_content) tuple or file path
            # For BytesIO from Streamlit, we need to pass the content
            transcription = self.client.audio.transcriptions.create(
                file=("input.wav", audio_file.read()),
                model=self.model,
                response_format="text"
            )
            return transcription
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
