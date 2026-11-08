"""Off-screen harness for a Tkinter window: drive it, then check real state.

Copy this next to the app, edit the EDIT lines, and run it with the project's own
interpreter. It answers the question desktop automation cannot: did the button
handlers actually do the work?

Two parts:
  * build / widget_geometry - inspect the window's own geometry (client coordinates)
  * drive_start_stop        - press Start/Stop and pump the Tk loop, then report state
"""
import ctypes
import sys
import time
from pathlib import Path

import tkinter as tk

PROJECT = Path(r"C:\path\to\project")            # EDIT
sys.path.insert(0, str(PROJECT))
import app_gui as gui                             # EDIT: module holding the window class

WINDOW_CLASS = gui.AppWindow                      # EDIT: the window class
CLIENT_SIZE = "1000x780"                          # EDIT: match the app's geometry
OFFSCREEN = "+3000+3000"                          # mapped, but out of the way
RUN_SECONDS = 12                                  # how long to "press Start" for
FINISH_TIMEOUT = 180                              # how long to wait after Stop


def build():
    root = tk.Tk()
    root.geometry(f"{CLIENT_SIZE}{OFFSCREEN}")
    win = WINDOW_CLASS(root)
    root.update()
    root.update_idletasks()
    return root, win


def widget_geometry(root, widgets: dict, window_title: str = "") -> dict:
    """Print each widget's centre in client coordinates.

    In a DPI-aware process these equal native pixels, so adding the window's client
    origin (from ClientToScreen) gives a screen point for a click. Recompute the
    origin every time you act: window position and screenshot scale can differ.
    """
    centres = {}
    for name, widget in widgets.items():
        x = widget.winfo_rootx() - root.winfo_rootx() + widget.winfo_width() // 2
        y = widget.winfo_rooty() - root.winfo_rooty() + widget.winfo_height() // 2
        centres[name] = (x, y)
        print(f"{name:16} centre=({x},{y}) size={widget.winfo_width()}x{widget.winfo_height()}")
    if window_title and sys.platform == "win32":
        from ctypes import wintypes
        hwnd = ctypes.windll.user32.FindWindowW(None, window_title)
        if hwnd:
            point = wintypes.POINT(0, 0)
            ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(point))
            print(f"client origin on screen: {point.x},{point.y} — add this to a centre above")
        else:
            print("window not found by title — is the app running?")
    return centres


def drive_start_stop(win, root) -> None:
    """Press Start, pump the loop, press Stop, wait for the worker to finish."""
    print("--- Start ---")
    win.start()
    started = time.time()
    peak_note = ""
    while time.time() - started < RUN_SECONDS:
        root.update()
        if hasattr(win, "var_level"):
            peak_note = f"level peaked at {win.var_level.get():.0f}%"
        time.sleep(0.02)
    print("status during run :", win.var_status.get())
    print("start button      :", win.start_button["state"])
    print("stop button       :", win.stop_button["state"])
    if peak_note:
        print(peak_note)

    print("--- Stop ---")
    win.stop()
    while getattr(win, "running", False) and time.time() - started < RUN_SECONDS + FINISH_TIMEOUT:
        root.update()
        time.sleep(0.02)
    print("final status      :", win.var_status.get())
    print("start back to     :", win.start_button["state"])


def main() -> int:
    root, win = build()
    widget_geometry(root, {"start": win.start_button, "stop": win.stop_button},
                    window_title="")                      # EDIT: the window's title
    drive_start_stop(win, root)

    # EDIT: assert on what the app should have produced.
    for attribute in ("last_report", "last_live"):
        print(f"{attribute}: {getattr(win, attribute, None)}")
    if hasattr(win, "transcript"):
        text = win.transcript.get("1.0", "end").strip()
        print("transcript pane   :", text[:200] or "(empty)")
    if hasattr(win, "log"):
        print("--- activity pane ---")
        print(win.log.get("1.0", "end").strip())
    root.destroy()
    return 0


if __name__ == "__main__":
    sys.exit(main())
