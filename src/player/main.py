import sys
from player.ui.app import MusicPlayerApp


def main() -> None:
    """Entry point for the CLI music player."""
    try:
        app = MusicPlayerApp()
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()