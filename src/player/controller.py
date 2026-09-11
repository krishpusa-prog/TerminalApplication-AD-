from typing import Optional
from player.audio import AudioPlayer, PlaybackState


class PlayerController:
    """Coordinates audio playback commands and emits events to the UI."""

    def __init__(self, audio_engine: AudioPlayer) -> None:
        self.audio = audio_engine

    def load_track(self, file_path: str) -> bool:
        return self.audio.load(file_path)

    def play(self, file_path: Optional[str] = None) -> bool:
        return self.audio.play(file_path)

    def pause(self) -> None:
        self.audio.pause()

    def unpause(self) -> None:
        self.audio.unpause()

    def stop(self) -> None:
        self.audio.stop()

    @property
    def state(self) -> PlaybackState:
        return self.audio.state