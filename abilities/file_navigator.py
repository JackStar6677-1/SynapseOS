import os
from pathlib import Path
from typing import Dict, Any, List

class FileNavigator:
    """
    Módulo para que la IA entienda y navegue el entorno del file system de Windows local.
    Le da contexto de "dónde está parada".
    """
    
    def __init__(self):
        self.current_directory = str(Path.cwd().absolute())
        
    def pwd(self) -> str:
        """Devuelve el directorio actual del bot."""
        return self.current_directory
        
    def cd(self, path: str) -> Dict[str, Any]:
        """Cambia el directorio de trabajo simulado del bot."""
        try:
            target = Path(self.current_directory) / path
            target = target.resolve()
            if not target.exists() or not target.is_dir():
                return {"status": "error", "message": f"Directory not found: {target}"}
            
            self.current_directory = str(target)
            return {"status": "success", "new_path": self.current_directory}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def ls(self, show_hidden: bool = False) -> Dict[str, Any]:
        """Lista los archivos y carpetas del directorio actual."""
        try:
            target = Path(self.current_directory)
            results = []
            for item in target.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                info = {
                    "name": item.name,
                    "is_dir": item.is_dir(),
                    "size_mb": round(item.stat().st_size / (1024*1024), 4) if item.is_file() else None,
                    "ext": item.suffix if item.is_file() else None
                }
                results.append(info)
                
            return {
                "status": "success", 
                "path": self.current_directory,
                "items": results
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def read_file(self, filename: str, lines: int = 100) -> Dict[str, Any]:
        """Lee las primeras N líneas de un archivo para entender contexto."""
        try:
            target = Path(self.current_directory) / filename
            if not target.exists() or not target.is_file():
                return {"status": "error", "message": "File not found."}
                
            content = []
            with open(target, 'r', encoding='utf-8', errors='replace') as f:
                for i, line in enumerate(f):
                    if i >= lines:
                        content.append("... [TRUNCATED]")
                        break
                    content.append(line.rstrip())
                    
            return {
                "status": "success",
                "content": "\n".join(content)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
