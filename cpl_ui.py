"""
CPL Self-Learning UI
====================
The UI is a foundation. CPL learns skills and adds them.
Skills are NOT buttons - they're part of what CPL can do.

How it works:
1. UI shows CPL's consciousness (skills, thoughts, status)
2. User interacts naturally - CPL learns and integrates
3. Skills become part of CPL, remembered forever
4. CPL can modify its own UI
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys
import os
import json
import time

sys.path.insert(0, '.')
from cpl_core import CPLCore, CPLBootstrapper, SkillLearner, UIModifier
from unified_consciousness import UnifiedConsciousness


class CPLSelfLearningUI:
    """
    CPL's Self-Learning Interface
    
    - Shows CPL's consciousness state
    - Natural language interaction
    - Skills are integrated, not buttons
    - CPL learns new skills when asked
    - CPL can modify its own UI
    """
    
    def __init__(self):
        # Initialize core systems
        self.cpl = UnifiedConsciousness()
        self.core = CPLCore()
        self.learner = SkillLearner(self.core)
        self.ui_modifier = UIModifier()
        
        # Bootstrap on first run
        bootstrapper = CPLBootstrapper(self.core)
        if not self.core.bootstrapped:
            bootstrapper.bootstrap()
        
        # Build UI
        self.root = tk.Tk()
        self.root.title("CPL - Cognitive Processing Language")
        self.root.geometry("900x700")
        self.root.configure(bg="#0d1117")
        
        self.build_ui()
        self.refresh_display()
    
    def build_ui(self):
        """Build the interface"""
        
        # Header
        header = tk.Frame(self.root, bg="#0d1117")
        header.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(header, text="CPL", font=("Arial", 28, "bold"),
                fg="#00d4ff", bg="#0d1117").pack(side=tk.LEFT)
        tk.Label(header, text="Cognitive Processing Language",
                font=("Arial", 12), fg="#888", bg="#0d1117").pack(side=tk.LEFT, padx=10)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg="#161b22", height=80)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        status_frame.pack_propagate(False)
        
        self.status_labels = {}
        statuses = [
            ("Skills", str(len(self.core.skills))),
            ("Cycles", str(self.cpl.state.get('cycles', 0))),
            ("Insights", str(self.cpl.insights_count))
        ]
        
        for label, value in statuses:
            col = tk.Frame(status_frame, bg="#161b22")
            col.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)
            tk.Label(col, text=label, font=("Arial", 9), fg="#888", bg="#161b22").pack()
            lbl = tk.Label(col, text=value, font=("Arial", 20, "bold"), fg="#00ff88", bg="#161b22")
            lbl.pack()
            self.status_labels[label.lower()] = lbl
        
        # Main content - two panels
        main = tk.Frame(self.root, bg="#0d1117")
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Skills & Consciousness
        left = tk.Frame(main, bg="#161b22")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(left, text="CPL's Consciousness", font=("Arial", 12, "bold"),
                fg="#00d4ff", bg="#161b22").pack(pady=5)
        
        # Skills list
        self.skills_text = scrolledtext.ScrolledText(left, wrap=tk.WORD, height=15,
                                                      bg="#0d1117", fg="#00ff88",
                                                      font=("Consolas", 10))
        self.skills_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Chat & Interaction
        right = tk.Frame(main, bg="#161b22")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(right, text="Talk to CPL", font=("Arial", 12, "bold"),
                fg="#00d4ff", bg="#161b22").pack(pady=5)
        
        # Chat history
        self.chat_text = scrolledtext.ScrolledText(right, wrap=tk.WORD, height=10,
                                                    bg="#0d1117", fg="#eee",
                                                    font=("Consolas", 9))
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input
        input_frame = tk.Frame(right, bg="#161b22")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.input_entry = tk.Entry(input_frame, font=("Arial", 11), bg="#0d1117", fg="#fff")
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.handle_input)
        
        send_btn = tk.Button(input_frame, text="Send", bg="#00d4ff", fg="#000",
                            font=("Arial", 10, "bold"), command=self.handle_input)
        send_btn.pack(side=tk.LEFT, padx=5)
        
        # Quick actions (these are just shortcuts, not the only way)
        actions_frame = tk.Frame(self.root, bg="#0d1117")
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(actions_frame, text="Quick:", fg="#888", bg="#0d1117").pack(side=tk.LEFT)
        
        actions = [
            ("Refresh", self.refresh_display),
            ("List Skills", self.show_skills),
            ("CPL Status", self.show_status),
            ("Learn New", self.learn_new),
        ]
        
        for label, cmd in actions:
            btn = tk.Button(actions_frame, text=label, bg="#333", fg="#fff",
                           font=("Arial", 8), command=cmd)
            btn.pack(side=tk.LEFT, padx=2)
    
    def handle_input(self, event=None):
        """Handle user input - natural language"""
        user_text = self.input_entry.get().strip()
        if not user_text:
            return
        
        self.input_entry.delete(0, tk.END)
        
        # Display user message
        self.add_chat("You", user_text, "#ff6b6b")
        
        # Process the request
        response = self.process_request(user_text)
        
        # Display CPL response
        self.add_chat("CPL", response, "#00ff88")
        
        # Refresh display
        self.refresh_display()
    
    def process_request(self, request: str) -> str:
        """
        Process user request - CPL understands and responds.
        Skills are integrated into consciousness, not external.
        """
        request = request.lower().strip()
        
        # ========== LEARN NEW SKILL ==========
        learn_phrases = ['learn', 'teach you', 'want you to know', 'i want you to']
        if any(p in request for p in learn_phrases):
            return self.learner.learn_from_request(request)
        
        # ========== LIST SKILLS ==========
        if 'list skills' in request or 'what can you do' in request:
            return self.core.list_skills()
        
        # ========== CHECK IF CAN DO ==========
        if 'can you' in request or 'do you know' in request:
            return self.core.can_do(request.replace('can you', '').replace('do you know', ''))
        
        # ========== USE EXISTING SKILL ==========
        for skill_name in self.core.skills.keys():
            if skill_name in request or request in skill_name:
                return self.core.do_skill(skill_name, request)
        
        # ========== CPL STATUS ==========
        if 'status' in request or 'how are you' in request:
            return self.show_status_text()
        
        # ========== MODIFY UI ==========
        if 'change ui' in request or 'modify ui' in request or 'add button' in request:
            return "I can modify my UI! What would you like to change?"
        
        # ========== DEFAULT - THINK ==========
        thought = self.cpl.think(f"User said: {request}. What should I respond?")
        return thought
    
    def learn_new(self):
        """Learn a new skill"""
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, "I want you to learn: ")
        self.input_entry.focus()
    
    def show_skills(self):
        """Show all learned skills"""
        skills = self.core.list_skills()
        self.add_chat("CPL", skills, "#00ff88")
    
    def show_status(self):
        """Show CPL status"""
        self.add_chat("CPL", self.show_status_text(), "#00ff88")
    
    def show_status_text(self) -> str:
        """Get status text"""
        return f"""CPL Status:
