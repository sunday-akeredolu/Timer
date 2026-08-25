import ctypes
import json
import os
import random
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
import winsound


class CustomTimerApp:
    """A professional-grade countdown timer with custom messaging."""

    def __init__(self, root):
        self.root = root
        self.root.title('Timer')
        self.root.geometry('400x560')
        self.root.resizable(False, False)
        self.root.configure(bg='black')
        self._set_dark_title_bar(self.root)

        self.remaining_time = 0
        self.timer_running = False
        self.is_paused = False
        self.after_id = None
        self.hide_fs_id = None
        self._last_width = 0
        self._last_height = 0

        self.countdown_window = None
        self.content_container = None
        self.msg_label = None
        self.countdown_label = None
        self.progress_canvas = None
        self.sizegrip = None
        self.total_duration = 0
        self._drag_data = {'x': 0, 'y': 0}

        self.transparent_var = tk.BooleanVar(value=True)
        self.saved_geometry = '1000x500+100+100'
        self.first_launch = True

        base_path = (
            os.path.dirname(sys.executable)
            if getattr(sys, 'frozen', False)
            else os.path.dirname(os.path.abspath(__file__))
        )
        self.presets_file = os.path.join(base_path, 'timer_presets.json')

        self._load_presets()
        self._show_welcome_screen()

        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<s>', lambda e: self.start_timer())
        self.root.bind('<p>', lambda e: self.toggle_pause())
        self.root.bind('<r>', lambda e: self.reset_timer())
        self.root.bind('<q>', lambda e: self._on_closing())
        self.root.protocol('WM_DELETE_WINDOW', self._on_closing)

    def _show_welcome_screen(self):
        """Displays a cinematic welcome screen on the first launch."""
        self.welcome_frame = tk.Frame(self.root, bg='black')
        self.welcome_frame.pack(expand=True, fill='both')

        tk.Label(
            self.welcome_frame, text='[ SYSTEM BOOT ]', font=('Consolas', 10), bg='black', fg='#03dac6'
        ).pack(pady=(120, 20))

        self.welcome_title = tk.Label(
            self.welcome_frame, text='TIMER', font=('Helvetica', 28, 'bold'), bg='black', fg='white'
        )
        self.welcome_title.pack()

        tk.Label(
            self.welcome_frame, text='INTERFACE v1.0', font=('Consolas', 10), bg='black', fg='#2980b9'
        ).pack(pady=10)

        self.boot_label = tk.Label(
            self.welcome_frame, text='LOADING MODULES...', font=('Consolas', 8), bg='black', fg='#7f8c8d'
        )
        self.boot_label.pack(side='bottom', pady=40)

        self._animate_glitch()
        self.root.after(1000, lambda: self.boot_label.config(text='CALIBRATING OVERLAY...'))
        self.root.after(2000, lambda: self.boot_label.config(text='READY.'))
        self.root.after(3000, self._show_developer_screen)

    def _show_developer_screen(self):
        """Displays developer information as the second part of the boot sequence."""
        if hasattr(self, 'glitch_id') and self.glitch_id:
            self.root.after_cancel(self.glitch_id)
            self.glitch_id = None
        if hasattr(self, 'welcome_frame') and self.welcome_frame.winfo_exists():
            for widget in self.welcome_frame.winfo_children():
                widget.destroy()

            tk.Label(
                self.welcome_frame, text='[ DEVELOPED BY: ]', font=('Consolas', 10), bg='black', fg='#03dac6'
            ).pack(pady=(120, 20))

            sunday_art = (
                "   _____ _   _ _   _ ____      _   __   __\n"
                "  / ___/| | | | \\ | |  _ \\    / \\  \\ \\ / /\n"
                "  \\__ \\ | | | |  \\| | | | |  / _ \\  \\ V / \n"
                " ___/ / | |_| | |\\  | |_/ /  / ___ \\  | |  \n"
                "/____/   \\___/|_| \\_|____/  /_/   \\_\\ |_|  "
            )
            self.welcome_title = tk.Label(
                self.welcome_frame, text=sunday_art, font=('Consolas', 9, 'bold'), bg='black', fg='white'
            )
            self.welcome_title.pack(pady=5)

            tk.Label(
                self.welcome_frame, text='© 2026 ALL RIGHTS RESERVED', font=('Consolas', 10), bg='black', fg='#2980b9'
            ).pack(pady=10)

            self.boot_label = tk.Label(
                self.welcome_frame, text='INITIALIZING CORE...', font=('Consolas', 8), bg='black', fg='#7f8c8d'
            )
            self.boot_label.pack(side='bottom', pady=40)

            self.root.after(3000, self._transition_to_main)

    def _animate_glitch(self):
        """Creates a subtle text glitch effect on the welcome screen."""
        if not hasattr(self, 'welcome_frame') or not self.welcome_frame.winfo_exists():
            return

        original_text = "TIMER"
        chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        glitched = list(original_text)
        valid_indices = [i for i, c in enumerate(original_text) if not c.isspace()]

        if valid_indices:
            for _ in range(random.randint(1, 2)):
                pos = random.choice(valid_indices)
                glitched[pos] = random.choice(chars)

            self.welcome_title.config(text=''.join(glitched), fg='#ff0266')
            self.root.after(
                60, 
                lambda: self.welcome_title.config(text=original_text, fg='white') 
                if self.welcome_title.winfo_exists() else None
            )

        self.glitch_id = self.root.after(random.randint(300, 1000), self._animate_glitch)

    def _transition_to_main(self):
        """Clears the welcome screen and loads the main UI."""
        if hasattr(self, 'glitch_id') and self.glitch_id:
            self.root.after_cancel(self.glitch_id)
        if hasattr(self, 'welcome_frame') and self.welcome_frame.winfo_exists():
            self.welcome_frame.destroy()
        self.first_launch = False
        self._save_data()
        self._setup_ui()

    def _setup_ui(self):
        """Initializes the User Interface components."""
        main_frame = tk.Frame(self.root, padx=20, pady=10, bg='black')
        main_frame.pack(expand=True, fill='both')

        header_frame = tk.Frame(main_frame, bg='black')
        header_frame.pack(fill='x', pady=(0, 10))

        tk.Label(header_frame, text='COORDINATES', font=('Consolas', 8), bg='black', fg='#03dac6').pack(side='left')
        tk.Label(header_frame, text='SYSTEM STATUS: ONLINE', font=('Consolas', 8), bg='black', fg='#03dac6').pack(side='right')

        input_frame = tk.Frame(main_frame, bg='black')
        input_frame.pack(pady=2)

        self.hour_entry = self._create_input(input_frame, 'HOURS', 0)
        tk.Label(input_frame, text=':', font=('Helvetica', 18), bg='black', fg='white').grid(row=0, column=1, padx=5, sticky='s')
        self.min_entry = self._create_input(input_frame, 'MINS', 2)
        tk.Label(input_frame, text=':', font=('Helvetica', 18), bg='black', fg='white').grid(row=0, column=3, padx=5, sticky='s')
        self.sec_entry = self._create_input(input_frame, 'SECS', 4)
        self.sec_entry.delete(0, tk.END)
        self.sec_entry.insert(0, '30')

        self.presets_container = tk.Frame(main_frame, bg='black')
        self.presets_container.pack(pady=2)
        self._render_presets()

        tk.Label(main_frame, text='OVERLAY TEXT', font=('Helvetica', 8, 'bold'), bg='black', fg='#7f8c8d').pack(pady=(10, 0))

        msg_container = tk.Frame(main_frame, width=300, height=35, bg='#1e1e1e', padx=2, pady=2)
        msg_container.pack_propagate(False)
        msg_container.pack(pady=5)

        self.msg_entry = tk.Entry(
            msg_container, font=('Helvetica', 11), justify='center', bg='#1e1e1e', fg='white', insertbackground='white', borderwidth=0
        )
        self.msg_entry.insert(0, 'Enter overlay message...')
        self.msg_entry.pack(expand=True, fill='both')

        size_row = tk.Frame(main_frame, bg='black')
        size_row.pack(pady=(0, 5))

        tk.Label(size_row, text='SCALE:', font=('Helvetica', 8, 'bold'), bg='black', fg='#7f8c8d').pack(side='left', padx=5)
        self.msg_size_entry = tk.Entry(
            size_row, font=('Helvetica', 11), width=5, justify='center', bg='#1e1e1e', fg='white', borderwidth=0
        )
        self.msg_size_entry.insert(0, '30')
        self.msg_size_entry.pack(side='left')
        self.msg_size_entry.bind('<KeyRelease>', lambda e: self._update_input_font())

        self.show_msg_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            main_frame, text='Show message during countdown', variable=self.show_msg_var,
            bg='black', fg='white', selectcolor='black', activebackground='black', activeforeground='white', font=('Helvetica', 10)
        ).pack(pady=5)

        tk.Checkbutton(
            main_frame, text='Enable 100% Transparency', variable=self.transparent_var,
            command=self._update_transparency, bg='black', fg='white', selectcolor='black', activebackground='black', activeforeground='white', font=('Helvetica', 10)
        ).pack(pady=5)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TSizegrip', background='#1a1a1a')

        self.display_label = tk.Label(main_frame, text='00:00:00', font=('Calibri', 50, 'bold'), fg='#2980b9', bg='black')
        self.display_label.pack(pady=5)

        btn_frame = tk.Frame(main_frame, bg='black')
        btn_frame.pack(pady=5)

        start_container = tk.Frame(btn_frame, bg='black')
        start_container.grid(row=0, column=0, padx=10, pady=5)
        self.start_button = tk.Button(
            start_container, text='▶ START', command=self.start_timer, bg='#27ae60', fg='white', font=('Helvetica', 10, 'bold'), width=12, relief='flat'
        )
        self.start_button.pack()
        tk.Label(start_container, text='[S]', font=('Helvetica', 8), fg='#7f8c8d', bg='black').pack()

        pause_container = tk.Frame(btn_frame, bg='black')
        pause_container.grid(row=0, column=1, padx=10, pady=5)
        self.pause_button = tk.Button(
            pause_container, text='⏸ PAUSE', command=self.toggle_pause, bg='#f39c12', fg='white', font=('Helvetica', 10, 'bold'), width=12, relief='flat', state='disabled'
        )
        self.pause_button.pack()
        tk.Label(pause_container, text='[P]', font=('Helvetica', 8), fg='#7f8c8d', bg='black').pack()

        reset_container = tk.Frame(btn_frame, bg='black')
        reset_container.grid(row=1, column=0, padx=10, pady=5)
        self.reset_button = tk.Button(
            reset_container, text='↺ RESET', command=self.reset_timer, bg='#c0392b', fg='white', font=('Helvetica', 10, 'bold'), width=12, relief='flat'
        )
        self.reset_button.pack()
        tk.Label(reset_container, text='[R]', font=('Helvetica', 8), fg='#7f8c8d', bg='black').pack()

        exit_container = tk.Frame(btn_frame, bg='black')
        exit_container.grid(row=1, column=1, padx=10, pady=5)
        self.exit_button = tk.Button(
            exit_container, text='✖ EXIT', command=self._on_closing, bg='#7f8c8d', fg='white', font=('Helvetica', 10, 'bold'), width=12, relief='flat'
        )
        self.exit_button.pack()
        tk.Label(exit_container, text='[Q]', font=('Helvetica', 8), fg='#7f8c8d', bg='black').pack()

        self.about_button = tk.Button(
            main_frame, text='ℹ About', command=self._show_about_screen,
            bg='black', fg='#7f8c8d', font=('Helvetica', 9), relief='flat', cursor='hand2', activebackground='black', activeforeground='#95a5a6'
        )
        self.about_button.pack(pady=(5, 0))

    def _create_input(self, parent, label, column):
        """Helper to create labeled entry fields."""
        container = tk.Frame(parent, bg='black')
        container.grid(row=0, column=column)
        tk.Label(container, text=label, font=('Helvetica', 7, 'bold'), fg='#7f8c8d', bg='black').pack()
        entry = tk.Entry(
            container, width=4, font=('Helvetica', 18), justify='center', bg='#1e1e1e', fg='#03dac6', borderwidth=0, insertbackground='#03dac6'
        )
        entry.insert(0, '00')
        entry.pack()
        return entry

    def _load_presets(self):
        """Loads presets and settings from file or defaults."""
        default_presets = [['5 MIN', 300], ['10 MIN', 600], ['30 MIN', 1800]]
        self.presets = default_presets

        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.presets = data.get('presets', default_presets)
                        self.transparent_var.set(data.get('transparency', True))
                        self.saved_geometry = data.get('geometry', '1000x500+100+100')
                        self.first_launch = data.get('first_launch', True)
                    elif isinstance(data, list):
                        self.presets = data

                standardized = []
                for _, seconds in self.presets:
                    standardized.append([self._format_duration(seconds), seconds])
                self.presets = standardized
                self._save_data()
            except (json.JSONDecodeError, IOError):
                pass

    def _render_presets(self):
        """Clears and redraws the preset buttons."""
        for widget in self.presets_container.winfo_children():
            widget.destroy()

        for i, (label, seconds) in enumerate(self.presets):
            f = tk.Frame(self.presets_container, bg='black')
            f.pack(side='left', padx=1)

            btn = tk.Button(
                f, text=label, command=lambda s=seconds: self._set_preset(s),
                bg='#34495e', fg='white', font=('Helvetica', 8, 'bold'), width=6, relief='flat'
            )
            btn.pack(side='left')

            del_btn = tk.Button(
                f, text='×', command=lambda idx=i: self._delete_preset(idx),
                bg='#34495e', fg='#e74c3c', font=('Helvetica', 7), padx=2, pady=0, relief='flat', activebackground='#ff0266'
            )
            del_btn.pack(side='left')

        save_btn = tk.Button(
            self.presets_container, text='+', command=self._save_current_as_preset,
            bg='#2980b9', fg='white', font=('Helvetica', 8, 'bold'), width=3, relief='flat'
        )
        save_btn.pack(side='left', padx=5)

    def _save_data(self):
        """Saves current presets and settings to file."""
        data = {
            'presets': self.presets,
            'transparency': self.transparent_var.get(),
            'geometry': self.saved_geometry,
            'first_launch': self.first_launch
        }
        try:
            with open(self.presets_file, 'w') as f:
                json.dump(data, f)
        except IOError:
            pass

    def _save_current_as_preset(self):
        """Saves current time settings to the presets list."""
        try:
            h = int(self.hour_entry.get() or 0)
            m = int(self.min_entry.get() or 0)
            s = int(self.sec_entry.get() or 0)
            total = h * 3600 + m * 60 + s
            if total <= 0:
                messagebox.showwarning('Invalid Input', 'Please enter a positive duration.')
                return
            label = self._format_duration(total)
            self.presets.append([label, total])
            self._save_data()
            self._render_presets()
        except ValueError:
            messagebox.showwarning('Invalid Input', 'Please enter valid numeric values for hours, minutes, and seconds.')

    def _delete_preset(self, index):
        """Removes a preset from the list and saves changes."""
        if 0 <= index < len(self.presets):
            self.presets.pop(index)
            self._save_data()
            self._render_presets()

    def _format_duration(self, total_seconds):
        """Generates a consistent label pattern like 5 MIN or 1H 30M."""
        h, remainder = divmod(total_seconds, 3600)
        m, s = divmod(remainder, 60)

        if h > 0 and m == 0 and s == 0:
            return f'{h} HR'
        elif h == 0 and m > 0 and s == 0:
            return f'{m} MIN'
        elif h == 0 and m == 0 and s > 0:
            return f'{s} SEC'
        else:
            parts = []
            if h > 0:
                parts.append(f'{h}H')
            if m > 0:
                parts.append(f'{m}M')
            if s > 0:
                parts.append(f'{s}S')
            return ' '.join(parts) if parts else '0 SEC'

    def _set_preset(self, total_seconds):
        """Sets the timer input fields to a predefined second value."""
        hours, remainder = divmod(total_seconds, 3600)
        mins, secs = divmod(remainder, 60)

        self.hour_entry.delete(0, tk.END)
        self.hour_entry.insert(0, f'{hours:02d}')

        self.min_entry.delete(0, tk.END)
        self.min_entry.insert(0, f'{mins:02d}')

        self.sec_entry.delete(0, tk.END)
        self.sec_entry.insert(0, f'{secs:02d}')

    def _update_input_font(self):
        """Updates the font size of the message entry based on user input."""
        try:
            display_size = min(max(self._get_msg_size(), 8), 15)
            self.msg_entry.config(font=('Helvetica', display_size))
        except ValueError:
            pass

    def _get_msg_size(self):
        """Helper to get and parse the font size entry."""
        try:
            return int(self.msg_size_entry.get() or 30)
        except ValueError:
            return 30

    def start_timer(self):
        """Validates inputs and begins the countdown."""
        if self.timer_running:
            return

        try:
            hours = int(self.hour_entry.get() or 0)
            mins = int(self.min_entry.get() or 0)
            secs = int(self.sec_entry.get() or 0)

            self.remaining_time = hours * 3600 + mins * 60 + secs
            self.total_duration = self.remaining_time

            if self.remaining_time <= 0:
                messagebox.showwarning('Input Error', 'Please enter a positive duration.')
                return

            self.timer_running = True
            self.is_paused = False

            self.start_button.config(state='disabled', bg='#1e1e1e', fg='#444444')
            self.pause_button.config(state='normal')

            self.countdown_window = tk.Toplevel(self.root)
            self.countdown_window.overrideredirect(True)
            self.countdown_window.title('Timer Overlay')
            self.countdown_window.geometry(self.saved_geometry)
            self.countdown_window.configure(bg='black')
            self.countdown_window.attributes('-topmost', True)
            self.countdown_window.attributes('-alpha', 1.0)

            if self.transparent_var.get():
                self.countdown_window.attributes('-transparentcolor', 'black')

            self.progress_canvas = tk.Canvas(self.countdown_window, height=10, bg='black', highlightthickness=0)
            self.progress_canvas.pack(side='bottom', fill='x')
            self.countdown_window.update_idletasks()
            win_width = max(self.countdown_window.winfo_width(), 1)
            self.progress_rect = self.progress_canvas.create_rectangle(0, 0, win_width, 10, fill='#2980b9', outline='')

            self.content_container = tk.Frame(self.countdown_window, bg='black')
            self.content_container.pack(expand=True)

            msg_text = self.msg_entry.get() if self.show_msg_var.get() else ""
            if msg_text and msg_text != 'Enter overlay message...':
                user_size = self._get_msg_size()
                self.msg_label = tk.Label(self.content_container, text=msg_text, font=('Calibri', user_size), fg='white', bg='black')
                self.msg_label.pack()
                self._bind_drag(self.msg_label)

            self.countdown_label = tk.Label(self.content_container, text='00:00:00', font=('Calibri', 150, 'bold'), fg='#2980b9', bg='black')
            self.countdown_label.pack()

            self.fs_button = tk.Button(
                self.countdown_window, text='⛶', command=self._toggle_fullscreen,
                bg='#1a1a1a', fg='#7f8c8d', font=('Arial', 12), relief='flat', bd=0, cursor='hand2'
            )
            self.fs_button.place(relx=0.5, rely=0.95, anchor='s')
            self.fs_button.bind('<Enter>', lambda e: self.fs_button.config(fg='#2980b9'))

            self.close_button = tk.Button(
                self.countdown_window, text='✖', command=self.reset_timer,
                bg='#1a1a1a', fg='#e74c3c', font=('Arial', 12), relief='flat', bd=0, cursor='hand2'
            )
            self.close_button.place(relx=0.65, rely=0.95, anchor='s')
            self.close_button.bind('<Enter>', lambda e: self.close_button.config(fg='#ff0266'))

            self.sizegrip = ttk.Sizegrip(self.countdown_window)
            self.sizegrip.place(relx=1.0, rely=1.0, anchor='se')

            for widget in [self.countdown_window, self.content_container, self.countdown_label, self.sizegrip, self.close_button]:
                widget.bind('<Motion>', self._on_overlay_motion)
            if self.msg_label:
                self.msg_label.bind('<Motion>', self._on_overlay_motion)

            for widget in [self.content_container, self.countdown_label, self.countdown_window]:
                self._bind_drag(widget)

            self.countdown_window.bind('<Configure>', self._on_window_resize)
            self.countdown_window.bind('<Escape>', lambda e: self.reset_timer())
            self.countdown_window.bind('<space>', lambda e: self.toggle_pause())
            self._on_overlay_motion()
            self.countdown()

        except ValueError:
            messagebox.showerror('Input Error', 'Please enter valid numeric values.')

    def _bind_drag(self, widget):
        """Helper to bind drag events to a widget."""
        widget.bind('<Button-1>', self._on_drag_start)
        widget.bind('<B1-Motion>', self._on_drag_motion)

    def toggle_pause(self):
        """Toggles the pause state of the timer."""
        if not self.timer_running:
            return

        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text='▶ RESUME', bg='#3498db')
        else:
            self.pause_button.config(text='⏸ PAUSE', bg='#f39c12')
            self.after_id = self.root.after(1000, self.countdown)

    def countdown(self):
        """The core recursive loop for the timer."""
        if self.is_paused:
            return
        else:
            if self.remaining_time >= 0:
                hours, remainder = divmod(self.remaining_time, 3600)
                mins, secs = divmod(remainder, 60)
                time_str = f'{hours:02d}:{mins:02d}:{secs:02d}'
                base_fg = '#e74c3c' if self.remaining_time <= 10 else '#2980b9'
                self.display_label.config(text=time_str, fg=base_fg)

                if self.countdown_window and self.countdown_window.winfo_exists():
                    threshold = 30 if self.total_duration < 300 else self.total_duration * 0.1
                    is_danger = self.remaining_time <= threshold
                    self._update_countdown_visuals(time_str, is_danger, base_fg)

                    if self.progress_canvas:
                        win_width = self.countdown_window.winfo_width()
                        progress = self.remaining_time / self.total_duration if self.total_duration > 0 else 0
                        r = int(231 + (-190) * progress)
                        g = int(76 + 52 * progress)
                        b = int(60 + 125 * progress)
                        current_prog_color = f'#{r:02x}{g:02x}{b:02x}'
                        new_width = win_width * progress
                        self.progress_canvas.coords(self.progress_rect, win_width - new_width, 0, win_width, 10)
                        self.progress_canvas.itemconfig(self.progress_rect, fill=current_prog_color)

                self.remaining_time -= 1
                self.after_id = self.root.after(1000, self.countdown)
            else:
                self.timer_running = False
                self.start_button.config(state='normal')
                self.pause_button.config(state='disabled', text='⏸ PAUSE')

    def _update_countdown_visuals(self, time_str, is_danger, base_fg):
        """Handles background flashing and color shifting during alerts."""
        flash_bg = 'red' if is_danger and self.remaining_time % 2 == 0 else 'black'
        active_fg = '#2980b9' if flash_bg == 'red' else base_fg

        if is_danger and self.remaining_time % 2 == 0:
            try:
                winsound.Beep(1000, 100)
            except (RuntimeError, OSError):
                pass

        if self.countdown_window.cget('bg') != flash_bg:
            for widget in [self.countdown_window, self.content_container, self.countdown_label]:
                widget.config(bg=flash_bg)
            if self.msg_label and self.msg_label.winfo_exists():
                self.msg_label.config(bg=flash_bg)
            if hasattr(self, 'fs_button') and self.fs_button.winfo_exists():
                self.fs_button.config(bg=flash_bg if flash_bg == 'red' else '#1a1a1a')

        self.countdown_label.config(text=time_str, fg=active_fg)

    def _update_transparency(self):
        """Updates the transparency state of the active countdown window."""
        self._save_data()
        if self.countdown_window and self.countdown_window.winfo_exists():
            if self.transparent_var.get():
                self.countdown_window.attributes('-transparentcolor', 'black')
            else:
                self.countdown_window.attributes('-transparentcolor', '')

    def _stop_timers(self):
        """Cancels all active timer and animation loops."""
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if self.hide_fs_id:
            self.root.after_cancel(self.hide_fs_id)
            self.hide_fs_id = None

    def _on_overlay_motion(self, event=None):
        """Shows UI controls and schedules them to hide after inactivity."""
        if self.countdown_window and self.countdown_window.winfo_exists():
            if hasattr(self, 'fs_button') and self.fs_button.winfo_exists():
                self.fs_button.place(relx=0.5, rely=0.95, anchor='s')
            if hasattr(self, 'close_button') and self.close_button.winfo_exists():
                self.close_button.place(relx=0.65, rely=0.95, anchor='s')
            if hasattr(self, 'sizegrip') and self.sizegrip and self.sizegrip.winfo_exists():
                self.sizegrip.place(relx=1.0, rely=1.0, anchor='se')

            if self.hide_fs_id:
                self.root.after_cancel(self.hide_fs_id)

            def hide_controls():
                if hasattr(self, 'fs_button') and self.fs_button.winfo_exists():
                    self.fs_button.place_forget()
                if hasattr(self, 'close_button') and self.close_button.winfo_exists():
                    self.close_button.place_forget()
                if hasattr(self, 'sizegrip') and self.sizegrip and self.sizegrip.winfo_exists():
                    self.sizegrip.place_forget()

            self.hide_fs_id = self.root.after(2500, hide_controls)

    def reset_timer(self):
        """Stops the current timer and clears all fields."""
        self._stop_timers()

        if self.countdown_window and self.countdown_window.winfo_exists():
            self.countdown_window.destroy()

        self.timer_running = False
        self.is_paused = False
        self.remaining_time = 0

        self.display_label.config(text='00:00:00', fg='#2980b9')
        self.start_button.config(state='normal')
        self.pause_button.config(state='disabled', text='⏸ PAUSE', bg='#f39c12')

        self.hour_entry.delete(0, tk.END)
        self.hour_entry.insert(0, '00')
        self.min_entry.delete(0, tk.END)
        self.min_entry.insert(0, '00')
        self.sec_entry.delete(0, tk.END)
        self.sec_entry.insert(0, '30')

    def _toggle_fullscreen(self):
        """Toggles the fullscreen state of the countdown window."""
        if not self.countdown_window or not self.countdown_window.winfo_exists():
            return

        screen_w = self.countdown_window.winfo_screenwidth()
        screen_h = self.countdown_window.winfo_screenheight()
        curr_w = self.countdown_window.winfo_width()

        if curr_w < screen_w:
            self._prev_geometry = self.countdown_window.geometry()
            self.countdown_window.geometry(f'{screen_w}x{screen_h}+0+0')
        else:
            prev_geo = getattr(self, '_prev_geometry', '1000x500+100+100')
            self.countdown_window.geometry(prev_geo)

    def _on_closing(self):
        """Safely stops the timer before closing the application."""
        self._stop_timers()
        if self.countdown_window and self.countdown_window.winfo_exists():
            self.saved_geometry = self.countdown_window.geometry()
        self._save_data()
        self.root.destroy()

    def _on_drag_start(self, event):
        """Records the initial mouse position for dragging."""
        self._drag_data['x'] = event.x_root
        self._drag_data['y'] = event.y_root

    def _on_drag_motion(self, event):
        """Calculates the delta and moves the window."""
        if not self.countdown_window or not self.countdown_window.winfo_exists():
            return
        deltax = event.x_root - self._drag_data['x']
        deltay = event.y_root - self._drag_data['y']
        new_x = self.countdown_window.winfo_x() + deltax
        new_y = self.countdown_window.winfo_y() + deltay

        self.countdown_window.geometry(f'+{new_x}+{new_y}')
        self.saved_geometry = self.countdown_window.geometry()
        self._drag_data['x'] = event.x_root
        self._drag_data['y'] = event.y_root

    def _on_window_resize(self, event):
        """Dynamically adjusts font sizes based on window dimensions."""
        if event.widget != self.countdown_window or (event.width == self._last_width and event.height == self._last_height):
            return

        if hasattr(self, '_resize_after_id') and self._resize_after_id:
            self.root.after_cancel(self._resize_after_id)

        target_w, target_h = event.width, event.height
        self._resize_after_id = self.root.after(10, lambda: self._perform_resize(target_w, target_h))

    def _perform_resize(self, width, height):
        """Actual layout adjustment logic separated for stability."""
        if not self.countdown_window or not self.countdown_window.winfo_exists():
            return

        self._last_width, self._last_height = width, height
        self.saved_geometry = self.countdown_window.geometry()

        # Dynamic font scaling relative to window size
        new_timer_size = max(20, int(height * 0.35))
        if self.countdown_label and self.countdown_label.winfo_exists():
            self.countdown_label.config(font=('Calibri', new_timer_size, 'bold'))

        if self.msg_label and self.msg_label.winfo_exists():
            user_base_size = self._get_msg_size()
            new_msg_size = int(user_base_size * (new_timer_size / 150))
            self.msg_label.config(font=('Calibri', max(12, new_msg_size)))

    def _set_dark_title_bar(self, window):
        """Forces the window title bar to use immersive dark mode on Windows."""
        try:
            window.update()
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value)
            )
        except (AttributeError, OSError, TypeError):
            pass

    def _open_portfolio(self):
        """Opens the developer portfolio URL in the default browser."""
        webbrowser.open('https://lightskyblue-wolverine-224124.hostingersite.com/')

    def _show_about_screen(self):
        """Displays the About dialog with app info, credits, and portfolio."""
        about = tk.Toplevel(self.root)
        about.title('About')
        about.geometry('500x400')
        about.resizable(False, False)
        about.configure(bg='black')
        about.transient(self.root)
        about.grab_set()

        content = tk.Frame(about, bg='black', padx=30, pady=20)
        content.pack(expand=True, fill='both')

        sunday_art = (
            "   _____ _   _ _   _ ____      _   __   __\n"
            "  / ___/| | | | \\ | |  _ \\    / \\  \\ \\ / /\n"
            "  \\__ \\ | | | |  \\| | | | |  / _ \\  \\ V / \n"
            " ___/ / | |_| | |\\  | |_/ /  / ___ \\  | |  \n"
            "/____/   \\___/|_| \\_|____/  /_/   \\_\\ |_|  "
        )
        tk.Label(
            content, text=sunday_art, font=('Consolas', 9, 'bold'), bg='black', fg='white', justify='center'
        ).pack(pady=(0, 10))

        tk.Label(
            content, text='A professional-grade countdown timer with custom messaging.',
            font=('Helvetica', 9), bg='black', fg='#bdc3c7', wraplength=400
        ).pack(pady=(15, 0))

        tk.Label(
            content, text='© 2026 ALL RIGHTS RESERVED', font=('Consolas', 10), bg='black', fg='#2980b9'
        ).pack(pady=(0, 20))

        portfolio_btn = tk.Button(
            content, text='🌐 Developer Portfolio', command=self._open_portfolio,
            bg='black', fg='#2980b9', font=('Helvetica', 10, 'underline'), relief='flat', cursor='hand2', activebackground='black', activeforeground='#3498db'
        )
        portfolio_btn.pack(pady=(0, 10))

        close_btn = tk.Button(
            content, text='Close', command=about.destroy,
            bg='#34495e', fg='white', font=('Helvetica', 9, 'bold'), relief='flat', padx=20, pady=5
        )
        close_btn.pack(pady=(10, 0))

if __name__ == '__main__':
    root = tk.Tk()
    app = CustomTimerApp(root)
    root.mainloop()