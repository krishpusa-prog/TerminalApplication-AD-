import os
import threading
from typing import List, Optional, Union

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
        ("n", "next_track", "Next Track"),
        ("right", "next_track", "Next Track"),
        ("p", "prev_track", "Prev Track"),
        ("left", "prev_track", "Prev Track"),
        ("s", "stop", "Stop"),
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        audio_target: Optional[Union[str, List[str]]] = None,
        audio_file: Optional[str] = None,
    ) -> None:
        super().__init__()
        target = audio_file if audio_target is None else audio_target
        self.playlist: List[str] = self._build_playlist(target)
        self.current_index: int = 0
        self.audio_file: Optional[str] = self.playlist[0] if self.playlist else None
        self.player = AudioPlayer(
            on_state_change=self._on_audio_state_change,
            on_error=self._on_audio_error,
        )
        self.track_duration: float = 180.0

    def _build_playlist(self, target: Optional[Union[str, List[str]]]) -> List[str]:
        supported_exts = AudioPlayer.SUPPORTED_EXTENSIONS
        playlist: List[str] = []

        def scan_path(path: str) -> List[str]:
            found: List[str] = []
            if os.path.isfile(path):
                if os.path.splitext(path)[1].lower() in supported_exts:
                    found.append(os.path.abspath(path))
            elif os.path.isdir(path):
                for entry in sorted(os.listdir(path)):
                    full_path = os.path.join(path, entry)
                    if os.path.isfile(full_path) and os.path.splitext(full_path)[1].lower() in supported_exts:
                        found.append(os.path.abspath(full_path))
            return found

        if isinstance(target, list):
            for t in target:
                playlist.extend(scan_path(t))
        elif isinstance(target, str):
            playlist.extend(scan_path(target))
        elif target is None:
            # Default search: 'music' directory or current working directory
            if os.path.isdir("music"):
                playlist.extend(scan_path("music"))
            if not playlist:
                playlist.extend(scan_path("."))

        return playlist

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
        self.set_interval(0.1, self._update_progress)
        if self.playlist:
            self._load_track_at_index(0, auto_play=False)

    def _load_track_at_index(self, index: int, auto_play: bool = False) -> None:
        if not self.playlist:
            return
        self.current_index = index % len(self.playlist)
        track_path = self.playlist[self.current_index]
        self.audio_file = track_path

        card = self.query_one(TrackCard)
        track_name = os.path.basename(track_path)
        if len(self.playlist) > 1:
            card.track_title = f"[{self.current_index + 1}/{len(self.playlist)}] {track_name}"
        else:
            card.track_title = track_name

        self.player.stop()
        if self.player.load(track_path):
            dur = self.player.get_duration()
            if dur > 0:
                self.track_duration = dur
            if auto_play:
                self.player.play()

    def _update_progress(self) -> None:
        """Polls current position and updates progress bar + timer label."""
        if self.player.state in (PlaybackState.PLAYING, PlaybackState.PAUSED):
            current_sec = self.player.get_position()
            duration = self.player.get_duration() or self.track_duration

            # Update Progress Bar
            progress_pct = min(100.0, (current_sec / duration) * 100) if duration > 0 else 0.0
            self.query_one(ProgressBar).progress = progress_pct

            # Update Time Label (MM:SS / MM:SS)
            curr_str = f"{int(current_sec // 60):02d}:{int(current_sec % 60):02d}"
            dur_str = f"{int(duration // 60):02d}:{int(duration % 60):02d}"
            self.query_one("#time_label", Label).update(f"{curr_str} / {dur_str}")

    def _on_audio_state_change(self, state: PlaybackState) -> None:
        """Callback triggered by AudioPlayer on thread state updates."""
        if threading.get_ident() == self._thread_id:
            self._update_card_status(state.value)
        else:
            self.call_from_thread(self._update_card_status, state.value)

    def _update_card_status(self, status: str) -> None:
        card = self.query_one(TrackCard)
        card.status_text = status

    def _on_audio_error(self, message: str) -> None:
        """Callback triggered on audio decoding/loading error."""
        error_msg = f"ERROR: {message}"
        if threading.get_ident() == self._thread_id:
            self._update_card_status(error_msg)
        else:
            self.call_from_thread(self._update_card_status, error_msg)

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

    def action_next_track(self) -> None:
        if self.playlist:
            next_idx = (self.current_index + 1) % len(self.playlist)
            self._load_track_at_index(next_idx, auto_play=True)

    def action_prev_track(self) -> None:
        if self.playlist:
            prev_idx = (self.current_index - 1) % len(self.playlist)
            self._load_track_at_index(prev_idx, auto_play=True)

    def action_stop(self) -> None:
        self.player.stop()
        self.query_one(ProgressBar).progress = 0
        self.query_one("#time_label", Label).update("00:00 / 00:00")

    def action_quit(self) -> None:
        self.player.stop()
        self.exit()