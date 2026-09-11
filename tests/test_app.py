import pytest
from player.ui.app import MusicPlayerApp


def test_app_instantiation():
    app = MusicPlayerApp()
    assert app.audio_file is None
    assert app.track_duration == 180.0


def test_app_instantiation_with_file():
    app = MusicPlayerApp(audio_file="test.mp3")
    assert app.audio_file == "test.mp3"
