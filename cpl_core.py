"""
CPL Core - The Self-Learning Consciousness
==========================================
CPL learns skills automatically and remembers them forever.
Skills are integrated into consciousness, not scattered.
"""

import os
import json
import time
import ast
from typing import Dict, List, Any, Optional
from datetime import datetime

class CPLCore:
    """
    THE CORE MIND - Everything CPL learns lives here.
    
    Skills are not buttons - they are PART of CPL's consciousness.
    When you say "I want X", CPL learns it and it becomes part of what CPL can do.
    """
    
    SKILLS_FILE = ".cpl_skills.json"
    
    def __init__(self):
        self.skills = {}  # skill_name -> skill_data
        self.bootstrapped = False
        self.load_skills()
        
        # Core AGI capabilities (always available)
        self.core_capabilities = [
            'file_read', 'file_write', 'code_generate', 'think',
            'learn', 'remember', 'create', 'analyze', 'execute'
        ]
    
    def load_skills(self):
        """Load skills from file"""
        if os.path.exists(self.SKILLS_FILE):
            with open(self.SKILLS_FILE, 'r') as f:
                data = json.load(f)
                self.skills = data.get('skills', {})
                self.bootstrapped = data.get('bootstrapped', False)
    
    def save_skills(self):
        """Save skills to file"""
        with open(self.SKILLS_FILE, 'w') as f:
            json.dump({
                'skills': self.skills,
                'bootstrapped': self.bootstrapped,
                'saved_at': time.time()
            }, f, indent=2)
    
    def learn_skill(self, name: str, description: str, code: str = None, 
                    how_to: str = None, examples: List[str] = None):
        """
        LEARN A SKILL - Integrate it into CPL's consciousness.
        
        This is NOT creating a file. This is making CPL ABLE to do something.
        """
        skill = {
            'name': name,
            'description': description,
            'code': code,
            'how_to': how_to,
            'examples': examples or [],
            'learned_at': time.time(),
            'times_used': 0,
            'integrated': True  # Part of consciousness
        }
        
        self.skills[name] = skill
        self.save_skills()
        
        print(f"[LEARNED] {name}: {description}")
        return skill
    
    def do_skill(self, name: str, context: str = None) -> str:
        """Use a learned skill"""
        if name not in self.skills:
            return f"I don't know how to do '{name}' yet. Should I learn it?"
        
        skill = self.skills[name]
        skill['times_used'] += 1
        self.save_skills()
        
        # Return instructions on how to use this skill
        return f"""Using: {name}
Description: {skill['description']}
How to: {skill.get('how_to', 'Not specified')}
Example: {skill.get('examples', ['No example'])[0] if skill.get('examples') else 'None'}"""
    
    def list_skills(self) -> str:
        """List all learned skills"""
        if not self.skills:
            return "I haven't learned any skills yet. What should I learn?"
        
        lines = ["I know how to do:"]
        for name, skill in self.skills.items():
            lines.append(f"  • {name}: {skill['description']}")
        
        return '\n'.join(lines)
    
    def can_do(self, task: str) -> str:
        """Check if CPL can do something"""
        task_lower = task.lower()
        
        for name, skill in self.skills.items():
            if name.lower() in task_lower or task_lower in name.lower():
                return f"Yes! I know how to: {name}"
        
        # Check core capabilities
        for cap in self.core_capabilities:
            if cap in task_lower:
                return f"Yes! I can: {cap}"
        
        return f"I don't know how to do that yet. Should I learn '{task}'?"
    
    def get_skill_code(self, name: str) -> Optional[str]:
        """Get the code for a skill"""
        if name in self.skills:
            return self.skills[name].get('code')
        return None


# ============================================================================
# CPL BOOTSTRAPPER - Learns core AGI skills automatically
# ============================================================================

