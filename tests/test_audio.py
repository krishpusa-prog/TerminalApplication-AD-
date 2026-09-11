import os
import pytest
from player.audio import AudioPlayer, PlaybackState, AudioPlaybackError


@pytest.fixture
def player():
    """Provides a fresh AudioPlayer instance for each test."""
    # Use dummy audio driver for headless CI/testing environments if needed
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    return AudioPlayer()


def test_initial_state(player):
    assert player.state == PlaybackState.STOPPED
    assert player.current_track is None
    assert player.get_position() == 0.0
    assert player.get_duration() == 0.0


def test_load_nonexistent_file(player):
    recorded_errors = []
    player._on_error = lambda msg: recorded_errors.append(msg)

    result = player.load("non_existent_file.mp3")

    assert result is False
    assert player.state == PlaybackState.ERROR
    assert len(recorded_errors) == 1
    assert "File not found" in recorded_errors[0]


def test_load_unsupported_file_format(player, tmp_path):
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("not an audio file")

    recorded_errors = []
    player._on_error = lambda msg: recorded_errors.append(msg)

    result = player.load(str(invalid_file))

    assert result is False
    assert player.state == PlaybackState.ERROR
    assert len(recorded_errors) == 1
    assert "Unsupported file extension" in recorded_errors[0]


def test_play_without_loading_track(player):
    recorded_errors = []
    player._on_error = lambda msg: recorded_errors.append(msg)

    result = player.play()

    assert result is False
    assert player.state == PlaybackState.ERROR
    assert "No track loaded" in recorded_errors[0]


def test_pause_and_stop_when_stopped(player):
    # Should not throw errors when pausing or stopping while stopped
    player.pause()
    assert player.state == PlaybackState.STOPPED

    player.stop()
    assert player.state == PlaybackState.STOPPED
