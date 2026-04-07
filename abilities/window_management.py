import asyncio
from typing import List, Dict, Any, Optional

try:
    import pygetwindow as pgw
    from pywinauto.application import Application
except ImportError:
    pass

class WindowManagement:
    """
    Manejo avanzado de ventanas. 
    Ideal para el entorno Windows donde la IA necesita saber qué está abierto.
    """

    @staticmethod
    async def list_windows() -> List[Dict[str, Any]]:
        """Lista todas las ventanas abiertas útiles (ignora fondo)."""
        windows = []
        for w in pgw.getAllWindows():
            if w.title.strip() and w.width > 0 and w.height > 0:
                windows.append({
                    "title": w.title,
                    "x": w.left,
                    "y": w.top,
                    "width": w.width,
                    "height": w.height,
                    "active": w.isActive,
                    "isMinimized": w.isMinimized,
                    "isMaximized": w.isMaximized
                })
        return windows

    @staticmethod
    async def get_active_window() -> Optional[Dict[str, Any]]:
        """Obtiene ventana actualmente enfocada en el sistema global."""
        active = pgw.getActiveWindow()
        if not active or not active.title.strip():
            return None
        return {
            "title": active.title,
            "x": active.left,
            "y": active.top,
            "width": active.width,
            "height": active.height
        }

    @staticmethod
    async def activate_window(window_title: str) -> bool:
        """Trae ventana al frente. Interfiere con el usuario."""
        for window in pgw.getAllWindows():
            if window_title.lower() in window.title.lower():
                try:
                    if window.isMinimized:
                        window.restore()
                    window.activate()
                    return True
                except Exception:
                    # Alternativa pywinauto
                    try:
                        app = Application().connect(handle=window._hWnd)
                        app.top_window().set_focus()
                        return True
                    except:
                        pass
        return False

    @staticmethod
    async def close_window(window_title: str) -> bool:
        """Cierra ventana."""
        for window in pgw.getAllWindows():
            if window_title.lower() in window.title.lower():
                window.close()
                return True
        return False

    @staticmethod
    async def get_window_elements(window_title: str) -> Dict[str, Any]:
        """
        Escanea la interfaz de usuario de una ventana y devuelve una representación
        en texto de sus botones, campos y etiquetas. ¡Es el súper poder de la IA en Desktop!
        """
        try:
            app = Application(backend="uia").connect(title_re=f".*{window_title}.*", timeout=3)
            dlg = app.top_window()
            
            # wrapper para imprimir el árbol de controles a string
            import tempfile
            import os
            import sys
            
            original_stdout = sys.stdout
            temp_path = os.path.join(tempfile.gettempdir(), f"{hash(window_title)}_tree.txt")
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                sys.stdout = f
                dlg.print_control_identifiers(depth=3) # Depth para no saturar memoria
                sys.stdout = original_stdout
                
            with open(temp_path, 'r', encoding='utf-8') as f:
                tree_text = f.read()
                
            os.remove(temp_path)
            
            return {
                "status": "success", 
                "window": dlg.window_text(),
                "tree": tree_text
            }
        except Exception as e:
            return {"status": "error", "message": f"Could not inspect window: {e}"}
