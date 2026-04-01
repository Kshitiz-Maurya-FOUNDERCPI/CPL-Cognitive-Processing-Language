from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ToolCallStep:
    tool: str
    args: Dict[str, Any]


@dataclass
class Skill:
    name: str
    description: str = ""
    steps: List[ToolCallStep] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.steps is None:
            self.steps = []


class SkillsStore:
    """
    Persistent skills stored as JSON under data/skills.json
    """

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.path = self.data_dir / "skills.json"
        self.skills: Dict[str, Skill] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.skills = {}
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            self.skills = {}
            return
        skills_raw: Dict[str, Any] = raw.get("skills", {})
        out: Dict[str, Skill] = {}
        for name, s in skills_raw.items():
            steps_raw = s.get("steps", [])
            steps = [ToolCallStep(tool=str(x["tool"]), args=dict(x.get("args", {}))) for x in steps_raw]
            out[name] = Skill(
                name=name,
                description=str(s.get("description", "")),
                steps=steps,
            )
        self.skills = out

    def save(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "skills": {
                name: {
                    "description": skill.description,
                    "steps": [{"tool": st.tool, "args": st.args} for st in skill.steps],
                }
                for name, skill in self.skills.items()
            }
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def upsert(self, skill: Skill) -> None:
        self.skills[skill.name] = skill
        self.save()

    def delete(self, name: str) -> bool:
        if name in self.skills:
            del self.skills[name]
            self.save()
            return True
        return False

    def list_names(self) -> List[str]:
        return sorted(self.skills.keys())

    def get(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)

