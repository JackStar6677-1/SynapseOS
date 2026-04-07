"""
PC Control Skill for SynapseOS
Provides autonomous PC automation capabilities
"""

import pyautogui
import pygetwindow as gw
from PIL import Image
import time
import logging

logger = logging.getLogger(__name__)

class PCController:
    """PC automation controller using PyAutoGUI and PyGetWindow"""

    def __init__(self, safety_delay=0.5):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = safety_delay
        self.safety_delay = safety_delay

    def move_mouse(self, x: int, y: int, duration: float = 0.5):
        """Move mouse to coordinates"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"Moved mouse to ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")
            return False

    def click(self, button: str = 'left', clicks: int = 1):
        """Click mouse button"""
        try:
            pyautogui.click(button=button, clicks=clicks)
            logger.info(f"Clicked {button} button {clicks} time(s)")
            return True
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            return False

    def type_text(self, text: str, interval: float = 0.02):
        """Type text with keyboard"""
        try:
            pyautogui.typewrite(text, interval=interval)
            logger.info(f"Typed text: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False

    def press_key(self, key: str):
        """Press a single key"""
        try:
            pyautogui.press(key)
            logger.info(f"Pressed key: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            return False

    def screenshot(self, region=None) -> Image.Image:
        """Take screenshot of screen or region"""
        try:
            screenshot = pyautogui.screenshot(region=region)
            logger.info("Screenshot taken")
            return screenshot
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None

    def get_window(self, title: str):
        """Get window by title"""
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                return windows[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get window: {e}")
            return None

    def focus_window(self, title: str):
        """Focus window by title"""
        try:
            window = self.get_window(title)
            if window:
                window.activate()
                logger.info(f"Focused window: {title}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to focus window: {e}")
            return False

    def get_screen_size(self):
        """Get screen dimensions"""
        return pyautogui.size()

    def wait(self, seconds: float):
        """Wait for specified seconds"""
        time.sleep(seconds)