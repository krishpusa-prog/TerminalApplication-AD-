# TerminalApplication-AD-
CLI Music Player
A lightweight, terminal-based audio player built with Python. Designed with a modular, event-driven architecture that completely separates the headless audio playback backend from the interactive terminal user interface (TUI).
Features
Decoupled Architecture: Audio engine operates on background threads, ensuring the UI remains smooth and non-blocking.
Asynchronous TUI: Built using Textual for rich, flicker-free terminal rendering with keyboard shortcuts.
Robust Error Handling: Gracefully handles missing files, invalid formats, and playback errors without crashing the app.
Lightweight Audio Engine: Native backend powered by pygame.mixer with built-in state monitoring.
Directory Structure
Plaintext
cli_music_player/
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
└── pyproject.toml
Prerequisites
Python 3.9+
Tested on macOS, Linux, and Windows terminal environments.
Installation
Clone the repository:
Bash
git clone https://github.com/your-username/cli-music-player.git
cd cli-music-player
Create and activate a virtual environment:
Bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install dependencies:
Bash
pip install pygame textual mutagen
Usage
Run the music player by passing the path to an audio file (.mp3, .wav, .ogg):
Bash
python -m player.main path/to/song.mp3
Keybindings
Key	Action
Space	Play / Pause track
S	Stop playback and reset position
↑ / ↓	Increase / Decrease volume
M	Toggle Mute
Q	Quit player
Architecture Overview
The project uses an Event-Driven Observer Pattern to isolate terminal rendering from audio processing:
[ User Inputs ] ---> [ Textual UI App ] --(Commands)--> [ Player Controller ]
                           ^                                    |
                           |                                    v
                     (UI Updates)                       [ Audio Engine ]
                           |                           (pygame / Background Thread)
                           +---------(Events)-----------+
audio.py: Pure Python playback logic. Has zero knowledge of the terminal UI.
app.py: Async event-loop interface using Textual. Updates controls and progress indicators safely using rendering guards to eliminate terminal redraw flicker.
License
Distributed under the MIT License. See LICENSE for more information.