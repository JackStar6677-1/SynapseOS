---
name: tts_speech
description: Text-to-speech synthesis using Microsoft Azure Cognitive Services or pyttsx3
homepage: https://speech.microsoft.com/
metadata: {"synapseos":{"emoji":"🔊","requires":{"packages":["pyttsx3","azure-cognitiveservices-speech"]},"install":[{"id":"pip","kind":"pip","packages":["pyttsx3"],"label":"Install basic TTS (pyttsx3)"},{"id":"pip","kind":"pip","packages":["azure-cognitiveservices-speech"],"label":"Install Azure TTS (optional)"}]}}
---

# Text-to-Speech Skill

Provides voice synthesis capabilities for SynapseOS.

## Features

- Multiple TTS engines (pyttsx3, Azure Cognitive Services)
- Voice selection and customization
- Speech rate and volume control
- Async speech synthesis

## Usage

```python
from skills.tts_speech import TextToSpeech

tts = TextToSpeech()
await tts.speak("Hello, I am SynapseOS")
```

## Configuration

Configure voice settings in config/settings.py:
- engine: 'pyttsx3' or 'azure'
- voice: voice name or ID
- rate: speech rate
- volume: speech volume