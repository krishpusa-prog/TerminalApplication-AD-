import enum
import time
import threading
from typing import Callable, Optional
import pygame


class PlaybackState(enum.Enum):
    STOPPED = "STOPPED"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"


class AudioPlayer:
    """Headless audio engine wrapping pygame.mixer.music."""

    def __init__(self, on_state_change: Optional[Callable[[PlaybackState], None]] = None) -> None:
        # Initialize mixer only (no GUI window required)
        pygame.mixer.init()
        
        self._state = PlaybackState.STOPPED
        self._current_track: Optional[str] = None
        self._on_state_change = on_state_change
        
        # Monitor thread for auto-detecting track end
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitor = threading.Event()

    @property
    def state(self) -> PlaybackState:
        return self._state

    @property
    def current_track(self) -> Optional[str]:
        return self._current_track

    def _set_state(self, new_state: PlaybackState) -> None:
        if self._state != new_state:
            self._state = new_state
            if self._on_state_change:
                self._on_state_change(self._state)

    def load(self, file_path: str) -> None:
        """Loads an MP3 or audio file into the player."""
        pygame.mixer.music.load(file_path)
        self._current_track = file_path
        self._set_state(PlaybackState.STOPPED)

    def play(self, file_path: Optional[str] = None) -> None:
        """Plays a track. If a file path is provided, it loads and plays it."""
        if file_path:
            self.load(file_path)

        if not self._current_track:
            raise RuntimeError("No track loaded to play.")

        pygame.mixer.music.play()
        self._set_state(PlaybackState.PLAYING)
        self._start_monitoring()

    def pause(self) -> None:
        """Pauses current playback."""
        if self._state == PlaybackState.PLAYING:
            pygame.mixer.music.pause()
            self._set_state(PlaybackState.PAUSED)

    def unpause(self) -> None:
        """Resumes playback from a paused state."""
        if self._state == PlaybackState.PAUSED:
            pygame.mixer.music.unpause()
            self._set_state(PlaybackState.PLAYING)

    def toggle_play_pause(self) -> None:
        """Toggles between playing and paused states."""
        if self._state == PlaybackState.PLAYING:
            self.pause()
        elif self._state == PlaybackState.PAUSED:
            self.unpause()

    def stop(self) -> None:
        """Stops playback entirely and resets position."""
        self._stop_monitoring()
        pygame.mixer.music.stop()
        self._set_state(PlaybackState.STOPPED)

    def set_volume(self, volume: float) -> None:
        """Sets playback volume between 0.0 (silent) and 1.0 (max)."""
        clamped_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(clamped_volume)

    def get_position(self) -> float:
        """Returns elapsed playback time in seconds for the current track."""
        if self._state == PlaybackState.STOPPED:
            return 0.0
        # pygame returns milliseconds
        pos_ms = pygame.mixer.music.get_pos()
        return max(0.0, pos_ms / 1000.0)

    # --- Background Track Completion Monitor ---

    def _start_monitoring(self) -> None:
        self._stop_monitoring()
        self._stop_monitor.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_playback, daemon=True)
        self._monitor_thread.start()

    def _stop_monitoring(self) -> None:
        self._stop_monitor.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=0.2)

    def _monitor_playback(self) -> None:
        """Polls pygame to check if music ended naturally."""
        while not self._stop_monitor.is_set():
            time.sleep(0.1)
            # If state is PLAYING but mixer reports no active audio, track finished
            if self._state == PlaybackState.PLAYING and not pygame.mixer.music.get_busy():
                self._set_state(PlaybackState.STOPPED)
                break