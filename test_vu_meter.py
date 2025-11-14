#!/usr/bin/env python3
"""Quick test of VU meter display"""

from time import sleep
from rich.console import Console
from rich.live import Live
from radioactive.utilities import _make_vu_meter

console = Console()

print("\n🎵 VU Meter Test - Press Ctrl+C to stop\n")

try:
    with Live(_make_vu_meter(), console=console, refresh_per_second=4) as live:
        while True:
            sleep(0.25)
            live.update(_make_vu_meter())
except KeyboardInterrupt:
    print("\n✓ VU meter test complete\n")
