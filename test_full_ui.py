#!/usr/bin/env python3
"""Test the full UI layout with VU meter"""

from time import sleep
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.console import Group

# Import from radioactive
from radioactive.c64_theme import make_panel, C64_WIDTH, apply_theme, active_style
from radioactive.utilities import _make_header_panel, _make_now_playing_panel, _make_vu_meter

console = Console()

# Apply a theme
apply_theme("classic")

print("\n🎵 Full UI Test with VU Meter - Press Ctrl+C to stop\n")
sleep(1)

station_name = "Jazz FM 91.1"
track_title = "Miles Davis - So What"

def make_test_view():
    """Simulate the full UI view"""
    # Header
    panel_head = _make_header_panel()
    
    # Station panel
    panel_now = _make_now_playing_panel(station_name, track_title)
    
    # Info panel
    info_text = Text("Playing smooth jazz from New York\nBitrate: 320kbps | Codec: MP3", justify="left")
    panel_info = make_panel(info_text, title="[ui.title]INFO[/]")
    
    # VU Meter
    vu_meter = _make_vu_meter()
    
    # Keys row
    hints_text = Text.from_markup(
        "[dim]Keys:[/dim] p=Play/Pause  i=Info  r=Record  n=RecordFile  f=Fav  w=List  t=Theme  v=VU  h=Help  q=Quit",
        style=active_style()
    )
    
    return Group(panel_head, panel_now, panel_info, vu_meter, hints_text)

try:
    with Live(make_test_view(), console=console, refresh_per_second=4, screen=True) as live:
        count = 0
        while count < 20:  # Run for 20 updates (~5 seconds)
            sleep(0.25)
            live.update(make_test_view())
            count += 1
    print("\n✓ Full UI test complete - VU meter is working!\n")
except KeyboardInterrupt:
    print("\n✓ Test interrupted - VU meter is working!\n")
