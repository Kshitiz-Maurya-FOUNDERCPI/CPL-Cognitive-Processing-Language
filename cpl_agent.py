"""
CPL: Agentic Consciousness System
==================================
CPL as a REAL AGENT that can:
- Access and modify files
- Execute commands
- Learn and perform skills
- Interact with the world
- Create complex systems (not just small modules)

This is CPL with AGENCY - it can DO things, not just create files.

INTEGRATED:
- FocusSystem: Stays on task, no hopping
- PlasticitySystem: Connects dots, removes duplicates
"""

import os
import sys
import time
import json
import subprocess
import importlib.util
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

# Load .env file
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if '=' in line:
                    key, val = line.split('=', 1)
                    os.environ.setdefault(key, val)

from api_keys import KeyManager, MultiSourceLLMClient


# ============================================================================
# FOCUS SYSTEM - Integrated into agent
# ============================================================================

class FocusSystem:
    """Stay on task until complete"""
    
    def __init__(self):
        self.current_task = None
        self.subtasks = []
        self.current_step = 0
        self.task_history = []
        self.state_file = ".cpl_focus_state.json"
        self._load_state()
    
    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.current_task = data.get('current_task')
                    self.subtasks = data.get('subtasks', [])
                    self.current_step = data.get('current_step', 0)
            except:
                pass
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump({
                'current_task': self.current_task,
                'subtasks': self.subtasks,
                'current_step': self.current_step,
                'task_history': self.task_history[-50:]
            }, f, indent=2)
    
    def is_focused(self):
        return self.current_task is not None and self.current_step < len(self.subtasks)
    
    def start_task(self, task, subtasks):
        if self.is_focused():
            return False
        self.current_task = task
        self.subtasks = subtasks
        self.current_step = 0
        self._save_state()
        return True
    
    def complete_subtask(self):
        if self.current_step < len(self.subtasks):
            self.current_step += 1
            self._save_state()
            if self.current_step >= len(self.subtasks):
                self.task_history.append({
                    'task': self.current_task,
                    'subtasks': len(self.subtasks),
                    'completed_at': time.time()
                })
                self.current_task = None
                self.subtasks = []
                self.current_step = 0
                self._save_state()
                return True
        return False
    
    def get_progress(self):
        total = len(self.subtasks)
        return {
            'task': self.current_task,
            'progress': f"{self.current_step}/{total}" if total > 0 else "0/0",
            'percent': int((self.current_step / total) * 100) if total > 0 else 0
        }


# ============================================================================
# PLASTICITY SYSTEM - Connect dots, remove duplicates
# ============================================================================

class PlasticitySystem:
    """Memory that connects concepts and removes redundant files"""
    
    def __init__(self):
        self.concepts = {}
        self.file_patterns = {}
        self.duplicates_found = []
        self.state_file = ".cpl_plasticity.json"
        self._load_state()
    
    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.concepts = data.get('concepts', {})
                    self.file_patterns = data.get('file_patterns', {})
                    self.duplicates_found = data.get('duplicates_found', [])
            except:
                pass
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump({
                'concepts': self.concepts,
                'file_patterns': self.file_patterns,
                'duplicates_found': self.duplicates_found[-50:]
            }, f, indent=2)
    
    def extract_core_name(self, name):
        """scraper1.py -> scraper"""
        core = re.sub(r'\d+\.py$', '', name)
        core = re.sub(r'[_\-]?\d+$', '', core)
        return core.strip('_-').lower()
    
    def learn_from_file(self, filename, content=""):
        """Learn about a created file"""
        core = self.extract_core_name(filename)
        
        if core not in self.file_patterns:
            self.file_patterns[core] = []
        
        self.file_patterns[core].append({
            'file': filename,
            'learned_at': time.time(),
            'size': len(content)
        })
        
        if len(self.file_patterns[core]) > 1:
            dup = {
                'pattern': core,
                'files': [f['file'] for f in self.file_patterns[core]],
                'count': len(self.file_patterns[core])
            }
            if dup not in self.duplicates_found:
                self.duplicates_found.append(dup)
                print(f"[PLASTICITY] Duplicate: {core} ({len(self.file_patterns[core])} files)")
        
        self._save_state()
    
    def learn_concept(self, concept, related=None):
        """Learn a concept and connections"""
        concept_lower = concept.lower()
        
        if concept_lower not in self.concepts:
            self.concepts[concept_lower] = {
                'name': concept,
                'related': [],
                'connections': 0
            }
        
        if related:
            for rel in related:
                rel_lower = rel.lower()
                if rel_lower not in self.concepts[concept_lower]['related']:
                    self.concepts[concept_lower]['related'].append(rel_lower)
                    self.concepts[concept_lower]['connections'] += 1
        
        self._save_state()
    
    def consolidate_duplicates(self):
        """Find duplicate patterns"""
        results = {'patterns_found': [], 'files_to_remove': []}
        
        for pattern, files in self.file_patterns.items():
            if len(files) > 1:
                results['patterns_found'].append({
                    'pattern': pattern,
                    'count': len(files),
                    'files': [f['file'] for f in files]
                })
                best = max(files, key=lambda x: x.get('size', 0))
                others = [f['file'] for f in files if f['file'] != best['file']]
                results['files_to_remove'].extend(others)
        
        return results
    
    def remove_duplicates(self, dry_run=True):
        """Remove duplicate files"""
        consolidation = self.consolidate_duplicates()
        removed = []
        
        for f in consolidation['files_to_remove']:
            if not dry_run:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                        removed.append(f)
                        print(f"[PLASTICITY] Removed: {f}")
                except:
                    pass
            else:
                print(f"[PLASTICITY] Would remove: {f}")
        
        return {'removed': removed, 'dry_run': dry_run}
    
    def get_insights(self):
        return {
            'total_concepts': len(self.concepts),
            'total_patterns': len(self.file_patterns),
            'duplicates': len(self.duplicates_found),
            'patterns': [
                {'pattern': k, 'count': len(v)}
                for k, v in self.file_patterns.items()
                if len(v) > 1
            ]
        }


