from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class CaseInput(BaseModel):
    case_text: str
    selected_agents: List[str] = ["Case Organizer", "Radiologist", "Pathologist", "Pulmonologist", "Rheumatologist", "Moderator"]
    model_configs: Dict[str, str] = {} # e.g. {"Radiologist": "gpt-4"}

class AgentStatusUpdate(BaseModel):
    role: str
    status: str # "working", "idle"

class StreamEvent(BaseModel):
    type: str # "status", "log", "token", "result", "error"
    role: Optional[str] = None
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
