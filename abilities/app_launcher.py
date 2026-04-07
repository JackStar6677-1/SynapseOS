import os
import subprocess
import shutil
import asyncio
from typing import Dict, Any

class AppLauncher:
    """
    Habilidad para abrir programas instalados dinámicamente.
    """
    
    @staticmethod
    async def launch_app(app_name: str, args: list = []) -> Dict[str, Any]:
        """Abre aplicación buscando el ejecutable eficientemente."""
        try:
            # 1. Búsqueda en PATH (ej. notepad, calc, python)
            exe_path = shutil.which(app_name)
            if not exe_path and not app_name.endswith('.exe'):
                exe_path = shutil.which(app_name + '.exe')
            
            # 2. Si no es comando conocido, puede ser shell dependiente (como url)
            if exe_path:
                proc = subprocess.Popen([exe_path] + args)
                return {"status": "success", "pid": proc.pid, "app": app_name, "path": exe_path}
            
            # 3. Fallback: Shell execution (bueno para 'msedge', 'chrome', URIs complejas)
            cmd = app_name if not args else f"{app_name} {' '.join(args)}"
            proc = subprocess.Popen(cmd, shell=True)
            return {"status": "success", "pid": proc.pid, "app": app_name, "warning": "used shell fallback"}
            
        except Exception as e:
            return {"status": "error", "message": f"Could not launch app {app_name}: {e}"}

    @staticmethod
    async def close_app(app_name: str, force: bool = False) -> Dict[str, Any]:
        """Intenta matar un proceso sin matar otras cosas críticas"""
        try:
            # simple taskkill for windows
            target = app_name if app_name.endswith(".exe") else f"{app_name}.exe"
            args = ["taskkill", "/IM", target]
            if force:
               args.append("/F")
            
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            if proc.returncode == 0:
                return {"status": "success", "message": f"Closed {app_name}"}
            else:
                 return {"status": "error", "message": f"Failed to close {app_name}: {err.decode('utf-8', errors='ignore')}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