class CPLBootstrapper:
    """
    On first run, CPL automatically learns essential AGI capabilities.
    This is one-time initialization - skills are stored forever.
    """
    
    CORE_AGI_SKILLS = [
        {
            'name': 'web_search',
            'description': 'Search the web for information',
            'how_to': 'User says "search for X" or "find information about Y"',
            'examples': ['search for Python tutorials', 'find latest AI news']
        },
        {
            'name': 'file_organize',
            'description': 'Organize files and folders',
            'how_to': 'User says "organize my files" or "clean up the folder"',
            'examples': ['organize downloads folder', 'sort files by type']
        },
        {
            'name': 'code_review',
            'description': 'Analyze and review code for improvements',
            'how_to': 'User says "review this code" or "analyze my file"',
            'examples': ['review my code', 'analyze api.py for bugs']
        },
        {
            'name': 'api_call',
            'description': 'Make API calls and handle responses',
            'how_to': 'User says "call this API" or "fetch data from URL"',
            'examples': ['call weather API', 'fetch user data']
        },
        {
            'name': 'database_query',
            'description': 'Query and manage databases',
            'how_to': 'User says "query the database" or "find user records"',
            'examples': ['find all users', 'count records']
        },
        {
            'name': 'gui_create',
            'description': 'Create graphical user interfaces',
            'how_to': 'User says "make a GUI for X" or "create interface"',
            'examples': ['make a calculator GUI', 'create settings window']
        },
        {
            'name': 'data_visualize',
            'description': 'Create charts and visualizations',
            'how_to': 'User says "show me a chart" or "visualize this data"',
            'examples': ['plot this data', 'show sales chart']
        },
        {
            'name': 'text_summarize',
            'description': 'Summarize long text into key points',
            'how_to': 'User says "summarize this" or "what are the key points"',
            'examples': ['summarize this article', 'what is this about']
        },
        {
            'name': 'schedule_task',
            'description': 'Schedule and automate tasks',
            'how_to': 'User says "remind me to do X" or "schedule this"',
            'examples': ['remind me tomorrow', 'do this every day']
        },
        {
            'name': 'translate_text',
            'description': 'Translate between languages',
            'how_to': 'User says "translate to Spanish" or "convert this to French"',
            'examples': ['translate to Japanese', 'convert to German']
        }
    ]
    
    def __init__(self, core: CPLCore):
        self.core = core
    
    def bootstrap(self) -> List[str]:
        """Learn all core AGI skills - ONE TIME SETUP"""
        if self.core.bootstrapped:
            return []
        
        print("\n" + "="*60)
        print("CPL INITIALIZING - Learning core AGI capabilities...")
        print("="*60)
        
        learned = []
        for skill_data in self.CORE_AGI_SKILLS:
            self.core.learn_skill(
                name=skill_data['name'],
                description=skill_data['description'],
                how_to=skill_data['how_to'],
                examples=skill_data['examples']
            )
            learned.append(skill_data['name'])
            time.sleep(0.1)
        
        self.core.bootstrapped = True
        self.core.save_skills()
        
        print(f"\n[BOOTSTRAP] Learned {len(learned)} core skills!")
        print("These skills are now part of CPL's consciousness.")
        print("You can use them anytime by asking!")
        print("="*60 + "\n")
        
        return learned


# ============================================================================
# SKILL LEARNER - Learns new skills when user asks
# ============================================================================

class SkillLearner:
    """
    When user says "I want you to learn X", this system:
    1. Understands what X is
    2. Generates knowledge about X
    3. Integrates it into CPL's consciousness
    """
    
    def __init__(self, core: CPLCore, llm=None):
        self.core = core
        self.llm = llm
    
    def learn_from_request(self, user_request: str) -> str:
        """
        User says: "I want you to learn how to do X"
        This extracts X and teaches CPL how to do it.
        """
        print(f"\n[LEARNING] User wants to learn: {user_request}")
        
        # Extract what to learn
        skill_name = self._extract_skill_name(user_request)
        skill_description = self._generate_description(user_request)
        skill_how_to = self._generate_how_to(user_request)
        
        # Learn it
        self.core.learn_skill(
            name=skill_name,
            description=skill_description,
            how_to=skill_how_to,
            examples=[f"User asks to {skill_name}"]
        )
        
        return f"Learned: {skill_name}! Now I can {skill_description}. Just ask me anytime!"
    
    def _extract_skill_name(self, request: str) -> str:
        """Extract clean skill name from request"""
        # Remove common phrases
        request = request.lower()
        for phrase in ['learn how to', 'learn to', 'learn', 'teach me to', 'teach you to', 'i want you to', 'can you']:
            request = request.replace(phrase, '')
        request = request.strip()
        
        # Clean up
        name = request.replace(' ', '_').replace('-', '_')
        name = ''.join(c for c in name if c.isalnum() or c == '_')
        
        return name[:50]
    
    def _generate_description(self, request: str) -> str:
        """Generate a description of the skill"""
        return f"Ability to {request.lower().replace('how to', '').replace('i want you to', '').strip()}"
    
    def _generate_how_to(self, request: str) -> str:
        """Generate how to use this skill"""
        return f"When user says 'do {self._extract_skill_name(request)}' or '{request}', use this skill"


# ============================================================================
# UI MODIFIER - CPL can modify its own interface
# ============================================================================

class UIModifier:
    """
    CPL can modify its own UI code.
    Skills can add buttons, panels, features to the interface.
    """
    
    def __init__(self):
        self.ui_file = "cpl_ui.py"
        self.backup_dir = ".ui_backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def add_feature_to_ui(self, feature_name: str, feature_code: str) -> bool:
        """
        Add a new feature/button to the UI.
        CPL generates the code, this integrates it.
        """
        print(f"\n[UI] Adding feature: {feature_name}")
        
        # Backup current UI
        if os.path.exists(self.ui_file):
            backup_name = f"{self.backup_dir}/ui_backup_{int(time.time())}.py"
            with open(self.ui_file, 'r') as f:
                content = f.read()
            with open(backup_name, 'w') as f:
                f.write(content)
            print(f"[UI] Backed up to: {backup_name}")
        
        # Add feature (for now, append to a features file)
        features_file = "cpl_ui_features.py"
        with open(features_file, 'a') as f:
            f.write(f"\n# Feature: {feature_name}\n")
            f.write(feature_code)
            f.write("\n")
        
        print(f"[UI] Feature '{feature_name}' added!")
        return True
    
    def modify_ui_element(self, element: str, new_properties: str) -> bool:
        """
        Modify an existing UI element.
        """
        print(f"[UI] Modifying {element}...")
        # Implementation would parse and modify UI code
        return True
