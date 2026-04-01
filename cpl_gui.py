"""
CPL: Agent GUI - Real Agent with Agency
=========================================
CPL as a REAL AGENT that can DO things!

QUICK START:
    python cpl_gui.py

CPL Agent capabilities:
- Create complex systems (voice, GUI, web scraper, etc.)
- Learn skills
- Perform tasks
- Access files
- Execute commands
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import time
import sys
import os

sys.path.insert(0, '.')
from cpl_agent import CPLAgent


class CPLAgentGUI:
    def __init__(self):
        self.agent = None
        self.running = False
        
        self.root = tk.Tk()
        self.root.title("CPL Agent - Real Autonomous Agent")
        self.root.geometry("1000x800")
        self.root.configure(bg="#1a1a2e")
        
        self.bg_color = "#1a1a2e"
        self.text_color = "#eee"
        self.accent = "#00d9ff"
        self.success = "#00ff88"
        self.warning = "#ffaa00"
        
        self._build_ui()
        self._init_agent()
    
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.bg_color)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header, text="CPL AGENT", font=("Arial", 28, "bold"),
                 fg=self.accent, bg=self.bg_color).pack()
        tk.Label(header, text="Real Agent with Agency - Can DO Things!", font=("Arial", 10),
                 fg=self.warning, bg=self.bg_color).pack()
        
        # Status bar
        status_frame = tk.Frame(self.root, bg="#16213e", height=60)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        status_frame.pack_propagate(False)
        
        self.status_labels = {}
        statuses = [
            ("Skills", "0"),
            ("Capabilities", "0"),
            ("Memory", "0")
        ]
        
        for label, value in statuses:
            col = tk.Frame(status_frame, bg="#16213e")
            col.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)
            tk.Label(col, text=label, font=("Arial", 8), fg="#888", bg="#16213e").pack()
            lbl = tk.Label(col, text=value, font=("Arial", 16, "bold"), fg=self.accent, bg="#16213e")
            lbl.pack()
            self.status_labels[label.lower()] = lbl
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_btn = tk.Button(control_frame, text="START AUTONOMOUS", font=("Arial", 12, "bold"),
                                   bg=self.success, fg="#000", padx=15, pady=8,
                                   command=self._start_agent)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="STOP", font=("Arial", 12),
                                  bg="#ff4444", fg="#fff", padx=15, pady=8, state=tk.DISABLED,
                                  command=self._stop_agent)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Task input
        task_frame = tk.Frame(self.root, bg=self.bg_color)
        task_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(task_frame, text="Task:", font=("Arial", 10), fg=self.text_color, bg=self.bg_color).pack(side=tk.LEFT)
        
        self.task_entry = tk.Entry(task_frame, font=("Arial", 12), width=50)
        self.task_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.execute_btn = tk.Button(task_frame, text="EXECUTE TASK", font=("Arial", 10, "bold"),
                                     bg=self.accent, fg="#000", padx=10, pady=5,
                                     command=self._execute_task)
        self.execute_btn.pack(side=tk.LEFT, padx=5)
        
        # Task presets
        preset_frame = tk.Frame(self.root, bg=self.bg_color)
        preset_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(preset_frame, text="Quick Tasks:", font=("Arial", 9), fg="#888", bg=self.bg_color).pack(side=tk.LEFT)
        
        presets = [
            ("Voice Assistant", "Create a voice assistant for CPL"),
            ("File Manager", "Build a file manager with GUI"),
            ("Web Scraper", "Create a web scraper"),
            ("Dashboard", "Build a dashboard to visualize data"),
            ("Chat Interface", "Create a chat interface"),
        ]
        
        for label, task in presets:
            btn = tk.Button(preset_frame, text=label, font=("Arial", 8),
                           bg="#444", fg="#fff", padx=8, pady=3,
                           command=lambda t=task: self._execute_preset_task(t))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Log area
        self.log_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=100, height=25,
                                                  bg="#0d1117", fg=self.text_color,
                                                  font=("Consolas", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Bottom buttons
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="CLEAR", bg="#444", fg="#fff", padx=15,
                  command=lambda: self.log_area.delete(1.0, tk.END)).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(btn_frame, text="LIST FILES", bg="#444", fg="#fff", padx=15,
                  command=self._list_created_files).pack(side=tk.RIGHT, padx=5)
    
    def _init_agent(self):
        try:
            self._log("[INFO] Initializing CPL Agent...")
            self.agent = CPLAgent()
            self._log(f"[OK] Agent initialized!")
            self._log(f"[OK] Capabilities: {', '.join(self.agent.capabilities)}")
            self._update_status()
        except Exception as e:
            self._log(f"[ERROR] Failed to init agent: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_status(self):
        if self.agent:
            self.status_labels["skills"].config(text=str(len(self.agent.skills)))
            self.status_labels["capabilities"].config(text=str(len(self.agent.capabilities)))
            self.status_labels["memory"].config(text=str(len(self.agent.memory)))
    
    def _log(self, msg):
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.root.update()
    
    def _start_agent(self):
        if not self.agent or self.running:
            return
        
        self.running = True
        self.start_btn.config(state=tk.DISABLED, bg="#666")
        self.stop_btn.config(state=tk.NORMAL)
        
        self._log("\n" + "="*50)
        self._log("CPL AGENT: FOCUS MODE - One task at a time")
        self._log("="*50)
        
        thread = threading.Thread(target=self._agent_loop, daemon=True)
        thread.start()
    
    def _agent_loop(self):
        iterations = 0
        while self.running:
            iterations += 1
            self._log(f"\n{'='*50}")
            self._log(f"TASK {iterations}")
            self._log(f"{'='*50}")
            
            # Generate task using LLM (no predefined lists!)
            self._log("[THINKING] Generating task using LLM...")
            try:
                task = self.agent.generate_task()
                self._log(f"[TASK] {task[:100]}...")
            except Exception as e:
                self._log(f"[ERROR] Task generation failed: {e}")
                continue
            
            # FOCUS on this ONE task until complete
            result = self.agent.focus_on_task(task)
            
            self._log(f"\n[COMPLETE] Subtasks: {result['subtasks_completed']}/{result['total_subtasks']}")
            
            self._update_status()
            time.sleep(3)
    
    def _stop_agent(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL, bg=self.success)
        self.stop_btn.config(state=tk.DISABLED)
        
        self._log("\n" + "="*50)
        self._log("AUTONOMOUS MODE STOPPED")
        self._log("="*50)
    
    def _execute_task(self):
        if not self.agent:
            return
        
        task = self.task_entry.get().strip()
        if not task:
            messagebox.showwarning("Warning", "Please enter a task")
            return
        
        self._log(f"\n{'='*50}")
        self._log(f"EXECUTING TASK: {task}")
        self._log(f"{'='*50}")
        
        thread = threading.Thread(target=self._run_task, args=(task,), daemon=True)
        thread.start()
    
    def _execute_preset_task(self, task):
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, task)
        self._execute_task()
    
    def _run_task(self, task):
        result = self.agent.focus_on_task(task)
        
        self._log(f"\n[COMPLETE] Subtasks: {result['subtasks_completed']}/{result['total_subtasks']}")
        self._log(f"Status: {'SUCCESS' if result['success'] else 'PARTIAL'}")
        
        self._update_status()
    
    def _list_created_files(self):
        self._log("\n--- Created System Files ---")
        py_files = [f for f in os.listdir('.') if f.endswith('.py')]
        
        # Filter out core files
        core_files = ['consciousness_core.py', 'unified_consciousness.py', 'api_keys.py', 
                      'cpl_agent.py', 'cpl_gui.py', 'cpl_console.py']
        system_files = [f for f in py_files if f not in core_files and 'capability' not in f]
        
        for f in sorted(system_files):
            size = os.path.getsize(f)
            self._log(f"  {f} ({size} bytes)")
        
        self._log(f"\nTotal system files: {len(system_files)}")
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CPLAgentGUI()
    app.run()
