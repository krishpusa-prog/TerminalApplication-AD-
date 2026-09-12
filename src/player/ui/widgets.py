import random
from typing import List
from textual.reactive import reactive
from textual.widgets import Static


class SpotifyVisualizer(Static):
    """Animated ASCII spectrum visualizer widget for Spotify CLI UI."""

    is_playing = reactive(False)

    BAR_CHARS = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

    def __init__(self, num_bars: int = 24, **kwargs) -> None:
        super().__init__(**kwargs)
        self.num_bars = num_bars
        self._heights: List[int] = [1] * num_bars

    def step_animation(self) -> None:
        if self.is_playing:
            self._heights = [
                max(0, min(len(self.BAR_CHARS) - 1, h + random.randint(-3, 3)))
                if random.random() > 0.15
                else random.randint(1, len(self.BAR_CHARS) - 1)
                for h in self._heights
            ]
        else:
            self._heights = [1 if i % 2 == 0 else 0 for i in range(self.num_bars)]
        self.refresh()

    def render(self) -> str:
        bars = "".join(self.BAR_CHARS[h] for h in self._heights)
        if self.is_playing:
            return f"[bold #1ED760]♫ Audio Visualizer[/bold #1ED760]\n[#1DB954]{bars}[/#1DB954]"
        return f"[dim #b3b3b3]♫ Audio Visualizer (Idle)[/dim #b3b3b3]\n[dim #444444]{bars}[/dim #444444]"


class ControlsBar(Static):
    """Renders modern Spotify playback control icons and keyboard hints."""

    status = reactive("STOPPED")

    def render(self) -> str:
        play_symbol = "⏸ PAUSE" if self.status == "PLAYING" else "▶ PLAY "
        return (
            f"[bold green]⏮ PREV[/bold green] [dim](P)[/dim]  "
            f"[bold #1ED760] {play_symbol} [/bold #1ED760] [dim](Space)[/dim]  "
            f"[bold green]⏭ NEXT[/bold green] [dim](N)[/dim]  "
            f"[bold red]⏹ STOP[/bold red] [dim](S)[/dim]"
        )
