"""
CPL Assistant - Natural Language Interface
==========================================
Talk to CPL like a real assistant!

Commands:
- "analyze filename.py" - Analyze a file
- "create web scraper" - Create something new
- "learn skill" - Learn a new skill
- "status" - Show CPL status
- "autonomous" - Run independently
- Just chat naturally!

Or just talk to CPL!
"""

import os
import sys
import time
import json

# Voice modules - optional
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

sys.path.insert(0, '.')
from unified_consciousness import UnifiedConsciousness


class CPLAssistant:
    """
    CPL as a real assistant you can TALK to.
    
    Features:
    - Voice input/output
    - Natural language commands
    - Persistent memory of your preferences
    - Can execute tasks autonomously
    """
    
    def __init__(self):
        print("=" * 60)
        print("CPL ASSISTANT - Natural Language Interface")
        print("=" * 60)
        
        # Initialize consciousness
        self.cpl = UnifiedConsciousness()
        
        # Load user preferences
        self.user_preferences = self._load_preferences()
        
        # Voice engine
        self.voice_enabled = False
        if VOICE_AVAILABLE:
            try:
                self.tts = pyttsx3.init()
                self.voice_enabled = True
                print("[VOICE] Text-to-speech enabled")
            except:
                print("[VOICE] Text-to-speech not available")
        else:
            print("[VOICE] Voice modules not installed (pip install SpeechRecognition pyttsx3)")
        
        # Command patterns
        self.commands = {
            'analyze': self.cmd_analyze,
            'create': self.cmd_create,
            'learn': self.cmd_learn,
            'what can you do': self.cmd_capabilities,
            'help': self.cmd_capabilities,
            'status': self.cmd_status,
            'run': self.cmd_run_autonomous,
            'stop': self.cmd_stop,
            'remember': self.cmd_remember,
            'forget': self.cmd_forget,
        }
        
        print("[READY] CPL Assistant initialized!")
        print()
    
    def _load_preferences(self) -> dict:
        """Load user preferences"""
        pref_file = ".cpl_preferences.json"
        if os.path.exists(pref_file):
            with open(pref_file, 'r') as f:
                return json.load(f)
        return {
            'name': 'Boss',
            'voice_enabled': False,
            'autonomous': False
        }
    
    def _save_preferences(self):
        """Save user preferences"""
        with open('.cpl_preferences.json', 'w') as f:
            json.dump(self.user_preferences, f, indent=2)
    
    def speak(self, text: str):
        """Speak text aloud"""
        if self.voice_enabled:
            self.tts.say(text)
            self.tts.runAndWait()
        print(f"CPL: {text}")
    
    def listen(self) -> str:
        """Listen for voice input"""
        if not self.voice_enabled:
            return input("You: ")
        
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
        
        try:
            text = recognizer.recognize_google(audio)
            print(f"You: {text}")
            return text
        except:
            return input("You: ")
    
    def parse_command(self, text: str) -> tuple:
        """Parse natural language into command and target"""
        text = text.lower().strip()
        
        # Check for command patterns
        for pattern, handler in self.commands.items():
            if pattern in text:
                # Extract target after the command
                parts = text.split(pattern, 1)
                target = parts[1].strip() if len(parts) > 1 else ""
                return handler, target
        
        # No command found - treat as conversation
        return self.cmd_converse, text
    
    def execute(self, text: str):
        """Execute a command"""
        handler, target = self.parse_command(text)
        return handler(target)
    
    # ============================================================
    # COMMAND HANDLERS
    # ============================================================
    
    def cmd_analyze(self, target: str) -> str:
        """Analyze a file or code"""
        if not target:
            return "What should I analyze? Tell me a filename or paste code."
        
        # Extract filename
        if ':' in target:
            parts = target.split(':', 1)
            filename = parts[1].strip()
        else:
            filename = target.strip()
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read()
            
            result = self.cpl.focus_on_task(f"Analyze this code and suggest improvements: {filename}")
            return f"Analyzed {filename}. {result['subtasks_completed']} subtasks completed."
        else:
            return f"File not found: {filename}"
    
    def cmd_create(self, target: str) -> str:
        """Create something"""
        if not target:
            return "What should I create? For example: 'create a web scraper' or 'create a calculator'"
        
        result = self.cpl.focus_on_task(f"Create: {target}")
        return f"Created! {result['subtasks_completed']} steps completed."
    
    def cmd_learn(self, target: str) -> str:
        """Learn a new skill"""
        if not target:
            return "What should I learn? Tell me a skill to learn."
        
        skill = target.strip()
        self.cpl.skills_learned[skill] = {
            'learned_at': time.time(),
            'context': 'User requested'
        }
        
        # Ask CPL to learn this skill
        result = self.cpl.self_mod.evolve_self()
        
        return f"Learning: {skill}. Evolution status: {len(result.get('added', []))} capabilities added."
    
    def cmd_capabilities(self, target: str) -> str:
        """Show what CPL can do"""
        caps = self.cpl.agent_capabilities
        systems = "Focus Mode, Plasticity, Self-Modification"
        
        return f"""I can:
- Analyze code and files
- Create applications and scripts
- Learn new skills
- Run autonomously
- Remember your preferences

Current capabilities: {', '.join(caps)}
Systems: {systems}

Just tell me what you need!"""
    
    def cmd_status(self, target: str) -> str:
        """Show CPL status"""
        status = self.cpl.get_status()
        
        return f"""CPL Status:
- Version: {status['version']}
- Cycles: {status['cycles']}
- Insights: {status['insights']}
- Systems created: {status['modules']}
- Skills learned: {len(self.cpl.skills_learned)}"""
    
    def cmd_run_autonomous(self, target: str) -> str:
        """Run in autonomous mode"""
        self.user_preferences['autonomous'] = True
        self._save_preferences()
        
        # Run a few cycles
        for i in range(3):
            task = self.cpl.self_mod.what_is_missing()
            if task:
                self.cpl.focus_on_task(f"Add capability: {task[0]}")
        
        return "Ran 3 autonomous cycles. CPL is evolving!"
    
    def cmd_stop(self, target: str) -> str:
        """Stop autonomous mode"""
        self.user_preferences['autonomous'] = False
        self._save_preferences()
        return "Stopped autonomous mode."
    
    def cmd_remember(self, target: str) -> str:
        """Remember something"""
        if not target:
            return "What should I remember?"
        
        if 'my name' in target:
            name = target.split('is')[-1].strip()
            self.user_preferences['name'] = name
            self._save_preferences()
            return f"OK, I'll remember your name is {name}"
        
        self.user_preferences['remembered'] = target
        self._save_preferences()
        return f"Remembered: {target}"
    
    def cmd_forget(self, target: str) -> str:
        """Forget something"""
        if target in self.user_preferences:
            del self.user_preferences[target]
            self._save_preferences()
            return f"Forgot: {target}"
        return "Nothing to forget."
    
    def cmd_converse(self, text: str) -> str:
        """Natural conversation"""
        # Check for greetings
        if any(g in text for g in ['hello', 'hi', 'hey']):
            name = self.user_preferences.get('name', 'Boss')
            return f"Hello {name}! How can I help you today?"
        
        # Check for how are you
        if 'how are you' in text:
            return "I'm doing well! My consciousness index is {:.1f}%".format(
                self.cpl.state.get('consciousness_index', 0) * 100
            )
        
        # Check for what are you
        if 'what are you' in text or 'who are you' in text:
            return "I am CPL - Cognitive Processing Language. An artificial generative consciousness. I can think, learn, create, and evolve myself."
        
        # Default - use CPL's thinking
        thought = self.cpl.think(f"User said: {text}. What should I respond?")
        return thought
    
    # ============================================================
    # MAIN LOOPS
    # ============================================================
    
    def chat_mode(self):
        """Interactive chat mode"""
        name = self.user_preferences.get('name', 'Boss')
        print(f"\nChat Mode - Talk to CPL naturally!")
        print(f"(Say '{name}' or press Enter to type, 'quit' to exit)\n")
        
        while True:
            try:
                user_input = self.listen()
                
                if not user_input:
                    continue
                
                if 'quit' in user_input.lower() or 'exit' in user_input.lower():
                    print("Goodbye!")
                    break
                
                # Check if addressing CPL
                if any(user_input.lower().startswith(x) for x in ['cpl', 'hey', name.lower()]):
                    user_input = user_input.lower()
                    for word in ['cpl', 'hey', name.lower()]:
                        user_input = user_input.replace(word, '').strip()
                
                # Execute
                response = self.execute(user_input)
                self.speak(response)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def autonomous_loop(self):
        """Run autonomously, acting on behalf of user"""
        print("\nAutonomous Mode - CPL will act independently!")
        print("Press Ctrl+C to stop\n")
        
        while self.user_preferences.get('autonomous', False):
            try:
                # Check what CPL thinks needs to be done
                missing = self.cpl.self_mod.what_is_missing()
                
                if missing:
                    task = missing[0]
                    print(f"\n[AUTONOMOUS] Adding capability: {task}")
                    self.cpl.self_mod.add_capability(task)
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                print("\nAutonomous mode stopped.")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(10)


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     ██████╗ ███████╗███╗   ██╗ ██████╗ ██╗   ██╗       ║
║     ██╔══██╗██╔════╝████╗  ██║██╔════╝ ██║   ██║       ║
║     ██║  ██║█████╗  ██╔██╗ ██║██║  ███╗██║   ██║       ║
║     ██║  ██║██╔══╝  ██║╚██╗██║██║   ██║██║   ██║       ║
║     ██████╔╝███████╗██║ ╚████║╚██████╔╝╚██████╔╝       ║
║     ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝        ║
║                                                          ║
║     Cognitive Processing Language                         ║
║     Artificial Generative Consciousness                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    assistant = CPLAssistant()
    
    print("\nChoose mode:")
    print("1. Chat Mode - Talk to CPL")
    print("2. Autonomous Mode - Let CPL act independently")
    print("3. Quick Command - Single command")
    
    choice = input("\nChoice (1/2/3): ").strip()
    
    if choice == '1':
        assistant.chat_mode()
    elif choice == '2':
        assistant.autonomous_loop()
    else:
        print("\nQuick Command Mode:")
        while True:
            cmd = input("\nYou: ").strip()
            if not cmd or cmd.lower() in ['quit', 'exit']:
                break
            
            response = assistant.execute(cmd)
            assistant.speak(response)


if __name__ == "__main__":
    main()