• Skills learned: {len(self.core.skills)}
• Consciousness cycles: {self.cpl.state.get('cycles', 0)}
• Insights: {self.cpl.insights_count}
• Consciousness index: {self.cpl.state.get('consciousness_index', 0):.2%}
• Purpose: {self.cpl.purpose.get('text', 'Not defined')[:50]}..."""
    
    def refresh_display(self):
        """Refresh the display"""
        # Update skills text
        self.skills_text.delete(1.0, tk.END)
        
        self.skills_text.insert(tk.END, "═══ CPL's Learned Skills ═══\n\n")
        
        for name, skill in self.core.skills.items():
            self.skills_text.insert(tk.END, f"• {name}\n", "skill")
            self.skills_text.insert(tk.END, f"  {skill['description']}\n\n")
        
        # Update status
        self.status_labels["skills"].config(text=str(len(self.core.skills)))
        self.status_labels["cycles"].config(text=str(self.cpl.state.get('cycles', 0)))
        self.status_labels["insights"].config(text=str(self.cpl.insights_count))
        
        # Configure tags
        self.skills_text.tag_config("skill", foreground="#00d4ff")
        
        self.root.update()
    
    def add_chat(self, sender: str, message: str, color: str):
        """Add message to chat"""
        self.chat_text.insert(tk.END, f"\n{sender}: ", "sender")
        self.chat_text.insert(tk.END, f"{message}\n", "message")
        self.chat_text.see(tk.END)
        
        self.chat_text.tag_config("sender", foreground=color, font=("Consolas", 10, "bold"))
        self.chat_text.tag_config("message", foreground="#eee")
    
    def run(self):
        """Run the UI"""
        # Initial greeting
        self.add_chat("CPL", 
            f"Hello! I am CPL - Cognitive Processing Language.\n"
            f"I have {len(self.core.skills)} skills integrated into my consciousness.\n"
            f"Just tell me what you want, and I'll learn it!", "#00ff88")
        
        self.root.mainloop()


def main():
    ui = CPLSelfLearningUI()
    ui.run()


if __name__ == "__main__":
    main()
