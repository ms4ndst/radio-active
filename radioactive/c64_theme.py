from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# Commodore 64 inspired palette (approximate)
C64_BG = "#2b1a5a"         # deep purple background
C64_FG = "#c7b8ff"         # light lavender text
C64_BORDER = "#b8a3ff"     # border accent
C64_TITLE = "#e0d7ff"      # bright title
C64_WIDTH = 85

_theme = Theme({
    "c64.text": C64_FG,
    "c64.title": f"bold {C64_TITLE}",
    "c64.border": C64_BORDER,
})


def c64_console(width: int = C64_WIDTH, record: bool = False, file=None) -> Console:
    return Console(
        theme=_theme,
        width=width,
        record=record,
        file=file,
        force_terminal=True,
        color_system="truecolor",
    )


def make_panel(body, title: str = "", width: int = C64_WIDTH) -> Panel:
    # Accept any Rich renderable; coerce only plain strings
    content = body if isinstance(body, Text) or not isinstance(body, str) else Text(body)
    return Panel(
        content,
        title=title,
        width=width,
        expand=True,
        border_style=C64_BORDER,
        box=box.HEAVY,
        style=f"{C64_FG} on {C64_BG}",
        safe_box=True,
    )


def make_table(headers: list[str], widths: list[int] | None = None) -> Table:
    table = Table(
        show_header=True,
        header_style="c64.title",
        min_width=C64_WIDTH,
        expand=True,
        box=box.HEAVY,
        border_style=C64_BORDER,
        style=f"{C64_FG} on {C64_BG}",
        safe_box=False,
    )
    for i, h in enumerate(headers):
        justify = "left" if i == 0 else "left"
        table.add_column(h, justify=justify, no_wrap=False)
    return table
