"""
Graphical User Interface (GUI) for the File Organizer.

This module provides a Tkinter-based front-end that orchestrates user input
and delegates all organizing logic to the core package functions:
`discover_files`, `plan_moves`, `execute_moves`, and `summarize`.

User flow:
1) Select Source and Destination folders (via read-only entries + Browse buttons).
2) Optionally enable "Dry-run" to preview the plan without moving files.
3) Click "Run" to list the plan; if not in Dry-run mode, confirm and execute.
4) Review the live log and the category summary at the bottom.

The GUI does not re-implement business logic; it only coordinates I/O and UX.
"""


from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox  # <- ttk correto
from organizer import discover_files, plan_moves, execute_moves, summarize


def main() -> None:
    """
    Launch the Tkinter GUI for the File Organizer.

    Responsibilities
    ----------------
    - Create the root window and bind Tkinter variables to the widgets.
    - Wire UI event handlers (browse source/destination, run action).
    - Provide a scrollable output area for the live plan/log.
    - Display a summary of files grouped by category.
    - Coordinate Dry-run vs. actual execution (with confirmation).

    Notes
    -----
    - All heavy lifting (scan, planning, moving, summarizing) is delegated to
      the core functions imported from the `organizer` package.
    - The function blocks UI controls during execution only minimally; for
      very large folders, consider using threading in future iterations.
    """
    # Root window
    root = tk.Tk()
    root.title("Organizer — Tkinter GUI")
    root.geometry("720x520")
    # --- State variables -----------------------------------------------------
    # Tk variables must be created after root; they hold user-controlled state.
    src_var = tk.StringVar(value=str(Path.home() / "Downloads"))
    dst_var = tk.StringVar(value=str(Path.home() / "Downloads" / "Organized"))
    dry_var = tk.BooleanVar(value=True)

    # --- Handlers ------------------------------------------------------------
    def on_browse_src() -> None:
        """
        Open a directory-chooser dialog and update the Source path field.

        Behavior
        --------
        - Opens a system dialog (`filedialog.askdirectory`).
        - If the user chooses a folder, updates `src_var` accordingly.
        """
        path = filedialog.askdirectory()
        if path:
            src_var.set(path)

    def on_browse_dst() -> None:
        """
        Open a directory-chooser dialog and update the Destination path field.
        Behavior
        --------
        - Opens a system dialog (`filedialog.askdirectory`).
        - If the user chooses a folder, updates `dst_var` accordingly.
        """
        path = filedialog.askdirectory()
        if path:
            dst_var.set(path)

    def clear_output() -> None:
        """
         Clear the log/output text area.

        Notes
        -----
        - Temporarily switches the text widget to 'normal' state to edit,
          then back to 'disabled' to avoid user typing.
        """
        txt_output.configure(state="normal")
        txt_output.delete("1.0", "end")
        txt_output.configure(state="disabled")

    def append_output(line: str) -> None:
        """
        Append a single line to the log/output text area.

        Parameters
        ----------
        line : str
            The message to append to the log window.

        Notes
        -----
        - Auto-scrolls to the end to keep the latest messages visible.
        - Keeps the widget read-only for user interactions.
        """
        txt_output.configure(state="normal")
        txt_output.insert("end", line + "\n")
        txt_output.see("end")
        txt_output.configure(state="disabled")

    def set_status(text: str) -> None:
        """
        Update the status bar text at the bottom of the window.

        Parameters
        ----------
        text : str
            Human-readable status message (e.g., 'Scanning...', 'Done').
        """
        lbl_status.configure(text=text)

    def on_run() -> None:
        """
         Execute the organize action: plan and optionally move files.

        Flow
        ----
        1) Clears previous output and shows "Scanning..." in the status bar.
        2) Validates the source folder and ensures the destination exists.
        3) Calls `discover_files` and `plan_moves` to build the plan.
        4) Prints the full plan (source -> destination [Category]) to the log.
        5) Shows a summary (category -> count) beneath the log.
        6) If Dry-run is enabled, stops here with "Dry-run complete".
        7) Otherwise, asks for user confirmation and calls `execute_moves`.
        8) On success, reports completion via status bar and message box.

        Error Handling
        --------------
        - Displays a message box for invalid source directories or unexpected
          exceptions, and sets the status to "Error".

        Notes
        -----
        - This handler intentionally keeps the UI logic separate from the
          underlying file operations implemented in the core module.
        """
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
    