from dataclasses import dataclass


@dataclass(frozen=True)
class PlaybackStateChanged:
    """Fired when playback state toggles (playing, paused, stopped)."""
    state: str


@dataclass(frozen=True)
class TrackPositionUpdated:
    """Fired periodically during playback."""
    position: float
    duration: float