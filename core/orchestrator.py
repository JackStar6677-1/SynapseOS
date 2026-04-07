import asyncio
import logging
import os
import subprocess
import webbrowser
from typing import Dict, Optional

from core.ai_providers import AIProviderManager
from core.task_queue import TaskQueue
from core.state_manager import StateManager
from skills.pc_control.pc_control import PCController
from skills.tts_speech.tts_speech import TextToSpeech
from abilities.terminal_control import TerminalControl
from abilities.file_navigator import FileNavigator
from abilities.window_management import WindowManagement
from abilities.input_control import InputControl

logger = logging.getLogger(__name__)


class TaskOrchestrator:
    """Orchestrates task execution for SynapseOS."""

    def __init__(
        self,
        ai_manager: AIProviderManager,
        task_queue: TaskQueue,
        state_manager: Optional[StateManager] = None,
    ):
        self.ai_manager = ai_manager
        self.task_queue = task_queue
        self.state_manager = state_manager
        self.pc = PCController()
        self.tts = TextToSpeech()
        
        # Nuevas habilidades de aislamiento (Phase 1 & 2)
        self.file_nav = FileNavigator()
        self.term_control = TerminalControl()

    async def execute_task(self, task: Dict[str, any]) -> str:
        task_id = task.get("id")
        self.task_queue.increment_attempts(task_id)
        self.task_queue.update_task(task_id, status="in_progress")

        try:
            result = await self._execute(task)
            self.task_queue.mark_task_completed(task_id, result)
            logger.info(f"Task completed: {task_id}")
            return result
        except Exception as e:
            error_message = str(e)
            self.task_queue.mark_task_failed(task_id, error_message)
            logger.error(f"Task {task_id} failed: {error_message}")
            return error_message

    async def _execute(self, task: Dict[str, any]) -> str:
        description = task.get("description", "").strip()
        lowered = description.lower()

        # Prevent work when the host is overloaded
        if self.state_manager and self.state_manager.is_overloaded():
            raise RuntimeError("System overloaded, delaying task execution")

        if "screenshot" in lowered:
            screenshot = self.pc.screenshot()
            if screenshot is None:
                raise RuntimeError("Failed to capture screenshot")
            screenshot_path = os.path.join("generated_images", f"screenshot_{task.get('id')}.png")
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            screenshot.save(screenshot_path)
            return f"Screenshot saved to {screenshot_path}"

        if "run command" in lowered or "ejecuta comando" in lowered or "cmd" in lowered:
            cmd = description.replace("run command", "").replace("ejecuta comando", "").replace("cmd", "").strip()
            if not cmd:
                return "No command provided to execute."
            result = await self.term_control.run_one_off_command(cmd, is_powershell=False)
            return f"Command execution result: {result.get('output', result.get('error'))}"
            
        if "run powershell" in lowered or "powershell" in lowered:
            cmd = description.replace("run powershell", "").replace("powershell", "").strip()
            if not cmd:
                return "No command provided to execute."
            result = await self.term_control.run_one_off_command(cmd, is_powershell=True)
            return f"Powershell execution result: {result.get('output', result.get('error'))}"

        if "list directory" in lowered or "ls" in lowered or "listar archivos" in lowered:
            res = self.file_nav.ls()
            return f"Directory contents: {res.get('items')}"
            
        if "read file" in lowered or "leer archivo" in lowered:
            filename = description.split()[-1] # Simplistic parsing
            res = self.file_nav.read_file(filename)
            return f"File snippet: {res.get('content')}"

        if any(keyword in lowered for keyword in ["open notepad", "open notebook", "notepad"]):
            self._launch_windows_app("notepad.exe")
            await asyncio.sleep(1)
            return "Opened Notepad"

        if any(keyword in lowered for keyword in ["open calculator", "calculator"]):
            self._launch_windows_app("calc.exe")
            await asyncio.sleep(1)
            return "Opened Calculator"

        if "open browser" in lowered or "open chrome" in lowered or "open edge" in lowered:
            if "edge" in lowered:
                webbrowser.get("windows-default").open("https://www.bing.com")
            else:
                webbrowser.open("https://www.google.com")
            return "Opened web browser"

        if "type" in lowered or "write" in lowered or "escribe" in lowered:
            if "notepad" in lowered:
                self._launch_windows_app("notepad.exe")
                await asyncio.sleep(1)
                message = description
                self.pc.type_text(message)
                return "Typed text into Notepad"

        if any(keyword in lowered for keyword in ["speak", "habla", "dilo"]):
            text_to_speak = description
            await self.tts.speak_async(text_to_speak)
            return "Spoken text with TTS"

        if "generate image" in lowered or "imagen" in lowered:
            image_path = await self.ai_manager.generate_image(description)
            if image_path:
                return f"Generated image saved to {image_path}"
            raise RuntimeError("Unable to generate image")

        # Default behavior: use AI to produce an answer or plan
        result = await self.ai_manager.generate_text(description, provider=task.get("provider"))
        if not result:
            raise RuntimeError("AI provider failed to generate text")
        return result

    def _launch_windows_app(self, executable: str):
        try:
            if os.path.exists(executable):
                subprocess.Popen([executable])
            else:
                subprocess.Popen([executable], shell=True)
            logger.info(f"Launched application: {executable}")
        except Exception as e:
            logger.warning(f"Unable to launch {executable}: {e}")
