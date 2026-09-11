import pytest
from player.audio import AudioPlayer, PlaybackState
from player.controller import PlayerController


@pytest.fixture
def controller():
    audio = AudioPlayer()
    return PlayerController(audio_engine=audio)


def test_controller_initialization(controller):
    assert isinstance(controller.audio, AudioPlayer)
    assert controller.state == PlaybackState.STOPPED


def test_controller_delegation(controller):
    assert controller.load_track("missing.mp3") is False
    assert controller.state == PlaybackState.ERROR

    controller.stop()
    assert controller.state == PlaybackState.STOPPED
