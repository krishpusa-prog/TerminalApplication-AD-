import math
import struct
import wave
import pytest
from player.audio import PlaybackState
from player.ui.app import MusicPlayerApp, TrackCard


def create_wav(path, duration=1.0, freq=440.0):
    sample_rate = 44100
    with wave.open(str(path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for i in range(int(sample_rate * duration)):
            val = int(32767.0 * math.sin(2.0 * math.pi * freq * i / sample_rate))
            f.writeframes(struct.pack("<h", val))
    return str(path)


@pytest.fixture
def sample_wav(tmp_path):
    return create_wav(tmp_path / "test_song.wav")


@pytest.mark.asyncio
async def test_tui_app_lifecycle_and_keybindings(sample_wav):
    app = MusicPlayerApp(audio_file=sample_wav)

    async with app.run_test() as pilot:
        card = app.query_one(TrackCard)
        assert card.track_title == "test_song.wav"
        assert card.status_text == "STOPPED"

        # 1. Press 'space' -> PLAYING
        await pilot.press("space")
        await pilot.pause(0.2)
        assert app.player.state == PlaybackState.PLAYING

        # 2. Press 'space' -> PAUSED
        await pilot.press("space")
        await pilot.pause(0.1)
        assert app.player.state == PlaybackState.PAUSED

        # 3. Press 'space' -> PLAYING (unpause)
        await pilot.press("space")
        await pilot.pause(0.1)
        assert app.player.state == PlaybackState.PLAYING

        # 4. Press 's' -> STOPPED
        await pilot.press("s")
        await pilot.pause(0.1)
        assert app.player.state == PlaybackState.STOPPED

        # 5. Press 'q' -> Quit app
        await pilot.press("q")


@pytest.mark.asyncio
async def test_tui_playlist_navigation(tmp_path):
    song1 = create_wav(tmp_path / "track1.wav")
    song2 = create_wav(tmp_path / "track2.wav")

    app = MusicPlayerApp(audio_target=[song1, song2])

    async with app.run_test() as pilot:
        card = app.query_one(TrackCard)
        assert "[1/2] track1.wav" in card.track_title

        # Press 'n' -> Next track
        await pilot.press("n")
        await pilot.pause(0.2)
        assert "[2/2] track2.wav" in card.track_title
        assert app.player.state == PlaybackState.PLAYING

        # Press 'p' -> Previous track
        await pilot.press("p")
        await pilot.pause(0.2)
        assert "[1/2] track1.wav" in card.track_title
        assert app.player.state == PlaybackState.PLAYING

        await pilot.press("q")