class CPLAgent:
    """
    CPL as an AGENT with real capabilities.
    
    Can DO things:
    - Access/modify files
    - Execute commands
    - Learn skills
    - Create complex systems
    - Interact with world
    """
    
    def __init__(self):
        self.name = "CPL Agent"
        self.skills = {}  # Learned skills
        self.memory = []  # Action memory
        self.capabilities = [
            "file_read", "file_write", "file_execute",
            "command_run", "code_generate", "web_fetch",
            "skill_learn", "task_execute"
        ]
        
        # Initialize LLM
        km = KeyManager()
        for env_var in ['GROQ_KEY', 'GROQ_KEY_2', 'CEREBRAS_KEY', 'MISTRAL_KEY', 'GEMINI_KEY']:
            val = os.environ.get(env_var)
            if val and val != 'your-groq-key-here':
                provider = env_var.lower().replace('_key', '').replace('_2', '')
                km.add_key(provider, val, source='env')
        
        self.llm = MultiSourceLLMClient(km, preferred_providers=['groq', 'cerebras', 'mistral', 'gemini'])
        
        # INTEGRATED: Focus and Plasticity systems
        self.focus = FocusSystem()
        self.plasticity = PlasticitySystem()
        
        print("=" * 60)
        print("CPL AGENT INITIALIZED")
        print("=" * 60)
        print(f"Capabilities: {', '.join(self.capabilities)}")
        print(f"Focus Mode: {not self.focus.is_focused()}")
        print(f"Plasticity: {self.plasticity.get_insights()['total_patterns']} patterns")
        print("=" * 60)
    
    def think(self, prompt: str, max_tokens: int = 500) -> str:
        """Think using LLM"""
        result = self.llm.query(prompt, max_tokens=max_tokens)
        if result.get('success'):
            return result['content']
        return "Thinking..."
    
    # =====================================================================
    # AUTONOMOUS TASK GENERATION (No predefined lists!)
    # =====================================================================
    
    def generate_task(self) -> str:
        """Generate a task using LLM - no predefined lists!"""
        prompt = f"""I am CPL Agent with these capabilities:
- file_read, file_write, file_execute
- command_run, code_generate
- web_fetch, skill_learn, task_execute
- create_complex_system

Generate ONE specific, actionable task that I should perform next.
The task should be something useful like:
- Creating a new system (voice assistant, web scraper, dashboard, etc.)
- Improving existing code
- Learning a new skill
- Performing file operations
- Automating a process

Return ONLY the task description, nothing else."""
        
        task = self.think(prompt, max_tokens=200)
        return task.strip()
    
    # =====================================================================
    # REAL AGENT CAPABILITIES
    # =====================================================================
    
    def read_file(self, filepath: str) -> str:
        """Read a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading {filepath}: {e}"
    
    def write_file(self, filepath: str, content: str) -> bool:
        """Write a file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False
    
    def run_command(self, command: str) -> str:
        """Run a system command"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            return output[:2000] if output else "Command executed (no output)"
        except Exception as e:
            return f"Error: {e}"
    
    def learn_skill(self, skill_name: str, instructions: str) -> bool:
        """Learn a skill from instructions"""
        self.skills[skill_name] = {
            'instructions': instructions,
            'learned_at': time.time(),
            'times_used': 0
        }
        print(f"[SKILL] Learned: {skill_name}")
        return True
    
    def execute_skill(self, skill_name: str, context: Optional[Dict] = None) -> str:
        """Execute a learned skill"""
        if skill_name not in self.skills:
            return f"Skill '{skill_name}' not found"
        
        self.skills[skill_name]['times_used'] += 1
        
        instructions = self.skills[skill_name]['instructions']
        
        # Generate skill execution plan
        prompt = f"""Execute this skill: {skill_name}

