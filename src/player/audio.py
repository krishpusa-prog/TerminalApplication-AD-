import enum
import os
import time
import threading
from typing import Callable, Optional
import pygame


class PlaybackState(enum.Enum):
    STOPPED = "STOPPED"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"


class AudioPlaybackError(Exception):
    """Custom exception for audio loading and playback failures."""
    pass


class AudioPlayer:
    """Headless audio engine wrapping pygame.mixer.music with robust error handling."""

    # Common formats natively supported by standard pygame SDL2 builds
    SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".ogg"}

    def __init__(
        self,
        on_state_change: Optional[Callable[[PlaybackState], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        try:
            pygame.mixer.init()
        except pygame.error as exc:
            raise AudioPlaybackError(f"Failed to initialize audio driver: {exc}") from exc

        self._state = PlaybackState.STOPPED
        self._current_track: Optional[str] = None
        self._track_duration: float = 0.0
        self._on_state_change = on_state_change
        self._on_error = on_error

        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitor = threading.Event()

    def get_position(self) -> float:
        """Returns the current playback position in seconds."""
        if self._state in (PlaybackState.PLAYING, PlaybackState.PAUSED):
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms >= 0:
                return pos_ms / 1000.0
        return 0.0

    def get_duration(self) -> float:
        """Returns the total track duration in seconds if known."""
        return self._track_duration

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

    def _handle_error(self, message: str) -> None:
        """Resets internal state and dispatches the error message to listener."""
        self.stop()
        self._set_state(PlaybackState.ERROR)
        if self._on_error:
            self._on_error(message)

    def load(self, file_path: str) -> bool:
        """
        Loads an audio file safely.
        Returns True if successful, False if loading failed.
        """
        if not os.path.exists(file_path):
            self._handle_error(f"File not found: '{file_path}'")
            return False

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            self._handle_error(
                f"Unsupported file extension '{ext}'. Pygame supports: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )
            return False

        try:
            pygame.mixer.music.load(file_path)
            self._current_track = file_path
            try:
                sound = pygame.mixer.Sound(file_path)
                self._track_duration = sound.get_length()
            except Exception:
                self._track_duration = 0.0
            self._set_state(PlaybackState.STOPPED)
            return True
        except pygame.error as exc:
            # Catches corrupted files, invalid headers, or missing backend codecs
            self._handle_error(f"Failed to decode audio file '{os.path.basename(file_path)}': {exc}")
            return False
        except Exception as exc:
            self._handle_error(f"Unexpected error loading file: {exc}")
            return False

    def play(self, file_path: Optional[str] = None) -> bool:
        """
        Plays a track. If a file path is passed, it loads it first.
        Returns True if playback started, False otherwise.
        """
        if file_path:
            if not self.load(file_path):
                return False

        if not self._current_track:
            self._handle_error("No track loaded to play.")
            return False

        try:
            pygame.mixer.music.play()
            self._set_state(PlaybackState.PLAYING)
            self._start_monitoring()
            return True
        except pygame.error as exc:
            self._handle_error(f"Playback error: {exc}")
            return False

    def pause(self) -> None:
        if self._state == PlaybackState.PLAYING:
            pygame.mixer.music.pause()
            self._set_state(PlaybackState.PAUSED)

    def unpause(self) -> None:
        if self._state == PlaybackState.PAUSED:
            try:
                pygame.mixer.music.unpause()
                self._set_state(PlaybackState.PLAYING)
            except pygame.error as exc:
                self._handle_error(f"Failed to resume playback: {exc}")

    def stop(self) -> None:
        self._stop_monitoring()
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        self._set_state(PlaybackState.STOPPED)

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
        while not self._stop_monitor.is_set():
            time.sleep(0.1)
            if self._state == PlaybackState.PLAYING and not pygame.mixer.music.get_busy():
                self._set_state(PlaybackState.STOPPED)
                break