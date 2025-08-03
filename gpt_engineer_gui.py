#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT Engineer GUI - Advanced User-Friendly Interface
A comprehensive graphical interface for running GPT Engineer with full feature support
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
import os
import subprocess
import threading
from pathlib import Path
import sys
import json
import webbrowser
from datetime import datetime
import shutil

class GPTEngineerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GPT Engineer v0.3.1 - Advanced Code Generation")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        self.root.minsize(800, 600)
        
        # Set up UTF-8 environment
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'
        
        # Enhanced Variables
        self.project_path = tk.StringVar()
        self.api_key = tk.StringVar()
        self.model_choice = tk.StringVar(value="gemini-2.0-flash")
        self.prompt_text = tk.StringVar()
        self.generation_mode = tk.StringVar(value="new")
        self.language_choice = tk.StringVar(value="auto")
        self.framework_choice = tk.StringVar(value="auto")
        self.advanced_options = tk.BooleanVar(value=False)
        self.auto_extract = tk.BooleanVar(value=True)
        self.auto_open = tk.BooleanVar(value=False)
        
        # Recent projects list
        self.recent_projects = []
        self.load_recent_projects()
        
        # Available languages from GPT Engineer
        self.supported_languages = [
            "auto", "Python", "JavaScript", "TypeScript", "HTML", "CSS", 
            "Java", "C#", "Ruby", "PHP", "Go", "Rust", "C++", "C", "Swift", "Kotlin"
        ]
        
        # Popular frameworks
        self.frameworks = {
            "auto": ["auto"],
            "Python": ["auto", "Django", "Flask", "FastAPI", "Streamlit", "Tkinter", "PyQt"],
            "JavaScript": ["auto", "React", "Vue.js", "Angular", "Node.js", "Express", "Next.js"],
            "TypeScript": ["auto", "React", "Angular", "Vue.js", "Node.js", "NestJS", "Next.js"],
            "HTML": ["auto", "Bootstrap", "Tailwind CSS", "Foundation"],
            "CSS": ["auto", "Bootstrap", "Tailwind CSS", "SCSS", "LESS"],
            "Java": ["auto", "Spring Boot", "Spring MVC", "Hibernate", "Maven", "Gradle"],
            "C#": ["auto", ".NET", "ASP.NET", "Entity Framework", "Blazor", "MAUI"],
            "Ruby": ["auto", "Rails", "Sinatra", "Jekyll"],
            "PHP": ["auto", "Laravel", "Symfony", "CodeIgniter", "WordPress"],
            "Go": ["auto", "Gin", "Echo", "Fiber", "Gorilla"],
            "Rust": ["auto", "Actix", "Rocket", "Warp", "Tokio"],
        }
        
        self.setup_ui()
        self.load_env()
        self.update_framework_options()
        
    def setup_ui(self):
        """Create the enhanced user interface"""
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="🚀 Generate Code")
        
        # Settings tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        
        # History tab
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="📜 History")
        
        # Help tab
        self.help_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.help_tab, text="❓ Help")
        
        self.setup_main_tab()
        self.setup_settings_tab()
        self.setup_history_tab()
        self.setup_help_tab()
        
    def setup_main_tab(self):
        """Setup the main generation tab"""
        # Main frame with scrollable content
        main_canvas = tk.Canvas(self.main_tab)
        main_scrollbar = ttk.Scrollbar(self.main_tab, orient="vertical", command=main_canvas.yview)
        main_frame = ttk.Frame(main_canvas)
        
        main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title Section
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 20))
        title_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(title_frame, text="🤖 GPT Engineer v0.3.1", font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0)
        
        subtitle_label = ttk.Label(title_frame, text="Transform ideas into working code with AI", 
                                 font=("Arial", 12), foreground="gray")
        subtitle_label.grid(row=1, column=0, pady=(5, 0))
        
        row += 1
        
        # Quick Start Section
        quick_frame = ttk.LabelFrame(main_frame, text="🚀 Quick Start", padding="10")
        quick_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        quick_frame.columnconfigure(1, weight=1)
        
        # Recent projects dropdown
        ttk.Label(quick_frame, text="Recent:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.recent_combo = ttk.Combobox(quick_frame, values=self.recent_projects, state="readonly", width=40)
        self.recent_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.recent_combo.bind("<<ComboboxSelected>>", self.load_recent_project)
        
        ttk.Button(quick_frame, text="📂 Load", command=self.load_recent_project, width=8).grid(row=0, column=2)
        
        # Templates
        ttk.Label(quick_frame, text="Templates:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        template_frame = ttk.Frame(quick_frame)
        template_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        templates = [
            ("🌐 Web App", "Create a modern web application with user authentication, database, and responsive design"),
            ("📱 Mobile App", "Build a cross-platform mobile application with native features"),
            ("🔌 API", "Develop a RESTful API with database integration and documentation"),
            ("🎮 Game", "Create an interactive game with graphics and user controls")
        ]
        
        for i, (name, prompt) in enumerate(templates):
            btn = ttk.Button(template_frame, text=name, 
                           command=lambda p=prompt: self.use_template(p), width=12)
            btn.grid(row=0, column=i, padx=2)
        
        row += 1
        
        # Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configuration", padding="10")
        config_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        config_frame.columnconfigure(1, weight=1)
        
        config_row = 0
        
        # API Key
        ttk.Label(config_frame, text="🔑 API Key:", font=("Arial", 10, "bold")).grid(row=config_row, column=0, sticky=tk.W, pady=5)
        api_frame = ttk.Frame(config_frame)
        api_frame.grid(row=config_row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        api_frame.columnconfigure(0, weight=1)
        
        self.api_entry = ttk.Entry(api_frame, textvariable=self.api_key, show="*")
        self.api_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(api_frame, text="💾", command=self.save_api_key, width=3).grid(row=0, column=1)
        ttk.Button(api_frame, text="�", command=self.toggle_api_visibility, width=3).grid(row=0, column=2, padx=(2, 0))
        ttk.Button(api_frame, text="🔗", command=self.open_api_help, width=3).grid(row=0, column=3, padx=(2, 0))
        
        config_row += 1
        
        # Model and Language selection
        ttk.Label(config_frame, text="🤖 Model:", font=("Arial", 10, "bold")).grid(row=config_row, column=0, sticky=tk.W, pady=5)
        model_combo = ttk.Combobox(config_frame, textvariable=self.model_choice, 
                                  values=["gemini-2.0-flash", "gemini-pro", "gemini-1.5-pro", "gpt-4", "gpt-3.5-turbo"], 
                                  state="readonly", width=20)
        model_combo.grid(row=config_row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(config_frame, text="🔤 Language:", font=("Arial", 10, "bold")).grid(row=config_row, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.language_combo = ttk.Combobox(config_frame, textvariable=self.language_choice, 
                                          values=self.supported_languages, state="readonly", width=15)
        self.language_combo.grid(row=config_row, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        self.language_combo.bind("<<ComboboxSelected>>", lambda e: self.update_framework_options())
        
        config_row += 1
        
        # Framework and Generation Mode
        ttk.Label(config_frame, text="🛠️ Framework:", font=("Arial", 10, "bold")).grid(row=config_row, column=0, sticky=tk.W, pady=5)
        self.framework_combo = ttk.Combobox(config_frame, textvariable=self.framework_choice, 
                                           state="readonly", width=20)
        self.framework_combo.grid(row=config_row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(config_frame, text="⚙️ Mode:", font=("Arial", 10, "bold")).grid(row=config_row, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        mode_frame = ttk.Frame(config_frame)
        mode_frame.grid(row=config_row, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        ttk.Radiobutton(mode_frame, text="New", variable=self.generation_mode, value="new").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Improve", variable=self.generation_mode, value="improve").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(mode_frame, text="Lite", variable=self.generation_mode, value="lite").pack(side=tk.LEFT, padx=(10, 0))
        
        config_row += 1
        
        # Project Path Section
        ttk.Label(config_frame, text="📁 Project:", font=("Arial", 10, "bold")).grid(row=config_row, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(config_frame)
        path_frame.grid(row=config_row, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        path_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(path_frame, textvariable=self.project_path).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(path_frame, text="📂", command=self.browse_folder, width=3).grid(row=0, column=1)
        ttk.Button(path_frame, text="➕", command=self.create_new_project, width=3).grid(row=0, column=2, padx=(2, 0))
        ttk.Button(path_frame, text="🔍", command=self.open_project_folder, width=3).grid(row=0, column=3, padx=(2, 0))
        
        row += 1
        
        # Advanced Options
        advanced_frame = ttk.Frame(main_frame)
        advanced_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Checkbutton(advanced_frame, text="🔧 Advanced Options", 
                       variable=self.advanced_options, command=self.toggle_advanced).pack(side=tk.LEFT)
        ttk.Checkbutton(advanced_frame, text="📤 Auto Extract Files", 
                       variable=self.auto_extract).pack(side=tk.LEFT, padx=(20, 0))
        ttk.Checkbutton(advanced_frame, text="📂 Auto Open Folder", 
                       variable=self.auto_open).pack(side=tk.LEFT, padx=(20, 0))
        
        row += 1
        
        # Advanced options frame (initially hidden)
        self.advanced_panel = ttk.LabelFrame(main_frame, text="🔧 Advanced Settings", padding="10")
        self.advanced_panel.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        self.advanced_panel.grid_remove()  # Hide initially
        
        # Add advanced options here
        ttk.Label(self.advanced_panel, text="Coming soon: Custom templates, batch processing, CI/CD integration", 
                 foreground="gray").pack()
        
        row += 1
        
        # Prompt Section
        prompt_frame = ttk.LabelFrame(main_frame, text="✍️ Project Description", padding="10")
        prompt_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        prompt_frame.columnconfigure(0, weight=1)
        prompt_frame.rowconfigure(1, weight=1)
        
        # Prompt toolbar
        prompt_toolbar = ttk.Frame(prompt_frame)
        prompt_toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(prompt_toolbar, text="📋 Load", command=self.load_prompt_file, width=8).pack(side=tk.LEFT)
        ttk.Button(prompt_toolbar, text="💾 Save", command=self.save_prompt_file, width=8).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(prompt_toolbar, text="🗑️ Clear", command=self.clear_prompt, width=8).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(prompt_toolbar, text="🎯 Examples", command=self.show_examples, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Character count
        self.char_count_label = ttk.Label(prompt_toolbar, text="0 characters", foreground="gray")
        self.char_count_label.pack(side=tk.RIGHT)
        
        # Prompt text area
        self.prompt_entry = scrolledtext.ScrolledText(prompt_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.prompt_entry.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.prompt_entry.bind("<KeyRelease>", self.update_char_count)
        
        row += 1
        
        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        self.generate_btn = ttk.Button(button_frame, text="🚀 Generate Code", 
                                     command=self.generate_code, style="Accent.TButton")
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop", 
                                  command=self.stop_generation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📊 Analyze", command=self.analyze_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🌐 Preview", command=self.preview_project).pack(side=tk.LEFT, padx=5)
        
        row += 1
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        row += 1
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="📄 Generation Output", padding="10")
        output_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)
        
        # Output toolbar
        output_toolbar = ttk.Frame(output_frame)
        output_toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(output_toolbar, text="📋 Copy", command=self.copy_output, width=8).pack(side=tk.LEFT)
        ttk.Button(output_toolbar, text="💾 Save Log", command=self.save_output, width=10).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(output_toolbar, text="🗑️ Clear", command=self.clear_output, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Status label
        self.status_label = ttk.Label(output_toolbar, text="Ready", foreground="green")
        self.status_label.pack(side=tk.RIGHT)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(output_frame, height=12, state=tk.DISABLED, 
                                                    font=("Consolas", 9))
        self.output_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure tags for colored output
        self.output_text.tag_configure("success", foreground="green")
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.tag_configure("warning", foreground="orange")
        self.output_text.tag_configure("info", foreground="blue")
        
        # Configure grid weights for main frame
        main_frame.rowconfigure(row, weight=1)
        examples_frame = ttk.LabelFrame(main_frame, text="💡 Example Prompts", padding="5")
        examples_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        examples_frame.columnconfigure(0, weight=1)
        
        examples = [
            "Create a todo app with React and TypeScript",
            "Build a REST API with Python Flask and SQLite",
            "Make a simple calculator with HTML, CSS, and JavaScript",
            "Create a blog website with Node.js and Express"
        ]
        
        for i, example in enumerate(examples):
            btn = ttk.Button(examples_frame, text=example, 
                           command=lambda ex=example: self.use_example(ex))
            btn.grid(row=i//2, column=i%2, sticky=(tk.W, tk.E), padx=2, pady=2)
            examples_frame.columnconfigure(i%2, weight=1)
        
        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=20)
        
        self.generate_btn = ttk.Button(button_frame, text="🚀 Generate Code", 
                                     command=self.generate_code, style="Accent.TButton")
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📋 Load Prompt", command=self.load_prompt_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Save Prompt", command=self.save_prompt_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔧 Settings", command=self.open_settings).pack(side=tk.LEFT, padx=5)
        
        # Output Section
        ttk.Label(main_frame, text="📄 Output:", font=("Arial", 10, "bold")).grid(row=10, column=0, sticky=tk.W, pady=(10, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10, state=tk.DISABLED)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(7, weight=1)
        main_frame.rowconfigure(11, weight=1)
        
    def load_recent_projects(self):
        """Load recent projects from config file"""
        try:
            config_file = Path(__file__).parent / ".gpt_engineer_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.recent_projects = config.get('recent_projects', [])
        except Exception:
            self.recent_projects = []
    
    def save_recent_projects(self):
        """Save recent projects to config file"""
        try:
            config_file = Path(__file__).parent / ".gpt_engineer_config.json"
            config = {
                'recent_projects': self.recent_projects[:10]  # Keep only last 10
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass
    
    def add_recent_project(self, project_path):
        """Add project to recent list"""
        if project_path in self.recent_projects:
            self.recent_projects.remove(project_path)
        self.recent_projects.insert(0, project_path)
        self.recent_projects = self.recent_projects[:10]  # Keep only last 10
        self.save_recent_projects()
        if hasattr(self, 'recent_combo'):
            self.recent_combo.configure(values=self.recent_projects)
    
    def load_recent_project(self, event=None):
        """Load a recent project"""
        project = self.recent_combo.get()
        if project and Path(project).exists():
            self.project_path.set(project)
    
    def update_framework_options(self):
        """Update framework options based on selected language"""
        language = self.language_choice.get()
        if hasattr(self, 'framework_combo'):
            frameworks = self.frameworks.get(language, ["auto"])
            self.framework_combo.configure(values=frameworks)
            self.framework_choice.set(frameworks[0])
    
    def use_template(self, prompt):
        """Use a template prompt"""
        self.prompt_entry.delete(1.0, tk.END)
        self.prompt_entry.insert(1.0, prompt)
        self.update_char_count()
    
    def toggle_api_visibility(self):
        """Toggle API key visibility"""
        if self.api_entry.cget('show') == '*':
            self.api_entry.configure(show='')
        else:
            self.api_entry.configure(show='*')
    
    def open_api_help(self):
        """Open API key help"""
        messagebox.showinfo("API Key Help", 
                           "Get your API key:\n\n" +
                           "• Gemini: https://aistudio.google.com/app/apikey\n" +
                           "• OpenAI: https://platform.openai.com/api-keys\n\n" +
                           "The API key will be saved securely in your .env file.")
    
    def toggle_advanced(self):
        """Toggle advanced options panel"""
        if self.advanced_options.get():
            self.advanced_panel.grid()
        else:
            self.advanced_panel.grid_remove()
    
    def open_project_folder(self):
        """Open project folder in file explorer"""
        path = self.project_path.get()
        if path and Path(path).exists():
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
    
    def clear_prompt(self):
        """Clear the prompt text"""
        self.prompt_entry.delete(1.0, tk.END)
        self.update_char_count()
    
    def show_examples(self):
        """Show example prompts window"""
        examples_window = tk.Toplevel(self.root)
        examples_window.title("Example Prompts")
        examples_window.geometry("600x400")
        examples_window.transient(self.root)
        examples_window.grab_set()
        
        # Create listbox with examples
        examples = [
            "Create a React e-commerce website with product catalog, shopping cart, and checkout",
            "Build a Python Flask REST API with user authentication and database integration",
            "Make a Vue.js dashboard with charts, data tables, and real-time updates",
            "Create a Node.js Express backend with JWT authentication and MongoDB",
            "Build a Django web application with user registration and blog functionality",
            "Make a React Native mobile app with navigation and local storage",
            "Create a Python data analysis script with pandas and matplotlib",
            "Build a JavaScript game using HTML5 Canvas and collision detection",
            "Make a Ruby on Rails CMS with admin panel and content management",
            "Create a C# Windows Forms application with database connectivity"
        ]
        
        listbox = tk.Listbox(examples_window, font=("Arial", 10))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for example in examples:
            listbox.insert(tk.END, example)
        
        def use_selected():
            selection = listbox.curselection()
            if selection:
                selected_example = listbox.get(selection[0])
                self.prompt_entry.delete(1.0, tk.END)
                self.prompt_entry.insert(1.0, selected_example)
                self.update_char_count()
                examples_window.destroy()
        
        button_frame = ttk.Frame(examples_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Use Selected", command=use_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=examples_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def update_char_count(self, event=None):
        """Update character count display"""
        if hasattr(self, 'char_count_label'):
            text = self.prompt_entry.get(1.0, tk.END)
            count = len(text.strip())
            self.char_count_label.configure(text=f"{count} characters")
    
    def stop_generation(self):
        """Stop the current generation process"""
        # This would require implementing process termination
        self.log_output("⏹️ Generation stopped by user", "warning")
        self.generate_btn.configure(state=tk.NORMAL, text="🚀 Generate Code")
        self.stop_btn.configure(state=tk.DISABLED)
        self.progress.stop()
        self.status_label.configure(text="Stopped", foreground="orange")
    
    def analyze_project(self):
        """Analyze the generated project"""
        path = self.project_path.get()
        if not path or not Path(path).exists():
            messagebox.showerror("Error", "Please select a valid project folder")
            return
        
        try:
            # Count files by type
            file_counts = {}
            total_files = 0
            total_size = 0
            
            for file_path in Path(path).rglob("*"):
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
                    ext = file_path.suffix.lower()
                    file_counts[ext] = file_counts.get(ext, 0) + 1
            
            # Show analysis
            analysis = f"📊 Project Analysis\n\n"
            analysis += f"📁 Folder: {path}\n"
            analysis += f"📄 Total Files: {total_files}\n"
            analysis += f"💾 Total Size: {total_size / 1024:.1f} KB\n\n"
            analysis += "📋 File Types:\n"
            
            for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True):
                if ext:
                    analysis += f"  {ext}: {count} files\n"
            
            messagebox.showinfo("Project Analysis", analysis)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze project: {e}")
    
    def preview_project(self):
        """Preview the generated project (if it's a web project)"""
        path = self.project_path.get()
        if not path or not Path(path).exists():
            messagebox.showerror("Error", "Please select a valid project folder")
            return
        
        # Look for common web files
        web_files = ["index.html", "app.html", "main.html", "home.html"]
        found_file = None
        
        for web_file in web_files:
            file_path = Path(path) / web_file
            if file_path.exists():
                found_file = file_path
                break
        
        if found_file:
            webbrowser.open(f"file://{found_file.absolute()}")
        else:
            messagebox.showinfo("Preview", "No web files found. This feature works best with HTML/web projects.")
    
    def copy_output(self):
        """Copy output text to clipboard"""
        try:
            text = self.output_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.log_output("📋 Output copied to clipboard", "info")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {e}")
    
    def save_output(self):
        """Save output to file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Output Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_text.get(1.0, tk.END))
                self.log_output(f"💾 Output saved to {file_path}", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def clear_output(self):
        """Clear the output text"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def setup_settings_tab(self):
        """Setup the settings tab"""
        settings_frame = ttk.Frame(self.settings_tab, padding="20")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(settings_frame, text="⚙️ Settings", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # API Configuration
        api_group = ttk.LabelFrame(settings_frame, text="API Configuration", padding="10")
        api_group.pack(fill=tk.X, pady=10)
        
        ttk.Label(api_group, text="Settings will be saved automatically and persisted between sessions.").pack()
        
        # Generation Settings
        gen_group = ttk.LabelFrame(settings_frame, text="Generation Settings", padding="10")
        gen_group.pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(gen_group, text="Auto-extract generated files", 
                       variable=self.auto_extract).pack(anchor=tk.W)
        ttk.Checkbutton(gen_group, text="Auto-open project folder after generation", 
                       variable=self.auto_open).pack(anchor=tk.W)
        
        # Reset button
        ttk.Button(settings_frame, text="🔄 Reset to Defaults", 
                  command=self.reset_settings).pack(pady=20)
    
    def setup_history_tab(self):
        """Setup the history tab"""
        history_frame = ttk.Frame(self.history_tab, padding="20")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(history_frame, text="📜 Generation History", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # History will be implemented here
        ttk.Label(history_frame, text="Generation history will be displayed here.\nComing in future update!", 
                 foreground="gray").pack()
    
    def setup_help_tab(self):
        """Setup the help tab"""
        help_frame = ttk.Frame(self.help_tab, padding="20")
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(help_frame, text="❓ Help & Documentation", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        help_text = """
🚀 Quick Start Guide:

1. 🔑 Enter your API Key (Gemini or OpenAI)
2. 📁 Select or create a project folder
3. ✍️ Describe what you want to build
4. 🚀 Click "Generate Code"
5. ⏳ Wait for completion
6. 📂 Check your project folder for generated files

💡 Tips for Better Results:

• Be specific about technologies and frameworks
• Include UI/UX requirements
• Mention specific features you need
• Provide example data or use cases
• Break complex projects into smaller parts

🔗 Useful Links:

• Gemini API: https://aistudio.google.com/app/apikey
• OpenAI API: https://platform.openai.com/api-keys
• Documentation: https://gpt-engineer.readthedocs.io/
• GitHub: https://github.com/gpt-engineer-org/gpt-engineer

⚠️ Troubleshooting:

• Check your internet connection
• Verify API key is correct and active
• Try a simpler prompt first
• Check the output area for error messages
"""
        
        help_text_widget = scrolledtext.ScrolledText(help_frame, height=20, wrap=tk.WORD, 
                                                    font=("Arial", 10))
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(1.0, help_text)
        help_text_widget.config(state=tk.DISABLED)
    
    def reset_settings(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.model_choice.set("gemini-2.0-flash")
            self.language_choice.set("auto")
            self.framework_choice.set("auto")
            self.generation_mode.set("new")
            self.advanced_options.set(False)
            self.auto_extract.set(True)
            self.auto_open.set(False)
            self.toggle_advanced()
    def load_env(self):
        """Load API key from .env file"""
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('GOOGLE_API_KEY=') or line.startswith('GEMINI_API_KEY='):
                            key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            if key and not key.startswith('your-'):
                                self.api_key.set(key)
                                break
            except Exception:
                pass
    
    def save_api_key(self):
        """Save API key to .env file"""
        if not self.api_key.get():
            messagebox.showerror("Error", "Please enter an API key")
            return
        
        try:
            env_file = Path(__file__).parent / ".env"
            content = f"GOOGLE_API_KEY={self.api_key.get()}\nGEMINI_API_KEY={self.api_key.get()}\n"
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("Success", "API key saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {e}")
    
    def browse_folder(self):
        """Browse for project folder"""
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.project_path.set(folder)
            self.add_recent_project(folder)
    
    def create_new_project(self):
        """Create a new project folder"""
        folder = filedialog.askdirectory(title="Select Parent Directory for New Project")
        if folder:
            project_name = simpledialog.askstring("Project Name", "Enter project name:")
            if project_name:
                new_path = Path(folder) / project_name
                new_path.mkdir(exist_ok=True)
                project_path = str(new_path)
                self.project_path.set(project_path)
                self.add_recent_project(project_path)
    
    def load_prompt_file(self):
        """Load prompt from file"""
        file_path = filedialog.askopenfilename(
            title="Load Prompt File",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.prompt_entry.delete(1.0, tk.END)
                self.prompt_entry.insert(1.0, content)
                self.update_char_count()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def save_prompt_file(self):
        """Save prompt to file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Prompt File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.prompt_entry.get(1.0, tk.END))
                messagebox.showinfo("Success", "Prompt saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def log_output(self, text, tag="normal"):
        """Add text to output log with optional tag for coloring"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_text = f"[{timestamp}] {text}\n"
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, formatted_text, tag)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.root.update()
    
    def generate_code(self):
        """Generate code using GPT Engineer with enhanced features"""
        # Validation
        if not self.api_key.get():
            messagebox.showerror("Error", "Please enter your API key")
            return
        
        if not self.project_path.get():
            messagebox.showerror("Error", "Please select a project folder")
            return
        
        prompt_text = self.prompt_entry.get(1.0, tk.END).strip()
        if not prompt_text:
            messagebox.showerror("Error", "Please enter a description of what you want to build")
            return
        
        # Save prompt to project folder
        try:
            project_dir = Path(self.project_path.get())
            project_dir.mkdir(exist_ok=True)
            
            # Create enhanced prompt with language/framework info
            enhanced_prompt = prompt_text
            if self.language_choice.get() != "auto":
                enhanced_prompt += f"\n\nUse {self.language_choice.get()} as the primary programming language."
            if self.framework_choice.get() != "auto":
                enhanced_prompt += f"\nUse {self.framework_choice.get()} framework."
            
            prompt_file = project_dir / "prompt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_prompt)
            
            # Add to recent projects
            self.add_recent_project(str(project_dir))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project folder: {e}")
            return
        
        # Update UI
        self.generate_btn.config(state=tk.DISABLED, text="🔄 Generating...")
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()
        self.status_label.configure(text="Generating...", foreground="blue")
        
        # Clear output
        self.clear_output()
        
        # Run generation in a separate thread
        thread = threading.Thread(target=self.run_generation)
        thread.daemon = True
        thread.start()
    
    def run_generation(self):
        """Run GPT Engineer generation with enhanced logging"""
        try:
            self.log_output("🚀 Starting GPT Engineer v0.3.1...", "info")
            self.log_output(f"📁 Project: {self.project_path.get()}", "info")
            self.log_output(f"🤖 Model: {self.model_choice.get()}", "info")
            self.log_output(f"⚙️ Mode: {self.generation_mode.get()}", "info")
            self.log_output(f"🔤 Language: {self.language_choice.get()}", "info")
            self.log_output(f"🛠️ Framework: {self.framework_choice.get()}", "info")
            self.log_output("", "normal")
            
            # Set up environment
            env = os.environ.copy()
            env.update({
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONUTF8': '1',
                'GRPC_VERBOSITY': 'ERROR',
                'GOOGLE_API_KEY': self.api_key.get(),
                'GEMINI_API_KEY': self.api_key.get(),
                'OPENAI_API_KEY': self.api_key.get()
            })
            
            # Build command
            cmd = [
                sys.executable, 'run_simple.py',
                self.project_path.get()
            ]
            
            # Add mode flags
            if self.generation_mode.get() == "improve":
                cmd.append("--improve")
            elif self.generation_mode.get() == "lite":
                cmd.append("--lite")
            
            self.log_output(f"🔧 Command: {' '.join(cmd)}", "info")
            self.log_output("", "normal")
            
            # Run command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                env=env,
                cwd=Path(__file__).parent
            )
            
            # Stream output
            for line in process.stdout:
                self.log_output(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log_output("", "normal")
                self.log_output("✅ Generation completed successfully!", "success")
                self.log_output("📁 Check your project folder for generated files", "success")
                self.status_label.configure(text="Completed", foreground="green")
                
                # Auto-extract files if enabled
                if self.auto_extract.get():
                    self.extract_files()
                
                # Auto-open folder if enabled
                if self.auto_open.get():
                    self.open_project_folder()
                    
            else:
                self.log_output("❌ Generation failed", "error")
                self.status_label.configure(text="Failed", foreground="red")
                
        except Exception as e:
            self.log_output(f"❌ Error: {e}", "error")
            self.status_label.configure(text="Error", foreground="red")
        
        finally:
            # Re-enable generate button
            self.generate_btn.config(state=tk.NORMAL, text="🚀 Generate Code")
            self.stop_btn.config(state=tk.DISABLED)
            self.progress.stop()
    
    def extract_files(self):
        """Extract generated files from logs"""
        try:
            self.log_output("🔍 Extracting generated files...", "info")
            
            # Run extraction script
            cmd = [sys.executable, 'extract_files.py']
            process = subprocess.run(cmd, capture_output=True, text=True, 
                                   cwd=Path(__file__).parent)
            
            if process.returncode == 0:
                self.log_output("✅ Files extracted successfully!", "success")
            else:
                self.log_output("❌ File extraction failed", "error")
                if process.stderr:
                    self.log_output(f"Error details: {process.stderr}", "error")
                
        except Exception as e:
            self.log_output(f"❌ Extraction error: {e}", "error")
    
    def save_api_key(self):
        """Save API key to .env file"""
        if not self.api_key.get():
            messagebox.showerror("Error", "Please enter an API key")
            return
        
        try:
            env_file = Path(__file__).parent / ".env"
            content = f"GOOGLE_API_KEY={self.api_key.get()}\nGEMINI_API_KEY={self.api_key.get()}\n"
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("Success", "API key saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {e}")
    
    def browse_folder(self):
        """Browse for project folder"""
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.project_path.set(folder)
    
    def create_new_project(self):
        """Create a new project folder"""
        folder = filedialog.askdirectory(title="Select Parent Directory for New Project")
        if folder:
            project_name = tk.simpledialog.askstring("Project Name", "Enter project name:")
            if project_name:
                new_path = Path(folder) / project_name
                new_path.mkdir(exist_ok=True)
                self.project_path.set(str(new_path))
    
    def use_example(self, example):
        """Use an example prompt"""
        self.prompt_entry.delete(1.0, tk.END)
        self.prompt_entry.insert(1.0, example)
    
    def load_prompt_file(self):
        """Load prompt from file"""
        file_path = filedialog.askopenfilename(
            title="Load Prompt File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.prompt_entry.delete(1.0, tk.END)
                self.prompt_entry.insert(1.0, content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def save_prompt_file(self):
        """Save prompt to file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Prompt File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.prompt_entry.get(1.0, tk.END))
                messagebox.showinfo("Success", "Prompt saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        ttk.Label(settings_window, text="⚙️ GPT Engineer Settings", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Add settings here (timeout, advanced options, etc.)
        ttk.Label(settings_window, text="More settings coming soon...").pack(pady=20)
        
        ttk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=10)
    
    def log_output(self, text):
        """Add text to output log"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.root.update()
    
    def generate_code(self):
        """Generate code using GPT Engineer"""
        # Validation
        if not self.api_key.get():
            messagebox.showerror("Error", "Please enter your API key")
            return
        
        if not self.project_path.get():
            messagebox.showerror("Error", "Please select a project folder")
            return
        
        prompt_text = self.prompt_entry.get(1.0, tk.END).strip()
        if not prompt_text:
            messagebox.showerror("Error", "Please enter a description of what you want to build")
            return
        
        # Save prompt to project folder
        try:
            project_dir = Path(self.project_path.get())
            project_dir.mkdir(exist_ok=True)
            
            prompt_file = project_dir / "prompt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project folder: {e}")
            return
        
        # Disable generate button
        self.generate_btn.config(state=tk.DISABLED, text="🔄 Generating...")
        
        # Clear output
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        # Run generation in a separate thread
        thread = threading.Thread(target=self.run_generation)
        thread.daemon = True
        thread.start()
    
    def run_generation(self):
        """Run GPT Engineer generation"""
        try:
            self.log_output("🚀 Starting GPT Engineer...")
            self.log_output(f"📁 Project: {self.project_path.get()}")
            self.log_output(f"🤖 Model: {self.model_choice.get()}")
            self.log_output(f"⚙️ Mode: {self.generation_mode.get()}")
            self.log_output("")
            
            # Set up environment
            env = os.environ.copy()
            env.update({
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONUTF8': '1',
                'GRPC_VERBOSITY': 'ERROR',
                'GOOGLE_API_KEY': self.api_key.get(),
                'GEMINI_API_KEY': self.api_key.get()
            })
            
            # Build command
            cmd = [
                sys.executable, 'run_simple.py',
                self.project_path.get()
            ]
            
            # Add mode flags
            if self.generation_mode.get() == "improve":
                cmd.append("--improve")
            elif self.generation_mode.get() == "lite":
                cmd.append("--lite")
            
            # Run command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                env=env,
                cwd=Path(__file__).parent
            )
            
            # Stream output
            for line in process.stdout:
                self.log_output(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log_output("")
                self.log_output("✅ Generation completed successfully!")
                self.log_output("📁 Check your project folder for generated files")
                
                # Ask if user wants to extract files
                if messagebox.askyesno("Extract Files", "Do you want to extract the generated files?"):
                    self.extract_files()
            else:
                self.log_output("❌ Generation failed")
                
        except Exception as e:
            self.log_output(f"❌ Error: {e}")
        
        finally:
            # Re-enable generate button
            self.generate_btn.config(state=tk.NORMAL, text="🚀 Generate Code")
    
    def extract_files(self):
        """Extract generated files from logs"""
        try:
            self.log_output("🔍 Extracting generated files...")
            
            # Run extraction script
            cmd = [sys.executable, 'extract_files.py']
            process = subprocess.run(cmd, capture_output=True, text=True, 
                                   cwd=Path(__file__).parent)
            
            if process.returncode == 0:
                self.log_output("✅ Files extracted successfully!")
                messagebox.showinfo("Success", "Files extracted to your project folder!")
            else:
                self.log_output("❌ File extraction failed")
                
        except Exception as e:
            self.log_output(f"❌ Extraction error: {e}")

def main():
    """Main function"""
    # Create and run the enhanced GUI
    root = tk.Tk()
    
    # Set modern theme and styling
    try:
        style = ttk.Style()
        # Try to use a modern theme
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Configure custom styles
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
        
    except Exception:
        pass
    
    # Create the application
    app = GPTEngineerGUI(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Set window icon (if available)
    try:
        # You can add an icon file here
        # root.iconbitmap("icon.ico")
        pass
    except Exception:
        pass
    
    # Configure window close behavior
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit GPT Engineer?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