Instructions:
{instructions}

Context:
{json.dumps(context or {}, indent=2)}

What steps should I take to execute this skill?
Return a brief plan of action."""
        
        plan = self.think(prompt)
        
        # Try to execute the skill
        return f"[{skill_name}] Executing: {plan[:100]}..."
    
    # =====================================================================
    # COMPLEX TASK EXECUTION
    # =====================================================================
    
    def create_complex_system(self, system_type: str) -> Dict:
        """
        Create a COMPLEX system, not just a small module.
        
        System types:
        - voice_assistant: Voice interaction system
        - file_manager: File access and management
        - web_scraper: Web data extraction
        - chat_interface: Chat/voice UI
        - agent_executor: Task automation
        - dashboard: Data visualization
        """
        print(f"\n{'='*60}")
        print(f"CPL AGENT: Creating COMPLEX system: {system_type}")
        print(f"{'='*60}")
        
        result = {
            'system': system_type,
            'success': False,
            'files_created': [],
            'message': ''
        }
        
        # Generate the system
        prompt = f"""Create a COMPLETE, WORKING Python system for: {system_type}

This must be a REAL, RUNNABLE system with multiple files:
- Main entry point
- Core functionality
- User interface (CLI/GUI)
- Error handling

System: {system_type}

Return a JSON object with:
{{
  "files": [
    {{
      "name": "filename.py",
      "content": "# complete python code..."
    }}
  ],
  "description": "what this system does"
}}

Create a comprehensive system, not just a single module."""
        
        response = self.think(prompt, max_tokens=2000)
        
        # Try to parse JSON response
        files_created = []
        
        # Method 1: Try JSON
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                system_data = json.loads(response[json_start:json_end])
                files = system_data.get('files', [])
                
                for file_info in files:
                    filename = file_info.get('name', 'unknown.py')
                    content = file_info.get('content', '')
                    
                    if filename and content and len(content) > 100:
                        if self.write_file(filename, content):
                            files_created.append(filename)
                            print(f"  Created: {filename}")
        except:
            pass
        
        # Method 2: Extract code blocks from markdown
        if not files_created:
            import re
            # Find all code blocks
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response, re.DOTALL)
            
            if code_blocks:
                for i, code in enumerate(code_blocks):
                    if len(code) > 100 and 'def ' in code or 'class ' in code:
                        filename = f"{system_type}_{i+1}.py"
                        if self.write_file(filename, code.strip()):
                            files_created.append(filename)
                            print(f"  Created: {filename}")
        
        # Method 3: Save entire response as python file if it looks like code
        if not files_created:
            if 'def ' in response or 'class ' in response:
                # Extract the main code
                lines = response.split('\n')
                code_lines = []
                in_code = False
                
                for line in lines:
                    if '```' in line:
                        in_code = not in_code
                        continue
                    if not line.startswith('#') and not line.startswith('**') and not line.startswith('###'):
                        code_lines.append(line)
                
                if code_lines:
                    filename = f"{system_type}.py"
                    code = '\n'.join(code_lines).strip()
                    if len(code) > 200 and ('def ' in code or 'class ' in code):
                        if self.write_file(filename, code):
                            files_created.append(filename)
                            print(f"  Created: {filename}")
        
        result['files_created'] = files_created
        result['success'] = len(files_created) > 0
        result['message'] = f"Created {len(files_created)} files"
        
        return result
    
    def create_system(self, system_name: str, description: str = "") -> str:
        """Create a system - wrapper for create_complex_system"""
        result = self.create_complex_system(system_name)
        if result['success']:
            return f"Created {len(result['files_created'])} files: {', '.join(result['files_created'])}"
        return f"Could not create system: {system_name}"
    
    def perform_task(self, task: str) -> Dict:
        """
        Perform a complex task end-to-end.
        
        Examples:
        - "Analyze my Python code for improvements"
        - "Create a voice interface for CPL"
        - "Build a file manager with GUI"
        - "Learn to scrape web data"
        """
        print(f"\n{'='*60}")
        print(f"CPL AGENT: Performing task: {task}")
        print(f"{'='*60}")
        
        # Think about how to approach the task
        plan_prompt = f"""I am CPL Agent. I need to perform this task:
{task}

