---
name: pc_control
description: PC automation and control using PyAutoGUI and PyGetWindow for mouse, keyboard, and window management.
homepage: https://pyautogui.readthedocs.io/
metadata: {"synapseos":{"emoji":"🖥️","requires":{"packages":["pyautogui","pygetwindow","pillow"]},"install":[{"id":"pip","kind":"pip","packages":["pyautogui","pygetwindow","pillow"],"label":"Install PC control dependencies"}]}}
---

# PC Control Skill

Provides autonomous PC control capabilities for SynapseOS.

## Features

- Mouse control (move, click, drag)
- Keyboard input simulation
- Window management (focus, resize, close)
- Screenshot capture
- Application launching

## Usage

```python
from skills.pc_control import PCController

controller = PCController()
controller.move_mouse(100, 100)
controller.click()
controller.type_text("Hello World")
```

## Safety Notes

- Use with caution in production environments
- Implement user confirmation for destructive actions
- Respect system permissions and user privacy