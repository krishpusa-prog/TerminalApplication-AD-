# Terminal Application AD - CLI Music Player

A lightweight, terminal-based audio player built with **Python**. Designed with a modular, event-driven architecture that completely separates the headless audio playback backend from the interactive terminal user interface (TUI).

---

## ✨ Features

- **Automatic Playlist & Directory Scanning**: Automatically loads all `.mp3`, `.wav`, and `.ogg` files in a folder or playlist.
- **Track Navigation**: Seamlessly switch tracks using keyboard shortcuts (<kbd>N</kbd>/<kbd>P</kbd> or Arrow Keys).
- **Decoupled Architecture**: Audio engine operates on background threads, ensuring the UI remains smooth and non-blocking.
- **Asynchronous TUI**: Built using **Textual** for rich, flicker-free terminal rendering with real-time progress indicators.
- **Robust Error Handling**: Gracefully handles missing files, invalid formats, and playback errors without crashing the app.

---

## 📂 Directory Structure

```text
CLI_MusicPlayer/
│
├── music/                   # Default audio directory (.mp3, .wav, .ogg)
│   └── sample.wav
├── src/
│   └── player/
│       ├── __init__.py
│       ├── main.py          # Application entry point
│       ├── audio.py         # Headless audio engine (pygame wrapper)
│       ├── controller.py    # Event & state controller bridge
│       ├── events.py        # Shared event types & dataclasses
│       │
│       └── ui/
│           ├── __init__.py
│           ├── app.py       # Textual UI app & layout
│           └── widgets.py   # Custom UI components
│
├── tests/                   # Unit & integration tests
├── .gitignore
├── README.md
├── pyproject.toml
├── setup.py
└── requirements.txt
```

---

## ⚙️ Prerequisites

- **Python 3.9+**
- Tested on macOS, Linux, and Windows terminal environments.

---

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/krishpusa-prog/TerminalApplication-AD-.git
   cd TerminalApplication-AD-
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

---

## 🎵 Usage

### Play all songs in the `music/` folder:
```bash
python -m player.main
# or
python -m player.main music/
```

### Play a specific file:
```bash
python -m player.main music/song.mp3
```

### Play multiple files:
```bash
python -m player.main song1.mp3 song2.mp3 song3.wav
```

---

## ⌨️ Controls & Keybindings

| Keybinding | Action | Description |
| :--- | :--- | :--- |
| <kbd>Space</kbd> | **Play / Pause** | Toggles playback between playing and paused states. |
| <kbd>N</kbd> or <kbd>→</kbd> | **Next Track** | Skips to the next track in the playlist. |
| <kbd>P</kbd> or <kbd>←</kbd> | **Prev Track** | Returns to the previous track in the playlist. |
| <kbd>S</kbd> | **Stop** | Stops playback and resets the progress bar. |
| <kbd>Q</kbd> | **Quit** | Gracefully stops audio playback and exits the app. |

---

## 🧪 Running Unit Tests

Run the full test suite with pytest:

```bash
pytest
```