import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.config import WATCH_DIR, CONFIG, save_config
from core.organizer import DirOrganizer
from utils.file_utils import validate_directory

class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart File Organizer")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        try:
            self.root.iconbitmap("folder_icon.ico")
        except:
            pass

        self.is_watching = False
        self.is_organizing = False
        self.stop_requested = False
        self.observer = None
        self.organizer = None
        self.gui_handler = None

        self.setup_style()
        self.create_widgets()
        self.update_status()

    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Light Creamy Theme color scheme
        self.colors = {
            'primary': '#d9a05b',       # Warm caramel/gold
            'primary_hover': '#c98e47', # Darker caramel
            'primary_pressed': '#b67a32',
            'secondary': '#f2e8cf',     # Light cream
            'success': '#8ab060',       # Soft sage green
            'success_hover': '#7a9e52',
            'success_pressed': '#688c42',
            'warning': '#e8a55d',       # Soft orange
            'warning_hover': '#d6944e',
            'warning_pressed': '#c4823d',
            'danger': '#d96c6c',        # Soft red/coral
            'danger_hover': '#c95a5a',
            'danger_pressed': '#b64b4b',
            'light': '#faf6f0',         # Very light warm gray/cream
            'dark': '#5c5248',          # Warm dark gray/brown for text
            'background': '#fcfbfa',    # Almost white with a hint of cream
            'text': '#36302a',          # Dark brown/black for text
            'widget_bg': '#ffffff',     # Pure white for contrast
            'border': '#e6dcd0'         # Soft beige border
        }

        self.root.configure(bg=self.colors['background'])
        self.style.configure('TFrame', background=self.colors['background'])
        
        self.style.configure('TLabel', background=self.colors['background'],
                             foreground=self.colors['text'], font=('Segoe UI', 10))
        self.style.configure('Title.TLabel', background=self.colors['background'],
                             foreground=self.colors['primary'], font=('Segoe UI', 18, 'bold'))
        self.style.configure('Subtitle.TLabel', background=self.colors['background'],
                             foreground=self.colors['dark'], font=('Segoe UI', 11))
        
        # Status Label Styles
        self.style.configure('Status.NotRunning.TLabel', background=self.colors['background'],
                             foreground=self.colors['dark'], font=('Segoe UI', 11, 'bold'))
        self.style.configure('Status.Running.TLabel', background=self.colors['background'],
                             foreground=self.colors['success'], font=('Segoe UI', 11, 'bold'))
        self.style.configure('Status.Organizing.TLabel', background=self.colors['background'],
                             foreground=self.colors['warning'], font=('Segoe UI', 11, 'bold'))
        
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'))

        # Primary Button (Caramel/Gold)
        self.style.configure('Primary.TButton', background=self.colors['primary'],
                             foreground='#ffffff', borderwidth=0, focusthickness=0,
                             focuscolor='none', padding=10, relief='flat')
        self.style.map('Primary.TButton',
                       background=[('disabled', self.colors['border']),
                                   ('pressed', self.colors['primary_pressed']), 
                                   ('active', self.colors['primary_hover'])],
                       foreground=[('disabled', self.colors['dark']),
                                   ('pressed', '#ffffff'), 
                                   ('active', '#ffffff')])

        # Success Button (Sage Green)
        self.style.configure('Success.TButton', background=self.colors['success'],
                             foreground='#ffffff', borderwidth=0, focusthickness=0,
                             focuscolor='none', padding=10, relief='flat')
        self.style.map('Success.TButton',
                       background=[('disabled', self.colors['border']),
                                   ('pressed', self.colors['success_pressed']), 
                                   ('active', self.colors['success_hover'])],
                       foreground=[('disabled', self.colors['dark']),
                                   ('pressed', '#ffffff'), 
                                   ('active', '#ffffff')])

        # Danger Button (Soft Red)
        self.style.configure('Danger.TButton', background=self.colors['danger'],
                             foreground='#ffffff', borderwidth=0, focusthickness=0,
                             focuscolor='none', padding=10, relief='flat')
        self.style.map('Danger.TButton',
                       background=[('disabled', self.colors['border']),
                                   ('pressed', self.colors['danger_pressed']), 
                                   ('active', self.colors['danger_hover'])],
                       foreground=[('disabled', self.colors['dark']),
                                   ('pressed', '#ffffff'), 
                                   ('active', '#ffffff')])

        # Regular Button
        self.style.configure('TButton', background=self.colors['secondary'],
                             foreground=self.colors['text'], borderwidth=0,
                             padding=5, relief='flat')
        self.style.map('TButton',
                       background=[('pressed', '#e3d6b8'), 
                                   ('active', '#ede3cc')],
                       foreground=[('pressed', self.colors['text']), 
                                   ('active', self.colors['text'])])

        self.style.configure('Treeview', background=self.colors['widget_bg'],
                             foreground=self.colors['text'], fieldbackground=self.colors['widget_bg'],
                             font=('Segoe UI', 9), bordercolor=self.colors['border'])
        self.style.configure('Treeview.Heading', background=self.colors['secondary'],
                             foreground=self.colors['text'], font=('Segoe UI', 10, 'bold'),
                             bordercolor=self.colors['border'])

        self.style.configure('TLabelframe', background=self.colors['background'],
                             bordercolor=self.colors['primary'], relief='solid', borderwidth=1)
        self.style.configure('TLabelframe.Label', background=self.colors['background'],
                             foreground=self.colors['primary'], font=('Segoe UI', 11, 'bold'))

        self.style.configure('TEntry', fieldbackground=self.colors['widget_bg'],
                             foreground=self.colors['text'], bordercolor=self.colors['secondary'],
                             insertcolor=self.colors['text'])  # Make cursor visible

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 25))

        title_container = ttk.Frame(header_frame)
        title_container.pack(fill=tk.X)

        title_label = ttk.Label(title_container, text="Smart File Organizer", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(title_container,
                                   text="Automatically organize your files by category",
                                   style='Subtitle.TLabel')
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0))

        status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding="20")
        status_frame.pack(fill=tk.X, pady=(0, 20))

        status_content = ttk.Frame(status_frame)
        status_content.pack(fill=tk.X)

        self.status_label = ttk.Label(status_content, text="Not Running",
                                      style='Status.NotRunning.TLabel', font=('Segoe UI', 12))
        self.status_label.pack(side=tk.LEFT)

        file_counter_frame = ttk.Frame(status_content)
        file_counter_frame.pack(side=tk.RIGHT)

        self.files_label = ttk.Label(file_counter_frame, text="Files organized: 0",
                                     font=('Segoe UI', 10))
        self.files_label.pack(side=tk.LEFT)

        dir_frame = ttk.LabelFrame(main_frame, text="Folder to Watch", padding="20")
        dir_frame.pack(fill=tk.X, pady=(0, 20))

        dir_input_frame = ttk.Frame(dir_frame)
        dir_input_frame.pack(fill=tk.X)

        self.dir_var = tk.StringVar(value=WATCH_DIR)
        dir_entry = ttk.Entry(dir_input_frame, textvariable=self.dir_var,
                              font=('Segoe UI', 10), width=60)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))

        browse_btn = ttk.Button(dir_input_frame, text="Browse",
                                command=self.browse_directory, style='Primary.TButton')
        browse_btn.pack(side=tk.RIGHT)

        control_frame = ttk.LabelFrame(main_frame, text="Actions", padding="20")
        control_frame.pack(fill=tk.X, pady=(0, 20))

        button_container = ttk.Frame(control_frame)
        button_container.pack(fill=tk.X)

        self.start_btn = ttk.Button(button_container, text="Start Watching",
                                    command=self.start_watching, style='Success.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.organize_btn = ttk.Button(button_container, text="Organize Existing Files",
                                       command=self.organize_existing, style='Primary.TButton')
        self.organize_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(button_container, text="Stop All",
                                   command=self.stop_all, style='Danger.TButton', state='disabled')
        self.stop_btn.pack(side=tk.LEFT)

        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="15")
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_header = ttk.Frame(log_frame)
        log_header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(log_header, text="Recent file movements and system messages",
                  font=('Segoe UI', 9), foreground=self.colors['dark']).pack(side=tk.LEFT)

        clear_btn = ttk.Button(log_header, text="Clear Log",
                               command=self.clear_log, style='TButton')
        clear_btn.pack(side=tk.RIGHT)

        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_container, height=15, bg=self.colors['widget_bg'],
                                fg=self.colors['text'], font=('Consolas', 9), wrap=tk.WORD,
                                state='disabled', relief='solid', borderwidth=1,
                                padx=10, pady=10, highlightthickness=0)

        scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_count = 0

        self.log("Application started. Ready to organize files!", "info")

        if WATCH_DIR == "":
            messagebox.showinfo("Select Folder", "Please choose a folder to watch.")
            self.browse_directory()

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            valid, msg = validate_directory(directory)
            if not valid:
                messagebox.showerror("Invalid Folder", msg)
                return

            self.dir_var.set(directory)
            CONFIG["watch_directory"] = directory
            save_config(CONFIG)

            self.start_btn.config(state='normal')
            self.log(f"Watch directory set to: {directory}", "success")
            self.update_status()

    def update_status(self):
        directory = self.dir_var.get()
        if os.path.exists(directory):
            file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
            self.files_label.config(text=f"Files in directory: {file_count}")
        else:
            self.files_label.config(text="Directory does not exist")

    def log(self, message, message_type="info"):
        self.log_text.config(state='normal')
        timestamp = time.strftime("%H:%M:%S")

        if message_type == "success":
            prefix = "[SUCCESS]"
        elif message_type == "warning":
            prefix = "[WARNING]"
        elif message_type == "error":
            prefix = "[ERROR]"
        elif message_type == "move":
            prefix = "[MOVE]"
        else:
            prefix = "[INFO]"

        self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()

    def clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.log("Log cleared", "info")

    def increment_file_count(self):
        self.file_count += 1
        self.files_label.config(text=f"Files organized: {self.file_count}")

    def start_watching(self):
        directory = self.dir_var.get()
        if not os.path.exists(directory):
            messagebox.showerror("Error", "The selected directory does not exist!")
            return

        try:
            self.organizer = DirOrganizer(directory, self)

            self.log("Organizing existing files...", "info")
            self.is_organizing = True
            self.update_button_states()

            org_thread = threading.Thread(target=self._organize_then_watch, daemon=True)
            org_thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start file watcher: {str(e)}")

    def _organize_then_watch(self):
        try:
            self.organizer._classify_existing_files_gui()

            if self.stop_requested:
                self.log("Organization stopped by user", "warning")
                return

            self.is_watching = True
            self.is_organizing = False
            self.update_button_states()

            self.log("Finished organizing existing files!", "success")
            self.log(f"Started watching directory: {self.dir_var.get()}", "success")

            self.organizer.start_gui()

        except Exception as e:
            self.log(f"Error during organization/watching: {str(e)}", "error")
        finally:
            self.is_organizing = False
            self.update_button_states()

    def stop_all(self):
        self.stop_requested = True
        self.is_organizing = False
        self.is_watching = False

        if self.organizer and self.organizer.observer:
            self.organizer.observer.stop()
            self.organizer.observer.join()

        self.status_label.config(text="Not Running", style='Status.NotRunning.TLabel')
        self.update_button_states()
        self.log("All operations stopped by user", "warning")

    def update_button_states(self):
        if self.is_organizing or self.is_watching:
            self.start_btn.config(state='disabled')
            self.organize_btn.config(state='disabled')
            self.stop_btn.config(state='normal')

            if self.is_organizing:
                self.status_label.config(text="Organizing Files...", style='Status.Organizing.TLabel')
                self.stop_btn.config(text="Stop Organization")
            else:
                self.status_label.config(text="Running - Watching for new files", style='Status.Running.TLabel')
                self.stop_btn.config(text="Stop Watching")
        else:
            self.start_btn.config(state='normal')
            self.organize_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.status_label.config(text="Not Running", style='Status.NotRunning.TLabel')
            self.stop_requested = False

    def organize_existing(self):
        directory = self.dir_var.get()
        if not os.path.exists(directory):
            messagebox.showerror("Error", "The selected directory does not exist!")
            return

        def organize_thread():
            self.is_organizing = True
            self.update_button_states()
            self.log("Starting to organize existing files...", "info")

            organizer = DirOrganizer(directory, self)
            organizer._classify_existing_files_gui()

            self.is_organizing = False
            self.update_button_states()
            self.log("Finished organizing existing files!", "success")

        thread = threading.Thread(target=organize_thread, daemon=True)
        thread.start()
