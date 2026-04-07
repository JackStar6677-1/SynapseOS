# SynapseOS Skills Manifest

Available tools for SynapseOS autonomous AI system:

- **pc_control**: PC automation and control using PyAutoGUI, PyGetWindow
- **screen_capture**: Screen capture and OCR using PIL, PyTesseract
- **web_browsing**: Web automation using Selenium or Playwright
- **file_management**: File operations and management
- **system_info**: System information gathering
- **gemini_integration**: Integration with Google Gemini API
- **oauth_auth**: OAuth authentication for external services
- **memory_system**: Persistent memory management
- **tts_speech**: Text-to-speech synthesis
- **task_scheduler**: Task scheduling and queue management

To use a skill, read its `SKILL.md` in its respective directory under `skills/`.

## Skill Development Guidelines

Each skill should have:
- SKILL.md with description, usage, and metadata
- Implementation in Python modules
- Proper error handling and logging
- Integration with the main SynapseOS core