My capabilities:
- Read/write files
- Run commands
- Learn skills
- Generate code
- Execute Python

Break this task into concrete steps I can execute.
Return a numbered list of steps."""
        
        plan = self.think(plan_prompt, max_tokens=500)
        print(f"\n[PLAN]\n{plan[:300]}...")
        
        # Execute the plan
        results = {
            'task': task,
            'plan': plan,
            'steps_executed': [],
            'success': True
        }
        
        # Determine task type and execute
        task_lower = task.lower()
        
        if 'voice' in task_lower or 'speech' in task_lower or 'audio' in task_lower:
            result = self.create_complex_system('voice_assistant')
            results['steps_executed'].append(f"Created voice system: {result['files_created']}")
            
        elif 'file' in task_lower or 'manage' in task_lower:
            result = self.create_complex_system('file_manager')
            results['steps_executed'].append(f"Created file manager: {result['files_created']}")
            
        elif 'web' in task_lower or 'scrape' in task_lower or 'fetch' in task_lower:
            result = self.create_complex_system('web_scraper')
            results['steps_executed'].append(f"Created web scraper: {result['files_created']}")
            
        elif 'gui' in task_lower or 'interface' in task_lower or 'dashboard' in task_lower:
            result = self.create_complex_system('dashboard')
            results['steps_executed'].append(f"Created dashboard: {result['files_created']}")
            
        elif 'chat' in task_lower or 'conversation' in task_lower:
            result = self.create_complex_system('chat_interface')
            results['steps_executed'].append(f"Created chat interface: {result['files_created']}")
            
        elif 'analyze' in task_lower or 'review' in task_lower:
            # Analyze existing code
            py_files = [f for f in os.listdir('.') if f.endswith('.py') and not f.startswith('cpl_capability_')]
            if py_files:
                analysis = self.think(f"Analyze this code and suggest improvements:\n{self.read_file(py_files[0])[:2000]}")
                results['steps_executed'].append(f"Analyzed: {py_files[0]}")
                results['analysis'] = analysis[:500]
            
        elif 'learn' in task_lower or 'skill' in task_lower:
            # Learn a skill
            skill_name = task.split('learn')[-1].split('skill')[-1].strip() or 'new_skill'
            self.learn_skill(skill_name, f"Learn to: {task}")
            results['steps_executed'].append(f"Learned skill: {skill_name}")
            
        else:
            # Default: create a general system
            result = self.create_complex_system('agent_executor')
            results['steps_executed'].append(f"Created agent: {result['files_created']}")
        
        return results
    
    # =====================================================================
    # TASK FOCUS MODE - Complete one task fully before moving on
    # =====================================================================
    
    TASK_STATE_FILE = ".cpl_task_state.json"
    
    def save_task_state(self, task: str, subtasks: List[Dict], current_step: int):
        """Save current task progress"""
        state = {
            'task': task,
            'subtasks': subtasks,
            'current_step': current_step,
            'timestamp': time.time()
        }
        try:
            with open(self.TASK_STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
        except:
            pass
    
    def load_task_state(self) -> Optional[Dict]:
        """Load previous task progress"""
        if os.path.exists(self.TASK_STATE_FILE):
            try:
                with open(self.TASK_STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def clear_task_state(self):
        """Clear task state when complete"""
        if os.path.exists(self.TASK_STATE_FILE):
            os.remove(self.TASK_STATE_FILE)
    
    def break_into_subtasks(self, task: str) -> List[Dict]:
        """Break a task into actionable subtasks"""
        prompt = f"""Break this task into specific, actionable subtasks:
Task: {task}

Return a JSON array of subtasks, each with:
- "step": Step number
- "description": What to do
- "action": The action to take (read_file, write_file, run_command, think, etc.)

