#!/usr/bin/env python3
"""GUI wrapper for Docker container runner."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from typing import List, Tuple, Optional
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


class DockerRunnerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Docker Runner GUI")
        self.root.geometry("900x700")
        
        # List to store command entries
        self.command_entries = []
        
        # Create main frames
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Commands section
        commands_frame = ttk.LabelFrame(main_frame, text="Docker Commands", padding="10")
        commands_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        commands_frame.columnconfigure(0, weight=1)
        
        # Commands list container with scrollbar
        self.commands_container = ttk.Frame(commands_frame)
        self.commands_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.commands_container.columnconfigure(0, weight=1)
        
        # Add command button
        add_button = ttk.Button(commands_frame, text="Add Command", command=self.add_command)
        add_button.grid(row=1, column=0, pady=(10, 0))
        
        # Add initial command
        self.add_command()
        
        # Control section
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Max workers input with larger font
        ttk.Label(control_frame, text="Max Workers:", font=('TkDefaultFont', 11)).grid(row=0, column=0, padx=(0, 5))
        self.max_workers_var = tk.StringVar(value="5")
        self.max_workers_entry = ttk.Entry(control_frame, textvariable=self.max_workers_var, width=10,
                                         font=('TkDefaultFont', 11))
        self.max_workers_entry.grid(row=0, column=1, padx=(0, 20))
        
        # Run button
        self.run_button = ttk.Button(control_frame, text="Run Docker Containers", command=self.run_containers)
        self.run_button.grid(row=0, column=2)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results text area with scrollbar and larger font
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15,
                                                     font=('TkDefaultFont', 11))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def add_command(self):
        """Add a new command entry."""
        command_frame = ttk.Frame(self.commands_container)
        command_frame.grid(row=len(self.command_entries), column=0, sticky=(tk.W, tk.E), pady=5)
        command_frame.columnconfigure(0, weight=1)
        
        # Command text widget with larger font
        command_text = tk.Text(command_frame, height=3, width=60, wrap=tk.WORD, 
                              font=('TkDefaultFont', 12))
        command_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Add scrollbar for text widget
        scrollbar = ttk.Scrollbar(command_frame, orient=tk.VERTICAL, command=command_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        command_text.config(yscrollcommand=scrollbar.set)
        
        # Set default value if this is the first command
        if not self.command_entries:
            command_text.insert(1.0, "Write a file called example.txt with 'Hello World'")
        
        # Delete button
        delete_button = ttk.Button(
            command_frame, 
            text="Delete", 
            command=lambda f=command_frame, t=command_text: self.delete_command(f, t)
        )
        delete_button.grid(row=0, column=2, padx=(5, 0))
        
        # Store reference
        self.command_entries.append(command_text)
        
    def delete_command(self, frame, text_widget):
        """Delete a command entry."""
        if len(self.command_entries) > 1:  # Keep at least one command
            frame.destroy()
            self.command_entries.remove(text_widget)
            # Re-grid remaining frames
            for i, child in enumerate(self.commands_container.winfo_children()):
                child.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5)
        else:
            messagebox.showwarning("Warning", "You must have at least one command.")
            
    def validate_max_workers(self):
        """Validate max workers input."""
        try:
            max_workers = int(self.max_workers_var.get())
            if max_workers < 1:
                raise ValueError("Max workers must be at least 1")
            return max_workers
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Max workers must be a positive integer: {e}")
            return None
            
    def run_containers(self):
        """Run Docker containers with the specified commands."""
        # Validate max workers
        max_workers = self.validate_max_workers()
        if max_workers is None:
            return
            
        # Get commands
        commands = []
        for text_widget in self.command_entries:
            # Get text from Text widget (excluding the trailing newline)
            text = text_widget.get(1.0, tk.END).strip()
            if text:
                commands.append(text)
        
        if not commands:
            messagebox.showwarning("No Commands", "Please enter at least one command.")
            return
            
        # Disable run button during execution
        self.run_button.config(state="disabled")
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Running {len(commands)} Docker containers with max {max_workers} workers...\n\n")
        self.results_text.update()
        
        # Run in separate thread to avoid blocking GUI
        thread = threading.Thread(
            target=self.run_containers_thread,
            args=(commands, max_workers),
            daemon=True
        )
        thread.start()
        
    def run_containers_thread(self, commands: List[str], max_workers: int):
        """Run containers in a separate thread."""
        try:
            results = self.run_containers_parallel(commands, max_workers)
            # Update GUI in main thread
            self.root.after(0, self.display_results, results)
        except Exception as e:
            self.root.after(0, self.display_error, str(e))
        finally:
            self.root.after(0, lambda: self.run_button.config(state="normal"))
            
    def run_docker_container(self, command: str) -> Tuple[str, Optional[str], Optional[str]]:
        """Run a single Docker container with the given command."""
        cmd = [
            "docker", "run",
            "-u", "coder",
            "-v", f"{os.getcwd()}:/home/coder/project",
            "-w", "/home/coder/project",
            "--rm", 
            "py-cl-7",
            "sh", "-c", f"echo '{command}' | npx @anthropic-ai/claude-code -p --dangerously-skip-permissions"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return (command, result.stdout.strip(), None)
        except subprocess.CalledProcessError as e:
            return (command, None, f"Error: {e.stderr.strip()}")
        except Exception as e:
            return (command, None, f"Error: {str(e)}")
            
    def run_containers_parallel(self, commands: List[str], max_workers: int) -> List[Tuple[str, Optional[str], Optional[str]]]:
        """Run multiple Docker containers in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_command = {
                executor.submit(self.run_docker_container, command): command 
                for command in commands
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_command):
                result = future.result()
                results.append(result)
                
        return results
        
    def display_results(self, results: List[Tuple[str, Optional[str], Optional[str]]]):
        """Display results in the GUI."""
        self.results_text.insert(tk.END, "="*60 + "\n")
        self.results_text.insert(tk.END, "DOCKER CONTAINER RESULTS\n")
        self.results_text.insert(tk.END, "="*60 + "\n\n")
        
        successful_runs = 0
        failed_runs = 0
        
        for i, (command, stdout, stderr) in enumerate(results, 1):
            if stdout:
                self.results_text.insert(tk.END, f"Container {i} - Command: {command}\n")
                self.results_text.insert(tk.END, f"  Status: SUCCESS\n")
                self.results_text.insert(tk.END, f"  Output: {stdout}\n")
                successful_runs += 1
            else:
                self.results_text.insert(tk.END, f"Container {i} - Command: {command}\n")
                self.results_text.insert(tk.END, f"  Status: FAILED\n")
                self.results_text.insert(tk.END, f"  Error: {stderr}\n")
                failed_runs += 1
            self.results_text.insert(tk.END, "\n")
            
        self.results_text.insert(tk.END, "="*60 + "\n")
        self.results_text.insert(tk.END, f"SUMMARY: {successful_runs} successful, {failed_runs} failed\n")
        self.results_text.insert(tk.END, "="*60 + "\n")
        
        # Scroll to bottom
        self.results_text.see(tk.END)
        
    def display_error(self, error_message: str):
        """Display error message in results."""
        self.results_text.insert(tk.END, f"\nERROR: {error_message}\n")
        self.results_text.see(tk.END)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = DockerRunnerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()