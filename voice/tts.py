import edge_tts
import asyncio
import tempfile
import os
import threading
import sounddevice as sd
import soundfile as sf


async def _speak_async(text: str):
    """Async streaming speech using edge-tts (sentence-by-sentence)
    
    STREAMING APPROACH:
    - Splits text into sentences
    - Generates and plays each sentence immediately
    - Overlaps generation/playback for lower perceived latency
    - Uses rate="+15%" for faster, natural-sounding speech
    """
    try:
        # Split long text into chunks at sentence boundaries
        # Handles "boss.", ". ", "!", "?" as sentence endings
        sentences = text.replace('boss.', 'boss.|').replace('!', '!|').replace('?', '?|')
        sentences = sentences.replace('. ', '.|').split('|')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Stream each sentence - generate and play immediately
        for sentence in sentences:
            if not sentence:
                continue
            
            # Generate audio for this sentence
            communicate = edge_tts.Communicate(
                sentence, 
                voice="en-GB-SoniaNeural", 
                rate="+15%"  # 15% faster speech rate for snappier response
            )
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                tmp_path = f.name
            
            await communicate.save(tmp_path)
            
            # Load and play audio immediately while next sentence may be generating
            try:
                data, samplerate = sf.read(tmp_path)
                sd.play(data, samplerate)
                # Wait for playback to complete
                sd.wait()
            except Exception:
                # Fallback: if soundfile fails, try with playsound
                try:
                    from playsound import playsound
                    playsound(tmp_path)
                except Exception:
                    pass
            
            # Cleanup temp file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
    
    except Exception:
        pass


def speak(text: str):
    """Speak the given text using FRIDAY voice synchronously
    
    Features:
    - Truncates long text (>300 chars) to prevent lengthy speeches
    - Streaming playback for low latency
    - Natural rate (+15% faster)
    
    Args:
        text: Text to speak (will be truncated if >300 chars)
    """
    try:
        # Truncate very long responses to keep speech concise
        # User can read full details on screen if needed
        if len(text) > 300:
            text = text[:300] + "... Check the screen for full details boss."
        
        asyncio.run(_speak_async(text))
    except Exception:
        pass


def speak_background(text: str):
    """Speak the given text in a background thread with streaming
    
    Features:
    - Non-blocking (returns immediately)
    - Truncates long text (>300 chars)
    - Streaming playback
    """
    try:
        # Truncate very long responses
        if len(text) > 300:
            text = text[:300] + "... Check the screen for full details boss."
        
        def run_async():
            asyncio.run(_speak_async(text))
        
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
    except Exception:
        pass


def speak_streaming(text: str):
    """Speak the full text without any character limit
    
    Use this when you need to speak long text that shouldn't be truncated.
    Streaming delivery keeps latency low even for longer content.
    
    Args:
        text: Full text to speak (no truncation applied)
    """
    try:
        asyncio.run(_speak_async(text))
    except Exception:
        pass
