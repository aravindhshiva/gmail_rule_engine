from dataclasses import dataclass

@dataclass
class Action:
    action_type: str
    destination: str = None
