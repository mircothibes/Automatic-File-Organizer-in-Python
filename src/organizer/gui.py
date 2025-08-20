"""
Graphical User Interface (GUI) for the File Organizer.

This module provides a **Tkinter-based front-end** for the File Organizer package.  
It allows users to interact with the organizer visually, without requiring command-line
knowledge. The GUI orchestrates user input, builds the movement plan, and executes file 
organization using the core functions defined in :mod:`organizer.core`.

Main Features
-------------
- Source folder selection (read-only field + Browse button).
- Destination folder selection (read-only field + Browse button).
- Optional "dry-run" mode (preview of planned file moves, without applying changes).
- Execution of the organization plan, moving files into categorized subfolders.
- Visual feedback with a summary of moved files, grouped by category.

Technical Notes
---------------
- Built with **Tkinter**, Python’s standard GUI toolkit.
- Uses `StringVar` and `BooleanVar` variables bound to input widgets for state management.
- Leverages the following core functions:
  - :func:`discover_files` – lists candidate files from the source directory.
  - :func:`plan_moves` – generates a move plan, including conflict resolution.
  - :func:`execute_moves` – executes the planned file movements.
  - :func:`summarize` – produces a category-based summary after execution.

How It Works
------------
1. The user selects a **source** folder and a **destination** folder.
2. The program scans the source for files, then computes their destinations based on extension.
3. If "dry-run" is checked, the planned moves and summary are displayed without touching the files.
4. Otherwise, the files are physically moved to categorized subfolders, and a summary is displayed.

Example Usage
-------------
Run the GUI with:

    $ python -m organizer.gui

Typical user workflow:
1. Launch the program.
2. Browse for the source and destination folders.
3. (Optional) Enable "dry-run" to preview the plan.
4. Click **Organize** to execute.
5. Review the summary of organized files.

This front-end complements the command-line interface (:mod:`organizer.cli`) by providing
a more intuitive experience for end-users.
"""


from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox  # <- ttk correto
from organizer import discover_files, plan_moves, execute_moves, summarize


def main() -> None:
    root = tk.Tk()
    root.title("Organizer — Tkinter GUI")
    root.geometry("720x520")
    # --- State variables -----------------------------------------------------
    src_var = tk.StringVar(value=str(Path.home() / "Downloads"))
    dst_var = tk.StringVar(value=str(Path.home() / "Downloads" / "Organized"))
    dry_var = tk.BooleanVar(value=True)

    # --- Handlers ------------------------------------------------------------
    def on_browse_src() -> None:
        path = filedialog.askdirectory()
        if path:
            src_var.set(path)

    def on_browse_dst() -> None:
        path = filedialog.askdirectory()
        if path:
            dst_var.set(path)

    def clear_output() -> None:
        txt_output.configure(state="normal")
        txt_output.delete("1.0", "end")
        txt_output.configure(state="disabled")

    def append_output(line: str) -> None:
        txt_output.configure(state="normal")
        txt_output.insert("end", line + "\n")
        txt_output.see("end")
        txt_output.configure(state="disabled")

    def set_status(text: str) -> None:
        lbl_status.configure(text=text)

    def on_run() -> None:
        try:
            clear_output()
            set_status("Scanning...")

            src = Path(src_var.get()).expanduser().resolve()
            dst = Path(dst_var.get()).expanduser().resolve()

            if not src.exists() or not src.is_dir():
                messagebox.showerror("Invalid source", f"Folder not found or not a directory:\n{src}")
                set_status("Ready")
                return

            dst.mkdir(parents=True, exist_ok=True)

            files = discover_files(src)
            if not files:
                append_output("No files found.")
                set_status("Ready")
                return

            plan = plan_moves(files, dst)

            # Show plan always
            for s, d in plan:
                category = d.parent.name
                append_output(f"{s} -> {d} [{category}]")

            # Summary
            sm = summarize(plan)
            lbl_summary.configure(text="Summary: " + " | ".join(f"{k}: {v}" for k, v in sm.items()))

            if dry_var.get():
                set_status("Dry-run complete")
                return

            # Confirm and execute
            if not messagebox.askyesno("Confirm", "Move files now?"):
                set_status("Cancelled")
                return

            set_status("Moving...")
            execute_moves(plan)
            set_status("Done")
            messagebox.showinfo("Completed", "Files moved successfully.")

        except Exception as e:
            messagebox.showerror("Unexpected error", str(e))
            set_status("Error")

    # --- UI ------------------------------------------------------------------
    
    root.title("Organizer — Tkinter GUI")
    root.geometry("720x520")

    # make the single main column/row expandable
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frame = ttk.Frame(root, padding=8)
    frame.grid(row=0, column=0, sticky="nsew")

    # grid expansion inside the frame
    frame.columnconfigure(1, weight=1)   # entry column grows
    frame.rowconfigure(3, weight=1)      # output area grows

    # Row 0: Source
    label_src = ttk.Label(frame, text="Source")
    entry_src = ttk.Entry(frame, textvariable=src_var, state="readonly")
    btn_browse_src = ttk.Button(frame, text="Browse…", command=on_browse_src)

    label_src.grid(row=0, column=0, sticky="w", padx=4, pady=6)
    entry_src.grid(row=0, column=1, sticky="ew", padx=4, pady=6)
    btn_browse_src.grid(row=0, column=2, padx=4, pady=6)

    # Row 1: Destination
    label_dst = ttk.Label(frame, text="Destination")
    entry_dst = ttk.Entry(frame, textvariable=dst_var, state="readonly")
    btn_browse_dst = ttk.Button(frame, text="Browse…", command=on_browse_dst)

    label_dst.grid(row=1, column=0, sticky="w", padx=4, pady=6)
    entry_dst.grid(row=1, column=1, sticky="ew", padx=4, pady=6)
    btn_browse_dst.grid(row=1, column=2, padx=4, pady=6)

    # Row 2: Options + Run
    chk_dry = ttk.Checkbutton(frame, text="Dry-run (simulate only)", variable=dry_var)
    btn_run = ttk.Button(frame, text="Run", command=on_run)

    chk_dry.grid(row=2, column=0, sticky="w", padx=4, pady=6, columnspan=2)
    btn_run.grid(row=2, column=2, sticky="e", padx=4, pady=6)

    # Row 3: Output
    txt_output = tk.Text(frame, wrap="none", height=12, state="disabled")
    scroll_y = ttk.Scrollbar(frame, orient="vertical", command=txt_output.yview)
    txt_output.configure(yscrollcommand=scroll_y.set)

    txt_output.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=(4,0), pady=(6,2))
    scroll_y.grid(row=3, column=2, sticky="ns", padx=(4,4), pady=(6,2))

    # Row 4: Summary
    lbl_summary = ttk.Label(frame, text="Summary: —")
    lbl_summary.grid(row=4, column=0, columnspan=3, sticky="w", padx=4, pady=(0,6))

    # Row 5: Status bar
    lbl_status = ttk.Label(frame, text="Ready", anchor="w")
    lbl_status.grid(row=5, column=0, columnspan=3, sticky="ew", padx=4)

    root.mainloop()


if __name__ == "__main__":
    main()
    