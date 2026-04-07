import asyncio
import subprocess
import os
import signal
from typing import Dict, Any

class TerminalSession:
    """Representa una sesión de terminal activa administrada por el bot."""
    def __init__(self, t_type: str, shell_args: list):
        self.type = t_type
        # Inciar proceso de manera interactiva sin consola visible
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        self.process = subprocess.Popen(
            shell_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            startupinfo=startupinfo
        )
        self.output_buffer = ""

    async def run_command(self, cmd: str, timeout: int = 10) -> str:
        """Ejecuta un comando en esta sesión y espera un timeout corto para capturar resultado"""
        if self.process.poll() is not None:
            return "Session has ended/closed."
            
        # Write command + newline
        self.process.stdin.write(cmd + "\n")
        self.process.stdin.flush()
        
        # Leemos async de stdout
        # Esto no es perfecto en Windows sin librerías estilo 'pexpect', 
        # pero para comandos simples puede funcionar usando asyncio
        result = []
        try:
            # Damos tiempo a que el comando responda
            await asyncio.sleep(timeout)
            
            import msvcrt
            import os
            # Solo leemos si hay bytes disponibles en el buffer para no bloquear
            while True:
                # O_NONBLOCK trick no aplicable fácilmente en win32 subprocess
                # Leemos la salida disponible (esto requiere un workaround en prod para que no se congele)
                # Como alternativa, para comandos que se completan, usamos communicate()
                break # Para la V1. Una mejor manera es usar hilos o comunicate en comandos one-off
                
        except Exception as e:
             return f"Capture error: {e}"
        
        return "Command injected to session. Full async streaming to be implemented."

class TerminalControl:
    """
    Para abrir y administrar consolas (Powershell, CMD) aisladas
    sin mostrar molestas ventanas cmd extra en el escritorio.
    """
    
    _sessions = {}
    
    @staticmethod
    async def run_one_off_command(command: str, is_powershell: bool = True, as_admin: bool = False, timeout: int = 30) -> Dict[str, Any]:
        """
        Ejecuta un comando individual y retorna TODA la respuesta de texto.
        """
        shell = "powershell.exe" if is_powershell else "cmd.exe"
        args = ["powershell.exe", "-Command", command] if is_powershell else ["cmd.exe", "/c", command]

        # In as_admin the true solution requires elevating the process, 
        # but if synapseOS runs as User, it will prompt UAC to User! 
        # So we warn if elevation needed without having it.
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW # Hide window
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                startupinfo=startupinfo
            )
            
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            
            out_str = stdout.decode('utf-8', errors='replace').strip()
            err_str = stderr.decode('utf-8', errors='replace').strip()
            
            if proc.returncode != 0:
                return {
                    "status": "error", 
                    "code": proc.returncode, 
                    "output": out_str, 
                    "error": err_str
                }
            
            return {
                "status": "success", 
                "output": out_str
            }
            
        except asyncio.TimeoutError:
            return {"status": "error", "message": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    async def open_session(session_id: str, is_powershell: bool = True) -> Dict[str, Any]:
        # TBD: Administrar sesiones con persistencia de variables
        pass
