#!/usr/bin/env python3
"""
Bit Buddy Desktop GUI - Chat window for your personal file companion
"""

import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from enhanced_buddy import EnhancedBitBuddy


class BuddyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bit Buddy - Your Personal File Companion")
        self.root.geometry("900x700")

        # Initialize buddy (will be loaded or created)
        self.buddy = None
        self.buddy_dir = Path.home() / ".bit_buddies" / "default"
        self.watch_dir = Path.home() / "Documents"

        # Create UI
        self.create_widgets()

        # Try to load existing buddy
        self.load_or_create_buddy()

    def create_widgets(self):
        # Header with buddy info
        header_frame = tk.Frame(self.root, bg="#2C3E50", height=80)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        self.buddy_name_label = tk.Label(
            header_frame,
            text="🤖 Bit Buddy",
            font=("Arial", 18, "bold"),
            bg="#2C3E50",
            fg="white",
        )
        self.buddy_name_label.pack(pady=10)

        self.status_label = tk.Label(
            header_frame,
            text="Initializing...",
            font=("Arial", 10),
            bg="#2C3E50",
            fg="#ECF0F1",
        )
        self.status_label.pack()

        # Chat area
        chat_frame = tk.Frame(self.root)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#ECF0F1",
            fg="#2C3E50",
            state="disabled",
        )
        self.chat_display.pack(fill="both", expand=True)

        # Configure tags for chat formatting
        self.chat_display.tag_config("user", foreground="#3498DB", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("buddy", foreground="#E74C3C", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("aside", foreground="#95A5A6", font=("Arial", 9, "italic"))

        # Input area
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.input_field = tk.Entry(input_frame, font=("Arial", 12))
        self.input_field.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", self.send_message)

        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg="#3498DB",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
        )
        self.send_button.pack(side="right")

        # Control panel
        control_frame = tk.Frame(self.root, bg="#34495E", height=50)
        control_frame.pack(fill="x", side="bottom")
        control_frame.pack_propagate(False)

        tk.Button(
            control_frame,
            text="⚙️ Settings",
            command=self.show_settings,
            bg="#34495E",
            fg="white",
            bd=0,
        ).pack(side="left", padx=10, pady=10)

        tk.Button(
            control_frame,
            text="🔄 Rescan Files",
            command=self.rescan_files,
            bg="#34495E",
            fg="white",
            bd=0,
        ).pack(side="left", padx=10, pady=10)

        tk.Button(
            control_frame,
            text="👤 Personality",
            command=self.show_personality,
            bg="#34495E",
            fg="white",
            bd=0,
        ).pack(side="left", padx=10, pady=10)

    def load_or_create_buddy(self):
        """Load existing buddy or create new one"""
        try:
            if self.buddy_dir.exists():
                # Load existing
                self.buddy = EnhancedBitBuddy(self.buddy_dir, self.watch_dir, model_path=None)
                personality = self.buddy.personality
                self.buddy_name_label.config(text=f"🤖 {personality.name}")
                self.status_label.config(text=f"Ready • Watching: {self.watch_dir.name}")
                self.add_chat_message(
                    "system",
                    f"Welcome back! {personality.name} is ready to help.",
                )
            else:
                # Create new buddy
                self.setup_new_buddy()
        except Exception as e:
            messagebox.showerror(
                "Error",
                (f"Failed to initialize buddy: {str(e)}\n\n" "Please check your installation."),
            )

    def setup_new_buddy(self):
        """First-time setup wizard"""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Welcome to Bit Buddy!")
        setup_window.geometry("500x400")
        setup_window.grab_set()

        tk.Label(
            setup_window,
            text="🎉 Welcome to Bit Buddy!",
            font=("Arial", 16, "bold"),
        ).pack(pady=20)

        tk.Label(
            setup_window,
            text="Let's set up your personal file companion.",
            font=("Arial", 11),
        ).pack()

        # Name input
        tk.Label(
            setup_window,
            text="\nWhat would you like to name your buddy?",
            font=("Arial", 10),
        ).pack(pady=(20, 5))

        name_var = tk.StringVar(value="Pixel")
        name_entry = tk.Entry(setup_window, textvariable=name_var, font=("Arial", 12), width=30)
        name_entry.pack()

        # Folder selection
        tk.Label(
            setup_window,
            text="\nWhich folder should your buddy watch?",
            font=("Arial", 10),
        ).pack(pady=(20, 5))

        folder_var = tk.StringVar(value=str(self.watch_dir))
        folder_frame = tk.Frame(setup_window)
        folder_frame.pack()

        tk.Entry(
            folder_frame,
            textvariable=folder_var,
            font=("Arial", 10),
            width=35,
            state="readonly",
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            folder_frame,
            text="Browse...",
            command=lambda: folder_var.set(filedialog.askdirectory(initialdir=str(self.watch_dir))),
        ).pack(side="left")

        def finish_setup():
            name = name_var.get().strip() or "Pixel"
            watch = Path(folder_var.get())

            if not watch.exists():
                messagebox.showerror("Error", "Selected folder doesn't exist!")
                return

            # Create buddy
            try:
                self.watch_dir = watch
                self.buddy = EnhancedBitBuddy(self.buddy_dir, self.watch_dir, model_path=None)
                self.buddy.personality.name = name
                self.buddy._save_personality(self.buddy.personality)

                self.buddy_name_label.config(text=f"🤖 {name}")
                self.status_label.config(text=f"Ready • Watching: {self.watch_dir.name}")

                setup_window.destroy()

                # Welcome message
                response = self.buddy.hello()
                self.add_chat_message("buddy", response["message"])
                if "aside" in response:
                    self.add_chat_message("aside", f"({response['aside']})")

            except Exception as e:
                messagebox.showerror("Error", f"Setup failed: {str(e)}")

        tk.Button(
            setup_window,
            text="Create My Buddy!",
            command=finish_setup,
            bg="#3498DB",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
        ).pack(pady=30)

    def add_chat_message(self, role, text):
        """Add message to chat display"""
        self.chat_display.config(state="normal")

        if role == "user":
            self.chat_display.insert("end", "You: ", "user")
            self.chat_display.insert("end", f"{text}\n\n")
        elif role == "buddy":
            self.chat_display.insert("end", f"{self.buddy.personality.name}: ", "buddy")
            self.chat_display.insert("end", f"{text}\n")
        elif role == "aside":
            self.chat_display.insert("end", f"  {text}\n\n", "aside")
        elif role == "system":
            self.chat_display.insert("end", f"ℹ️  {text}\n\n", "aside")

        self.chat_display.config(state="disabled")
        self.chat_display.see("end")

    def send_message(self, event=None):
        """Send user message to buddy"""
        message = self.input_field.get().strip()
        if not message or not self.buddy:
            return

        # Clear input
        self.input_field.delete(0, "end")

        # Display user message
        self.add_chat_message("user", message)

        # Get buddy response
        self.status_label.config(text="Thinking...")
        self.root.update()

        try:
            response = self.buddy.ask(message)
            self.add_chat_message("buddy", response["answer"])

            if "aside" in response:
                self.add_chat_message("aside", f"({response['aside']})")

            # Show file results if any
            if response.get("file_results"):
                files = response["file_results"][:3]  # Show top 3
                if files:
                    file_list = "\n".join([f"  📄 {f['name']}" for f in files])
                    self.add_chat_message("aside", f"Relevant files:\n{file_list}")

        except Exception as e:
            self.add_chat_message("system", f"Oops! Something went wrong: {str(e)}")
        finally:
            self.status_label.config(text=f"Ready • Watching: {self.watch_dir.name}")

    def rescan_files(self):
        """Trigger file rescan"""
        if not self.buddy:
            return

        self.status_label.config(text="Scanning files...")
        self.root.update()

        try:
            self.buddy.rag.index_files()
            self.add_chat_message("system", "✓ File scan complete! I've updated my knowledge.")
        except Exception as e:
            self.add_chat_message("system", f"Scan failed: {str(e)}")
        finally:
            self.status_label.config(text=f"Ready • Watching: {self.watch_dir.name}")

    def show_personality(self):
        """Show personality details"""
        if not self.buddy:
            return

        p = self.buddy.personality
        info = f"""
🎭 Personality Profile

Name: {p.name}
Humor: {p.humor}/10
Curiosity: {p.curiosity}/10
Formality: {p.formality}/10
Temperature: {p.temperature}

Specialties: {', '.join(p.specialties)}

Total Experience: {len(p.experience_log)} events
"""
        messagebox.showinfo("Personality", info)

    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.grab_set()

        tk.Label(
            settings_window,
            text="⚙️ Bit Buddy Settings",
            font=("Arial", 14, "bold"),
        ).pack(pady=20)

        # Watch folder
        tk.Label(settings_window, text="Watch Folder:", font=("Arial", 10)).pack(
            anchor="w", padx=20, pady=(10, 5)
        )

        folder_frame = tk.Frame(settings_window)
        folder_frame.pack(fill="x", padx=20)

        folder_var = tk.StringVar(value=str(self.watch_dir))
        tk.Entry(
            folder_frame,
            textvariable=folder_var,
            font=("Arial", 10),
            state="readonly",
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(
            folder_frame,
            text="Change",
            command=lambda: self.change_watch_folder(folder_var),
        ).pack(side="left")

        tk.Button(
            settings_window,
            text="Close",
            command=settings_window.destroy,
            padx=20,
        ).pack(pady=20)

    def change_watch_folder(self, folder_var):
        """Change the watched folder"""
        new_folder = filedialog.askdirectory(initialdir=str(self.watch_dir))
        if new_folder:
            self.watch_dir = Path(new_folder)
            folder_var.set(str(self.watch_dir))
            if self.buddy:
                self.buddy.watch_dir = self.watch_dir
                self.status_label.config(text=f"Ready • Watching: {self.watch_dir.name}")
                self.add_chat_message("system", f"Now watching: {self.watch_dir}")


def main():
    root = tk.Tk()
    app = BuddyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
