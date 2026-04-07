import time
import io
import asyncio
from typing import Dict, Any, Optional

try:
    from pywinauto import ElementNotFoundError
    from pywinauto.application import Application
except ImportError:
    pass

try:
    import pyautogui
except ImportError:
    pass

try:
    from PIL import ImageGrab
except ImportError:
    pass


class InputControl:
    """
    Control de input diseñado para minimizar la interferencia con el usuario humano.
    Priorizamos pywinauto para enviar clicks y eventos de teclado a nivel de sistema UIAutomation,
    sin mover el puntero físico del ratón del usuario cuando es posible.
    """
    
    @staticmethod
    async def click_element(window_title: str, control_property: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hace click en un elemento de una ventana en segundo plano (sin mover el ratón físico si es posible).
        Usa pywinauto.
        """
        try:
            app = Application(backend="uia").connect(title_re=f".*{window_title}.*", timeout=3)
            dlg = app.top_window()
            
            # Buscar el control según prop
            # ej control_property = {"title": "Guardar", "control_type": "Button"}
            control = dlg.child_window(**control_property)
            control.click_input() # click_input() mueve un poco pero se asegura el focus, click() hace evento puro
            
            return {"status": "success", "message": f"Clicked on {control_property}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    async def type_text_in_element(window_title: str, control_property: Dict[str, Any], text: str) -> Dict[str, Any]:
        """
        Escribe texto en un elemento específico de una ventana específica (en segundo plano).
        """
        try:
            app = Application(backend="uia").connect(title_re=f".*{window_title}.*", timeout=3)
            dlg = app.top_window()
            control = dlg.child_window(**control_property)
            control.set_text(text)
            return {"status": "success", "message": f"Typed '{text[:10]}...'", "length": len(text)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    async def mouse_move(x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
        """
        [FALLBACK] Mueve ratón físico con trayectoria suave. Usar solo si es estrictamente necesario,
        ya que interrumpirá al usuario humano.
        """
        pyautogui.moveTo(x, y, duration=duration)
        return {"status": "success", "x": x, "y": y, "warning": "Physical mouse grabbed"}

    @staticmethod
    async def mouse_click(x: int, y: int, button: str = "left") -> Dict[str, Any]:
        """
        [FALLBACK] Click en posición física en pantalla.
        """
        pyautogui.click(x, y, button=button)
        return {"status": "success", "warning": "Physical mouse grabbed"}

    @staticmethod
    async def keyboard_type(text: str, interval: float = 0.05) -> Dict[str, Any]:
        """
        [FALLBACK] Escribe texto en la ventana que tenga foco global.
        """
        for char in text:
            pyautogui.typewrite(char)
            await asyncio.sleep(interval)
        return {"status": "success", "length": len(text), "warning": "Global focus used"}

    @staticmethod
    async def keyboard_hotkey(*keys: str) -> Dict[str, Any]:
        """
        [FALLBACK] Atajo global (Ctrl+C, Alt+Tab, etc)
        """
        pyautogui.hotkey(*keys)
        return {"status": "success"}

    @staticmethod
    async def screenshot(window_title: Optional[str] = None) -> bytes:
        """
        Captura pantalla. Si se provee window_title, intenta hacer captura de la ventana específica 
        sin importar lo que haya encima, si no, captura global.
        """
        buffer = io.BytesIO()
        try:
            if window_title:
                app = Application(backend="uia").connect(title_re=f".*{window_title}.*", timeout=2)
                dlg = app.top_window()
                img = dlg.capture_as_image()
            else:
                img = ImageGrab.grab()
            img.save(buffer, format="PNG")
        except Exception as e:
            # Fallback a pantalla completa si falla ventana
            img = ImageGrab.grab()
            img.save(buffer, format="PNG")
            
        return buffer.getvalue()
