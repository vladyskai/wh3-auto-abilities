---
name: python-desktop-gui
description: "Use when a script needs a friendly double-click window."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [gui, tkinter, desktop, ux, verification]
    category: software-development
    related_skills: [computer-use, systematic-debugging]
---

# A window over an existing tool

How to turn something that works from a terminal (a script you just wrote, or a shipped
CLI) into an app the user runs by clicking: choose an input, start, stop, read the
result. When the user does not read code, the window IS the deliverable, not a demo —
it must launch by double-click, explain each control in plain words, and never leave
them guessing whether it is running or whether their microphone is even working.

## Toolkit

- **Tkinter + ttk** (`import tkinter, tkinter.ttk`) is the default: ships with CPython,
  no installs, no build step, native widgets, instant start. A local HTML page is the
  fallback only when the user must share or embed the result.
- Launch with **`pythonw.exe`** (no console window) from a `.bat` beside the project:
  `"%~dp0.venv\Scripts\pythonw.exe" "%~dp0app_gui.py" %*`. Check both exist in the
  venv before promising a double-click app.
- Before creating the window: `ctypes.windll.shcore.SetProcessDpiAwareness(1)` and
  `ttk.Style().theme_use("vista")`, both inside `try/except`. Side benefit: in a
  DPI-aware process Tk widget coordinates ARE native pixels, so `winfo_*` arithmetic
  maps 1:1 onto screen coordinates for automation and layout assertions.

## Procedure

1. **Never reimplement the engine.** Import the working module and drive it; put the
   hooks the UI needs in the ENGINE, never in the GUI:
   - `stop_event: threading.Event` checked inside every long loop (the capture loop
     *and* any reconnect loop). A Stop button that cannot interrupt a blocking loop is
     a broken Stop button.
   - `level_callback(peak)` invoked from the audio/data callback, for an input meter.
   - text callbacks (`ui.interim(text)` / `.final(text)` / `.notice(text)`) replacing
     stdout printing, so the GUI receives clean events instead of scraping the console.
   - one entry point that accepts injection:
     `def main(argv=None, args=None, stop_event=None, ui=None)` — the CLI keeps
     `parse_args(argv)`, the GUI hands in a hand-built `argparse.Namespace`.
2. **Re-test the CLI after the refactor**: a cheap probe/entitlement check plus one
   short real run. This is the regression that catches a hook wired into the branch the
   GUI does not take.
3. **Threading model**: Tk owns the main thread. Run the engine in a
   `threading.Thread`; the worker only `queue.put(...)`s; the main thread drains with
   `root.after(100, drain)` and is the only code that touches a widget. Redirect
   `sys.stdout/stderr` to a queue-writing object for the duration of the run so engine
   logging lands in an "Activity" pane, and restore them in `finally`.
4. **Build the args namespace in one function** (`_build_args`) so buttons, tests and
   any script all exercise the same widget→args mapping. A missing attribute read as
   `args.x` deep inside the engine is the classic crash; keep optional hooks as
   `getattr(args, "x", None)` on the engine side.
5. **Layout that explains itself**: numbered steps in order of use, plain-language
   labels (define any jargon inline), a grey one-line note under each control stating
   the rule the backend enforces, Start/Stop plus a status label, results in a
   scrollable read-only `Text`, footer buttons that open the output folder and the last
   report (`os.startfile`). Every state change must update the status string — a status
   stuck on "Starting…" reads as a hung app even while it works.
6. **Meters are decibel-scaled** with a slow fall (`max(new, old * 0.9)`): map dBFS
   −60…0 to 0…100% and print the dBFS value beside the bar. A linear peak meter makes a
   live-but-quiet microphone read ~1% and look dead — precisely the failure the meter
   exists to prevent.
7. **Remember settings** in a small JSON file next to the app (device, selections,
   lists, mode): load at start, write on close and before a force-quit. Making the user
   re-pick the same options every launch is the fastest way to make a GUI unwelcome.
8. **Guard the exit and the buttons**: closing while a long job runs asks first, then
   sets the stop event and closes after a grace delay instead of yanking the window out
   from under the worker; Start/file buttons disable while running and re-enable when
   the worker reports done.
9. **Offer the non-interactive path too**: a "…instead, use a file" button with
   `filedialog.askopenfilename(..., filetypes=[...])` lets the user re-run something
   they already have without a terminal.

## Verify it without a human at the mouse

Tk draws its own widgets, so they are **absent from the Windows UIA / accessibility
tree** — element-index automation sees only the title bar, and pixel clicks are
fragile. So verify in this order:

1. **Confirm the pixels once**: launch it, capture the window, read the screenshot —
   layout, labels, defaults, disabled states, whether long text fits.
2. **Drive the logic off-screen**: build the same window object at an off-screen offset
   (`geometry("1000x780+3000+3000")`), call the handlers the buttons are bound to
   (`win.start()`, `win.stop()`), and pump the loop with `root.update()` in a `while`
   loop. Assert on real state: status variables, button `state`, transcript contents,
   files written to disk, whether a report was produced. `templates/gui_smoke_test.py`
   is the harness — copy it and edit the marked lines.
3. **Report what you did not test**: say the button callbacks were driven directly and
   the physical click is the user's first action, rather than implying a mouse test.
4. Expect this to find real bugs cheaply: the first run of this pattern caught a status
   label that never advanced past "Starting…" and a level meter reading 1.3% in a quiet
   room.

## Pitfalls

- **`pythonw.exe` swallows tracebacks.** Wrap the worker body in `try/except Exception`
  and push `traceback.format_exc()` into the Activity pane, or a background failure
  looks like a frozen window with no explanation.
- **Never touch a widget from the worker thread**, log lines included — queue all of it.
- **Do not let GUI formatting leak into saved files** (clock prefixes, wrapped lines):
  the writer belongs to the engine so the CLI and the GUI produce identical output.
- **Pixel clicks are the last resort, and never reuse coordinates**: recompute each time
  from `ClientToScreen(hwnd)` plus the widget's `winfo_*` geometry. Screenshot scale and
  window position can differ between captures, so a stale point silently misses.
- **Long jobs stay in the worker with progress in the status/Activity pane**; a modal
  "working…" dialog blocks the GUI and hides the log the user actually needs.

## Files

- `templates/gui_smoke_test.py` — off-screen harness: drives Start/Stop, prints widget
  centres (for computing click coordinates when that is genuinely the only route), and
  reports what the app produced.
