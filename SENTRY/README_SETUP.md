# SENTRY — Phase 0 & Phase 1 Setup

Follow these steps in order. Every command below goes into a **terminal**
(in VS Code: menu **Terminal → New Terminal**).

## Step 1 — Install the tools (one-time only)

1. **Python** — download from https://www.python.org/downloads/
   During install, **tick the box "Add Python to PATH"** before clicking Install. This step is the #1 cause of "python not recognized" errors — don't skip the checkbox.
2. **VS Code** — download from https://code.visualstudio.com/
3. **Git** — download from https://git-scm.com/downloads

Restart your laptop once after installing all three (clears up PATH issues).

## Step 2 — Open the project folder

1. Unzip the `SENTRY` folder I've given you anywhere you like (e.g. `Documents\SENTRY`).
2. Open VS Code → **File → Open Folder** → select that `SENTRY` folder.

## Step 3 — Create a virtual environment (keeps this project's packages separate from everything else on your PC)

In the VS Code terminal, run:

```bash
python -m venv venv
```

Then activate it:

**Windows (PowerShell):**
```bash
venv\Scripts\activate
```

You'll know it worked when you see `(venv)` at the start of the terminal line.

> If PowerShell blocks the activate script with a "running scripts is disabled" error, run this once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` then try activating again.

## Step 4 — Install the required package

```bash
pip install -r requirements.txt
```

## Step 5 — Run the app

```bash
python main.py
```

**What you should see:** a desktop window opens showing your full TOS dashboard, and the window's title bar changes to read:
`SENTRY — Hello from Python — bridge is working!`

That title-bar change is the proof — it means Python successfully talked to the page and back. If you see that, Phase 1 is complete and we move to Phase 2 (real database + wiring the journal to actual data).

## If something goes wrong

Copy the **exact error text** from the terminal and paste it back to me (whichever AI you're working with) along with `PROJECT_MASTER.md` — don't try to fix it yourself.

## When Phase 1 is confirmed working — commit it to GitHub

```bash
git init
git add .
git commit -m "Phase 1: SENTRY skeleton app — pywebview shell + dashboard loads + bridge confirmed"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```
(Replace `<your-username>` and `<repo-name>` with your actual GitHub username and the repo name you create on github.com — click "New repository" there first, leave it empty, no README/license, then use the URL it gives you.)
