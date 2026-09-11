import pytest
from player.ui.app import MusicPlayerApp


def test_app_instantiation_empty():
    app = MusicPlayerApp(audio_target=[])
    assert app.audio_file is None
    assert app.playlist == []


def test_app_instantiation_with_existing_file(tmp_path):
    f = tmp_path / "song.wav"
    f.write_text("")
    app = MusicPlayerApp(audio_target=str(f))
    assert app.audio_file == str(f)
    assert len(app.playlist) == 1