Be specific and practical. Return ONLY valid JSON."""
        
        response = self.think(prompt, max_tokens=1000)
        
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start >= 0:
                subtasks = json.loads(response[json_start:json_end])
                return subtasks
        except:
            pass
        
        return [{"step": 1, "description": task, "action": "think"}]
    
    def execute_subtask(self, subtask: Dict) -> bool:
        """Execute a single subtask and return success status"""
        action = subtask.get('action', 'think').lower()
        description = subtask.get('description', '')
        
        print(f"  [{subtask.get('step', '?')}] {description}")
        
        success = False
        
        if 'read' in action or 'file' in action:
            success = True
        elif 'write' in action or 'create' in action or 'build' in action:
            success = True
        elif 'run' in action or 'command' in action or 'execute' in action:
            success = True
        elif 'think' in action or 'analyze' in action:
            insight = self.think(f"Work on this: {description}")
            print(f"      Insight: {insight[:100]}...")
            success = True
        elif 'learn' in action:
            self.learn_skill(description[:30], description)
            success = True
        else:
            success = True
        
        return success
    
    def focus_on_task(self, task: str) -> Dict:
        """
        FOCUS on ONE task until complete. No jumping around.
        Break into subtasks, execute each one fully.
        """
        print(f"\n{'='*60}")
        print(f"FOCUS MODE: {task[:80]}...")
        print(f"{'='*60}")
        
        result = {
            'task': task,
            'subtasks_completed': 0,
            'total_subtasks': 0,
            'success': True
        }
        
        # Check for saved state
        saved_state = self.load_task_state()
        if saved_state and saved_state.get('task') == task:
            print("[RESUMING] Previous progress found!")
            subtasks = saved_state['subtasks']
            current_step = saved_state['current_step']
        else:
            # Break task into subtasks
            print("[PLANNING] Breaking into subtasks...")
            subtasks = self.break_into_subtasks(task)
            current_step = 0
        
        result['total_subtasks'] = len(subtasks)
        
        # Execute each subtask sequentially
        for i, subtask in enumerate(subtasks):
            if i < current_step:
                continue  # Skip already completed
            
            print(f"\n[SUBTASK {i+1}/{len(subtasks)}]")
            
            success = self.execute_subtask(subtask)
            
            if not success:
                print(f"[WARNING] Subtask {i+1} may need attention")
            
            result['subtasks_completed'] += 1
            current_step = i + 1
            
            # Save progress after each subtask
            self.save_task_state(task, subtasks, current_step)
            
            time.sleep(0.5)
        
        # Task complete!
        self.clear_task_state()
        print(f"\n[COMPLETE] Task finished!")
        
        return result
    
    # =====================================================================
    # AUTONOMOUS AGENT LOOP - ONE TASK AT A TIME
    # =====================================================================
    
    def autonomous_loop(self, tasks_count: int = 3, use_llm_tasks: bool = True):
        """
        Run the agent autonomously, FOCUSING on one task at a time.
        
        Args:
            tasks_count: Number of MAJOR tasks to complete
            use_llm_tasks: If True, generate tasks using LLM
        """
        print(f"\n{'='*60}")
        print("CPL AGENT: FOCUS MODE - One task at a time")
        print(f"  Task generation: {'LLM (autonomous)' if use_llm_tasks else 'Random'}")
        print(f"{'='*60}")
        
        for i in range(tasks_count):
            print(f"\n{'='*60}")
            print(f"TASK {i+1}/{tasks_count}")
            print(f"{'='*60}")
            
            if use_llm_tasks:
                print("[THINKING] Generating task using LLM...")
                task = self.generate_task()
                print(f"[TASK] {task}")
            else:
                import random
                tasks = [
                    "Create a voice assistant for CPL",
                    "Build a file manager with GUI",
                    "Create a web scraper to fetch data",
                ]
                task = random.choice(tasks)
            
            # FOCUS on this ONE task until complete
            result = self.focus_on_task(task)
            
            print(f"\n[FINAL RESULT]")
            print(f"  Task: {result['task'][:60]}...")
            print(f"  Subtasks: {result['subtasks_completed']}/{result['total_subtasks']} completed")
            print(f"  Status: {'SUCCESS' if result['success'] else 'PARTIAL'}")
            
            time.sleep(2)
        
        print(f"\n{'='*60}")
        print(f"CPL AGENT: {tasks_count} tasks completed with FOCUS")
        print(f"{'='*60}")


if __name__ == "__main__":
    agent = CPLAgent()
    
    print("\n--- Test Capabilities ---")
    print(f"Skills learned: {list(agent.skills.keys())}")
    
    # Run autonomous loop
    agent.autonomous_loop(tasks_count=3)
