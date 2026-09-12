import os
import threading
from typing import List, Optional, Union

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, ListItem, ListView, ProgressBar, Static

from player.audio import AudioPlayer, PlaybackState
from player.ui.widgets import ControlsBar, SpotifyVisualizer


class TrackCard(Static):
    """Widget to display track title, artist info, and Spotify state badge."""

    status_text = reactive("STOPPED")
    track_title = reactive("No track loaded")

    def render(self) -> str:
        if self.status_text == "PLAYING":
            badge = "[bold #000000 on #1ED760] ▶ PLAYING [/bold #000000 on #1ED760]"
        elif self.status_text == "PAUSED":
            badge = "[bold #000000 on #E2B714] ⏸ PAUSED [/bold #000000 on #E2B714]"
        elif "ERROR" in self.status_text:
            badge = "[bold #FFFFFF on #E74C3C] ✖ ERROR [/bold #FFFFFF on #E74C3C]"
        else:
            badge = "[bold #888888 on #282828] ⏹ STOPPED [/bold #888888 on #282828]"

        return (
            f"[dim #B3B3B3]NOW PLAYING[/dim #B3B3B3]\n"
            f"[bold #FFFFFF]{self.track_title}[/bold #FFFFFF]\n"
            f"{badge}"
        )


class MusicPlayerApp(App[None]):
    """Modern Spotify-inspired Textual CLI Music Player Interface."""

    TITLE = "Spotify CLI Player"
    SUB_TITLE = "Minimalistic Audio Player"

    CSS = """
    Screen {
        background: #121212;
        color: #FFFFFF;
    }

    Header {
        background: #181818;
        color: #1ED760;
        dock: top;
    }

    Footer {
        background: #181818;
        color: #B3B3B3;
        dock: bottom;
    }

    #main_layout {
        width: 100%;
        height: 1fr;
        padding: 1 2;
    }

    #sidebar_pane {
        width: 35%;
        height: 100%;
        border: round #282828;
        background: #181818;
        padding: 1 1;
        margin-right: 1;
    }

    #sidebar_header {
        text-align: center;
        border-bottom: solid #282828;
        padding-bottom: 1;
        margin-bottom: 1;
        color: #1ED760;
        text-style: bold;
    }

    #playlist_list {
        background: #181818;
        height: 1fr;
        border: none;
    }

    #playlist_list > ListItem {
        padding: 0 1;
        color: #B3B3B3;
    }

    #playlist_list > ListItem:hover {
        background: #282828;
        color: #FFFFFF;
    }

    #playlist_list > ListItem.--highlight {
        background: #282828;
        color: #1ED760;
        text-style: bold;
    }

    #now_playing_pane {
        width: 65%;
        height: 100%;
        border: round #1DB954;
        background: #181818;
        padding: 1 2;
        align: center middle;
    }

    TrackCard {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        content-align: center middle;
        text-align: center;
    }

    SpotifyVisualizer {
        width: 100%;
        height: 3;
        content-align: center middle;
        text-align: center;
        margin-bottom: 1;
    }

    ControlsBar {
        width: 100%;
        content-align: center middle;
        text-align: center;
        margin-bottom: 1;
    }

    ProgressBar {
        width: 100%;
        margin-bottom: 1;
    }

    ProgressBar > .bar--bar {
        color: #1DB954;
        background: #282828;
    }

    ProgressBar > .bar--complete {
        color: #1ED760;
    }

    #time_label {
        content-align: center middle;
        width: 100%;
        color: #B3B3B3;
        text-style: bold;
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
        with Horizontal(id="main_layout"):
            with Vertical(id="sidebar_pane"):
                yield Label("📁 PLAYLIST", id="sidebar_header")
                list_items = [
                    ListItem(Label(f"{i + 1}. {os.path.basename(path)}"))
                    for i, path in enumerate(self.playlist)
                ]
                yield ListView(*list_items, id="playlist_list")
            with Vertical(id="now_playing_pane"):
                yield TrackCard(id="track_card")
                yield SpotifyVisualizer(id="visualizer")
                yield ControlsBar(id="controls_bar")
                yield ProgressBar(total=100, show_percentage=False, id="progress_bar")
                yield Label("00:00 / 00:00", id="time_label")
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts. Sets up timers and loads track if provided."""
        self.set_interval(0.1, self._update_progress)
        if self.playlist:
            self._load_track_at_index(0, auto_play=False)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle track selection from the playlist sidebar."""
        index = event.list_view.index
        if index is not None and 0 <= index < len(self.playlist):
            self._load_track_at_index(index, auto_play=True)

    def _load_track_at_index(self, index: int, auto_play: bool = False) -> None:
        if not self.playlist:
            return
        self.current_index = index % len(self.playlist)
        track_path = self.playlist[self.current_index]
        self.audio_file = track_path

        try:
            card = self.query_one(TrackCard)
            track_name = os.path.basename(track_path)
            if len(self.playlist) > 1:
                card.track_title = f"[{self.current_index + 1}/{len(self.playlist)}] {track_name}"
            else:
                card.track_title = track_name
        except NoMatches:
            pass

        try:
            playlist_list = self.query_one("#playlist_list", ListView)
            playlist_list.index = self.current_index
        except (NoMatches, Exception):
            pass

        self.player.stop()
        if self.player.load(track_path):
            dur = self.player.get_duration()
            if dur > 0:
                self.track_duration = dur
            if auto_play:
                self.player.play()

    def _update_progress(self) -> None:
        """Polls current position and updates progress bar, visualizer + timer label."""
        # Update Visualizer animation
        try:
            vis = self.query_one(SpotifyVisualizer)
            vis.is_playing = (self.player.state == PlaybackState.PLAYING)
            vis.step_animation()
        except (NoMatches, Exception):
            pass

        if self.player.state in (PlaybackState.PLAYING, PlaybackState.PAUSED):
            current_sec = self.player.get_position()
            duration = self.player.get_duration() or self.track_duration

            # Update Progress Bar
            try:
                progress_pct = min(100.0, (current_sec / duration) * 100) if duration > 0 else 0.0
                self.query_one(ProgressBar).progress = progress_pct

                # Update Time Label (MM:SS / MM:SS)
                curr_str = f"{int(current_sec // 60):02d}:{int(current_sec % 60):02d}"
                dur_str = f"{int(duration // 60):02d}:{int(duration % 60):02d}"
                self.query_one("#time_label", Label).update(f"{curr_str} / {dur_str}")
            except (NoMatches, Exception):
                pass

    def _on_audio_state_change(self, state: PlaybackState) -> None:
        """Callback triggered by AudioPlayer on thread state updates."""
        if threading.get_ident() == self._thread_id:
            self._update_card_status(state.value)
        else:
            self.call_from_thread(self._update_card_status, state.value)

    def _update_card_status(self, status: str) -> None:
        try:
            card = self.query_one(TrackCard)
            card.status_text = status
        except (NoMatches, Exception):
            pass

        try:
            controls = self.query_one(ControlsBar)
            controls.status = status
        except (NoMatches, Exception):
            pass

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
        try:
            self.query_one(ProgressBar).progress = 0
            self.query_one("#time_label", Label).update("00:00 / 00:00")
        except (NoMatches, Exception):
            pass

    def action_quit(self) -> None:
        self.player.stop()
        self.exit()