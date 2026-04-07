import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class PlaybookLibrary:
    """
    Cuando un agente encuentra una solución iterativa a "open spotify and play X", 
    los pasos (comandos/ui-clicks) se guardan aquí. La siguiente vez buscará 
    coincidencia exacta o semántica y se ahorrará llamadas de la LLM.
    """
    def __init__(self):
        self.db_path = Path("tasks") / "playbooks.json"
        self.playbooks = {}
        self._load()
        
    def _load(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.db_path.exists():
            try:
                with open(self.db_path, "r") as f:
                    self.playbooks = json.load(f)
            except:
                self.playbooks = {}
                
    def _save(self):
        with open(self.db_path, "w") as f:
            json.dump(self.playbooks, f, indent=2)

    def save_playbook(self, intent: str, resolved_steps: List[Dict[str, Any]]):
        """Almacena una serie de pasos rígidos para la intención descripta."""
        # Se normaliza la intencion (muy basico localmente para V1)
        normalized_intent = intent.lower().strip()
        self.playbooks[normalized_intent] = {
            "steps": resolved_steps,
            "success_rate": 1.0,
            "created_at": datetime.now().isoformat()
        }
        self._save()

    def find_playbook(self, intent: str) -> Optional[List[Dict[str, Any]]]:
        """Intenta localizar un mapa directo de acciones sin necesidad de LLM."""
        normalized_intent = intent.lower().strip()
        if normalized_intent in self.playbooks:
            return self.playbooks[normalized_intent]["steps"]
        return None
