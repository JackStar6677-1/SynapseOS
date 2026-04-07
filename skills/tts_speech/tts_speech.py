"""
Text-to-Speech Skill for SynapseOS
Voice synthesis capabilities
"""

import pyttsx3
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TextToSpeech:
    """Text-to-speech synthesis using pyttsx3"""

    def __init__(self, voice: str = None, rate: int = 200, volume: float = 1.0):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)

        if voice:
            self.set_voice(voice)

    def set_voice(self, voice_name: str):
        """Set the voice by name"""
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if voice_name.lower() in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                logger.info(f"Set voice to: {voice.name}")
                return True
        logger.warning(f"Voice '{voice_name}' not found")
        return False

    def get_available_voices(self):
        """Get list of available voices"""
        voices = self.engine.getProperty('voices')
        return [voice.name for voice in voices]

    def speak(self, text: str):
        """Speak text synchronously"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            logger.info(f"Spoke: {text[:50]}...")
        except Exception as e:
            logger.error(f"Failed to speak: {e}")

    async def speak_async(self, text: str):
        """Speak text asynchronously"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.speak, text)

    def save_to_file(self, text: str, filename: str):
        """Save speech to audio file"""
        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            logger.info(f"Saved speech to: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save speech: {e}")
            return False

    def stop(self):
        """Stop current speech"""
        try:
            self.engine.stop()
        except Exception as e:
            logger.error(f"Failed to stop speech: {e}")