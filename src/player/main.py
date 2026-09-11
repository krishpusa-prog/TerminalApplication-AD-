import sys
from player.ui.app import MusicPlayerApp


def main() -> None:
    audio_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = MusicPlayerApp(audio_file=audio_file)
    app.run()


if __name__ == "__main__":
    main()