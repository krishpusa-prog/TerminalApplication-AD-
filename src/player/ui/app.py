from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static


class MusicPlayerApp(App[None]):
    """Textual TUI Application Shell."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("space", "toggle_play", "Play/Pause"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Music Player Initialized", id="main_view")
        yield Footer()

    def action_toggle_play(self) -> None:
        pass