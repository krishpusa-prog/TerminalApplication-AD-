from player.audio import AudioEngine


class PlayerController:
    """Coordinates audio playback commands and emits events to the UI."""

    def __init__(self, audio_engine: AudioEngine) -> None:
        self.audio = audio_engine