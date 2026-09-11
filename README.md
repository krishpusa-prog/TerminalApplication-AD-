# Terminal Application AD - CLI Music Player

A lightweight, terminal-based audio player built with **Python**. Designed with a modular, event-driven architecture that completely separates the headless audio playback backend from the interactive terminal user interface (TUI).

---

## ✨ Features

- **Decoupled Architecture**: Audio engine operates on background threads, ensuring the UI remains smooth and non-blocking.
- **Asynchronous TUI**: Built using **Textual** for rich, flicker-free terminal rendering with keyboard shortcuts.
- **Robust Error Handling**: Gracefully handles missing files, invalid formats, and playback errors without crashing the app.
- **Lightweight Audio Engine**: Native backend powered by `pygame.mixer` with built-in state monitoring.

---

## 📂 Directory Structure

```text
CLI_MusicPlayer/
│
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
   ```

---

## 🎵 Usage

Run the music player by passing the path to an audio file (`.mp3`, `.wav`, `.ogg`):

```bash
python -m player.main path/to/song.mp3
```

---

## ⌨️ Keybindings

| Key | Action |
| :--- | :--- |
| <kbd>Space</kbd> | Play / Pause track |
| <kbd>S</kbd> | Stop playback and reset position |
| <kbd>Q</kbd> | Quit player |

---

## 🏗️ Architecture Overview

The project uses an **Event-Driven Observer Pattern** to isolate terminal rendering from audio processing:

```text
[ User Inputs ] ---> [ Textual UI App ] --(Commands)--> [ Player Controller ]
                           ^                                    |
                           |                                    v
                     (UI Updates)                       [ Audio Engine ]
                           |                           (pygame / Background Thread)
                           +---------(Events)-----------+
```

- **[audio.py](file:///Users/kaustubh/Desktop/PROJECTS/CLI_MusicPlayer/src/player/audio.py)**: Pure Python playback logic. Has zero knowledge of the terminal UI.
- **[app.py](file:///Users/kaustubh/Desktop/PROJECTS/CLI_MusicPlayer/src/player/ui/app.py)**: Async event-loop interface using Textual. Updates controls and progress indicators safely using rendering guards to eliminate terminal redraw flicker.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.