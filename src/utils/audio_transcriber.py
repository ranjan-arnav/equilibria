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
        # Using turbo model for faster transcription
        self.model = "whisper-large-v3-turbo"
        self.client = None
        
        if self.api_key and GROQ_AVAILABLE:
            self.client = Groq(api_key=self.api_key)
            
    def transcribe(self, audio_file: BinaryIO) -> Optional[str]:
        """Transcribe audio file object to text."""
        if not self.client:
            print("ERROR: Groq client not initialized. Check API key.")
            return None
            
        try:
            # Ensure we're at start of file
            audio_file.seek(0)
            
            # Read audio data
            audio_data = audio_file.read()
            print(f"Transcribing audio: {len(audio_data)} bytes")
            
            # Groq expects (filename, file_content) tuple
            # Streamlit records in webm/opus format, but Groq accepts various formats
            # Try with .webm extension first, then .wav as fallback
            try:
                print("Trying .webm format...")
                transcription = self.client.audio.transcriptions.create(
                    file=("audio.webm", audio_data),
                    model=self.model,
                    response_format="text"
                )
            except Exception as e1:
                print(f"WebM failed: {e1}")
                # Fallback: try with .wav extension
                try:
                    print("Trying .wav format...")
                    transcription = self.client.audio.transcriptions.create(
                        file=("audio.wav", audio_data),
                        model=self.model,
                        response_format="text"
                    )
                except Exception as e2:
                    print(f"WAV failed: {e2}")
                    print(f"Both formats failed. webm error: {e1}, wav error: {e2}")
                    return None
            
            # Handle response - it might be a string or object
            if isinstance(transcription, str):
                result = transcription.strip() if transcription else None
            elif hasattr(transcription, 'text'):
                result = transcription.text.strip() if transcription.text else None
            else:
                result = str(transcription).strip() if transcription else None
            
            print(f"Transcription result: {result[:100] if result else 'EMPTY'}")
            return result
                
        except Exception as e:
            print(f"Transcription error: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return None
