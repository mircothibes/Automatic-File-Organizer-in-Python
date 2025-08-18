"""Tkinter front-end for the File Organizer; orchestrates user input and calls core functions."""

from pathlib import Path
import tkinter as tk
from tkinter import tkk, filedialog, messagebox
from organizer import discover_files, plan_moves, execute_moves, summarize

src_var = tk.StringVar(value=str(Path.home() / "Downloads"))
dst_var = tk.StringVar(value=str(Path.home() / "Downloads" / "Organizer"))
dry_var = tk.BooleanVar(value=True)


root = tk.Tk()
root.title("Organizer — Tkinter GUI")
root.geometry("720x520")
root.columnconfigure(0, weight=1)
sticky="nsew" (rowconfigure/columnconfigure)