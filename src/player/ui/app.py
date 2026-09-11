import os
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Center, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, ProgressBar, Static

from player.audio import AudioPlayer, PlaybackState


class TrackCard(Static):
    """Widget to display track title and playback status."""

    status_text = reactive("STOPPED")
    track_title = reactive("No track loaded")

    def render(self) -> str:
        return f"[bold cyan]Track:[/bold cyan] {self.track_title}\n[bold yellow]Status:[/bold yellow] {self.status_text}"


class MusicPlayerApp(App[None]):
    """Textual CLI Music Player Interface."""

    CSS = """
    Screen {
        align: center middle;
    }

    #player_container {
        width: 60;
        height: 13;
        border: solid green;
        padding: 1 2;
    }

    TrackCard {
        margin-bottom: 1;
        height: 3;
    }

    ProgressBar {
        width: 100%;
        margin-bottom: 1;
    }

    #time_label {
        content-align: center middle;
        width: 100%;
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("space", "toggle_play", "Play/Pause"),
        ("s", "stop", "Stop"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, audio_file: Optional[str] = None) -> None:
        super().__init__()
        self.audio_file = audio_file
        self.player = AudioPlayer(
            on_state_change=self._on_audio_state_change,
            on_error=self._on_audio_error,
        )
        self.track_duration: float = 180.0  # Placeholder duration (3:00) until metadata parsing is added

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Center():
            with Vertical(id="player_container"):
                yield TrackCard(id="track_card")
                yield ProgressBar(total=100, show_percentage=False, id="progress_bar")
                yield Label("00:00 / 00:00", id="time_label")
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts. Sets up timers and loads track if provided."""
        # UI timer loop: updates progress 10 times per second safely on the UI thread
        self.set_interval(0.1, self._update_progress)

        if self.audio_file:
            track_name = os.path.basename(self.audio_file)
            card = self.query_one(TrackCard)
            card.track_title = track_name
            self.player.load(self.audio_file)

    def _update_progress(self) -> None:
        """Polls current position and updates progress bar + timer label."""
        if self.player.state == PlaybackState.PLAYING:
            current_sec = self.player.get_position()
            
            # Update Progress Bar
            progress_pct = min(100.0, (current_sec / self.track_duration) * 100)
            self.query_one(ProgressBar).progress = progress_pct

            # Update Time Label (MM:SS / MM:SS)
            curr_str = f"{int(current_sec // 60):02d}:{int(current_sec % 60):02d}"
            dur_str = f"{int(self.track_duration // 60):02d}:{int(self.track_duration % 60):02d}"
            self.query_one("#time_label", Label).update(f"{curr_str} / {dur_str}")

    def _on_audio_state_change(self, state: PlaybackState) -> None:
        """Callback triggered by AudioPlayer on thread state updates."""
        # Use call_from_thread to update reactive UI state safely
        self.call_from_thread(self._update_card_status, state.value)

    def _update_card_status(self, status: str) -> None:
        card = self.query_one(TrackCard)
        card.status_text = status

    def _on_audio_error(self, message: str) -> None:
        """Callback triggered on audio decoding/loading error."""
        self.call_from_thread(self._update_card_status, f"ERROR: {message}")

    # --- Keybinding Action Handlers ---

    def action_toggle_play(self) -> None:
        if not self.player.current_track and self.audio_file:
            self.player.play(self.audio_file)
        elif self.player.state == PlaybackState.PLAYING:
            self.player.pause()
        elif self.player.state == PlaybackState.PAUSED:
            self.player.unpause()
        elif self.player.state == PlaybackState.STOPPED:
            self.player.play()

    def action_stop(self) -> None:
        self.player.stop()
        self.query_one(ProgressBar).progress = 0
        self.query_one("#time_label", Label).update("00:00 / 00:00")

    def action_quit(self) -> None:
        self.player.stop()
        self.exit()