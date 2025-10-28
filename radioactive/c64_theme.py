from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# Theme registry and active palette
C64_WIDTH = 85

_THEMES = {
    # Classic deep-purple inspired palette (approximate)
    "classic": {
        "bg": "#2b1a5a",
        "fg": "#c7b8ff",
        "border": "#b8a3ff",
        "title": "#e0d7ff",
    },
    # Gruvbox (dark) inspired
    "gruvbox-dark": {
        "bg": "#282828",
        "fg": "#ebdbb2",
        "border": "#d5c4a1",
        "title": "#fabd2f",
    },
    # Catppuccin Mocha inspired
    "catppuccin-mocha": {
        "bg": "#1e1e2e",
        "fg": "#cdd6f4",
        "border": "#89b4fa",
        "title": "#cba6f7",
    },
    # Popular VS Code themes (approximate palettes)
    "one-dark-pro": {
        "bg": "#282c34",
        "fg": "#abb2bf",
        "border": "#61afef",
        "title": "#e5c07b",
    },
    "dracula": {
        "bg": "#282a36",
        "fg": "#f8f8f2",
        "border": "#bd93f9",
        "title": "#ff79c6",
    },
    "solarized-dark": {
        "bg": "#002b36",
        "fg": "#93a1a1",
        "border": "#268bd2",
        "title": "#b58900",
    },
    "nord": {
        "bg": "#2e3440",
        "fg": "#d8dee9",
        "border": "#88c0d0",
        "title": "#ebcb8b",
    },
    "monokai": {
        "bg": "#272822",
        "fg": "#f8f8f2",
        "border": "#a6e22e",
        "title": "#fd971f",
    },
    "github-dark": {
        "bg": "#0d1117",
        "fg": "#c9d1d9",
        "border": "#58a6ff",
        "title": "#d2a8ff",
    },
    "material-darker": {
        "bg": "#212121",
        "fg": "#eeeeee",
        "border": "#82aaff",
        "title": "#c3e88d",
    },
    "night-owl": {
        "bg": "#011627",
        "fg": "#d6deeb",
        "border": "#82aaff",
        "title": "#ecc48d",
    },
    "ayu-dark": {
        "bg": "#0f1419",
        "fg": "#b3b1ad",
        "border": "#e6b450",
        "title": "#39bae6",
    },
    "tokyo-night": {
        "bg": "#1a1b26",
        "fg": "#c0caf5",
        "border": "#7aa2f7",
        "title": "#bb9af7",
    },
}

_active_name = "classic"
_ACTIVE_BG = _THEMES[_active_name]["bg"]
_ACTIVE_FG = _THEMES[_active_name]["fg"]
_ACTIVE_BORDER = _THEMES[_active_name]["border"]
_ACTIVE_TITLE = _THEMES[_active_name]["title"]

_theme = Theme(
    {
        "ui.text": _ACTIVE_FG,
        "ui.title": f"bold {_ACTIVE_TITLE}",
        "ui.border": _ACTIVE_BORDER,
    }
)


def available_themes() -> list[str]:
    return list(_THEMES.keys())


def get_active_theme_name() -> str:
    return _active_name


def get_palette() -> dict:
    return {
        "bg": _ACTIVE_BG,
        "fg": _ACTIVE_FG,
        "border": _ACTIVE_BORDER,
        "title": _ACTIVE_TITLE,
        "name": _active_name,
    }


def active_style() -> str:
    return f"{_ACTIVE_FG} on {_ACTIVE_BG}"


def apply_theme(name: str, console: Console | None = None):
    """Apply a theme by name; optionally push new Theme to the given Console."""
    global _active_name, _ACTIVE_BG, _ACTIVE_FG, _ACTIVE_BORDER, _ACTIVE_TITLE, _theme
    if name not in _THEMES:
        name = "classic"
    _active_name = name
    pal = _THEMES[name]
    _ACTIVE_BG = pal["bg"]
    _ACTIVE_FG = pal["fg"]
    _ACTIVE_BORDER = pal["border"]
    _ACTIVE_TITLE = pal["title"]
    _theme = Theme(
        {
            "ui.text": _ACTIVE_FG,
            "ui.title": f"bold {_ACTIVE_TITLE}",
            "ui.border": _ACTIVE_BORDER,
        }
    )
    if console is not None:
        try:
            console.push_theme(_theme)
        except Exception:
            pass


def themed_console(width: int = C64_WIDTH, record: bool = False, file=None) -> Console:
    return Console(
        theme=_theme,
        width=width,
        record=record,
        file=file,
        force_terminal=True,
        color_system="truecolor",
    )

# Back-compat alias (deprecated)
c64_console = themed_console


def make_panel(body, title: str = "", width: int = C64_WIDTH) -> Panel:
    # Accept any Rich renderable; coerce only plain strings
    content = body if isinstance(body, Text) or not isinstance(body, str) else Text(body)
    return Panel(
        content,
        title=title,
        width=width,
        expand=True,
        border_style=_ACTIVE_BORDER,
        box=box.HEAVY,
        style=f"{_ACTIVE_FG} on {_ACTIVE_BG}",
        safe_box=True,
    )


def make_table(headers: list[str], widths: list[int] | None = None) -> Table:
    table = Table(
        show_header=True,
        header_style="ui.title",
        min_width=C64_WIDTH,
        expand=True,
        box=box.HEAVY,
        border_style=_ACTIVE_BORDER,
        style=f"{_ACTIVE_FG} on {_ACTIVE_BG}",
        safe_box=False,
    )
    for i, h in enumerate(headers):
        justify = "left" if i == 0 else "left"
        table.add_column(h, justify=justify, no_wrap=False)
    return table
