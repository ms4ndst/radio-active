from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
import shutil

# Theme registry and active palette
C64_WIDTH = 85

_THEMES = {
    # Classic deep-purple inspired palette (approximate)
    "classic": {
        "bg": "#2b1a5a",
        "fg": "#c7b8ff",
        "border": "#b8a3ff",
        "title": "#e0d7ff",
        "vu_low": "#50c878",
        "vu_mid_low": "#7ae582",
        "vu_mid": "#a4ff8c",
        "vu_mid_high": "#ffeb3b",
        "vu_high": "#ffc107",
        "vu_very_high": "#ff9800",
        "vu_critical_low": "#ff5722",
        "vu_critical": "#f44336",
    },
    # Gruvbox (dark) inspired
    "gruvbox-dark": {
        "bg": "#282828",
        "fg": "#ebdbb2",
        "border": "#d5c4a1",
        "title": "#fabd2f",
        "vu_low": "#98971a",
        "vu_mid_low": "#b8bb26",
        "vu_mid": "#d79921",
        "vu_mid_high": "#fabd2f",
        "vu_high": "#fe8019",
        "vu_very_high": "#fb4934",
        "vu_critical_low": "#cc241d",
        "vu_critical": "#9d0006",
    },
    # Catppuccin Mocha inspired
    "catppuccin-mocha": {
        "bg": "#1e1e2e",
        "fg": "#cdd6f4",
        "border": "#89b4fa",
        "title": "#cba6f7",
        "vu_low": "#a6e3a1",
        "vu_mid_low": "#94e2d5",
        "vu_mid": "#89dceb",
        "vu_mid_high": "#f9e2af",
        "vu_high": "#fab387",
        "vu_very_high": "#f38ba8",
        "vu_critical_low": "#eba0ac",
        "vu_critical": "#f38ba8",
    },
    # Popular VS Code themes (approximate palettes)
    "one-dark-pro": {
        "bg": "#282c34",
        "fg": "#abb2bf",
        "border": "#61afef",
        "title": "#e5c07b",
        "vu_low": "#98c379",
        "vu_mid_low": "#b4d273",
        "vu_mid": "#d19a66",
        "vu_mid_high": "#e5c07b",
        "vu_high": "#e06c75",
        "vu_very_high": "#be5046",
        "vu_critical_low": "#e06c75",
        "vu_critical": "#e55561",
    },
    "dracula": {
        "bg": "#282a36",
        "fg": "#f8f8f2",
        "border": "#bd93f9",
        "title": "#ff79c6",
        "vu_low": "#50fa7b",
        "vu_mid_low": "#8be9fd",
        "vu_mid": "#ffb86c",
        "vu_mid_high": "#f1fa8c",
        "vu_high": "#ffb86c",
        "vu_very_high": "#ff79c6",
        "vu_critical_low": "#ff6e6e",
        "vu_critical": "#ff5555",
    },
    "solarized-dark": {
        "bg": "#002b36",
        "fg": "#93a1a1",
        "border": "#268bd2",
        "title": "#b58900",
        "vu_low": "#859900",
        "vu_mid_low": "#b58900",
        "vu_mid": "#cb4b16",
        "vu_mid_high": "#dc322f",
        "vu_high": "#d33682",
        "vu_very_high": "#6c71c4",
        "vu_critical_low": "#268bd2",
        "vu_critical": "#2aa198",
    },
    "nord": {
        "bg": "#2e3440",
        "fg": "#d8dee9",
        "border": "#88c0d0",
        "title": "#ebcb8b",
        "vu_low": "#a3be8c",
        "vu_mid_low": "#8fbcbb",
        "vu_mid": "#88c0d0",
        "vu_mid_high": "#81a1c1",
        "vu_high": "#5e81ac",
        "vu_very_high": "#b48ead",
        "vu_critical_low": "#bf616a",
        "vu_critical": "#d08770",
    },
    "monokai": {
        "bg": "#272822",
        "fg": "#f8f8f2",
        "border": "#a6e22e",
        "title": "#fd971f",
        "vu_low": "#a6e22e",
        "vu_mid_low": "#a6db22",
        "vu_mid": "#e6db74",
        "vu_mid_high": "#f4bf75",
        "vu_high": "#fd971f",
        "vu_very_high": "#f92672",
        "vu_critical_low": "#f83535",
        "vu_critical": "#f92672",
    },
    "github-dark": {
        "bg": "#0d1117",
        "fg": "#c9d1d9",
        "border": "#58a6ff",
        "title": "#d2a8ff",
        "vu_low": "#3fb950",
        "vu_mid_low": "#56d364",
        "vu_mid": "#d2a8ff",
        "vu_mid_high": "#ffa657",
        "vu_high": "#f85149",
        "vu_very_high": "#da3633",
        "vu_critical_low": "#f85149",
        "vu_critical": "#ff6b6b",
    },
    "material-darker": {
        "bg": "#212121",
        "fg": "#eeeeee",
        "border": "#82aaff",
        "title": "#c3e88d",
        "vu_low": "#c3e88d",
        "vu_mid_low": "#89ddff",
        "vu_mid": "#82aaff",
        "vu_mid_high": "#c792ea",
        "vu_high": "#ffcb6b",
        "vu_very_high": "#f78c6c",
        "vu_critical_low": "#ff5370",
        "vu_critical": "#f07178",
    },
    "night-owl": {
        "bg": "#011627",
        "fg": "#d6deeb",
        "border": "#82aaff",
        "title": "#ecc48d",
        "vu_low": "#addb67",
        "vu_mid_low": "#7fdbca",
        "vu_mid": "#82aaff",
        "vu_mid_high": "#c792ea",
        "vu_high": "#ecc48d",
        "vu_very_high": "#f78c6c",
        "vu_critical_low": "#ef5350",
        "vu_critical": "#ff5370",
    },
    "ayu-dark": {
        "bg": "#0f1419",
        "fg": "#b3b1ad",
        "border": "#e6b450",
        "title": "#39bae6",
        "vu_low": "#95e6cb",
        "vu_mid_low": "#5ccfe6",
        "vu_mid": "#39bae6",
        "vu_mid_high": "#73d0ff",
        "vu_high": "#ffb454",
        "vu_very_high": "#ff8f40",
        "vu_critical_low": "#f07178",
        "vu_critical": "#ff3333",
    },
    "tokyo-night": {
        "bg": "#1a1b26",
        "fg": "#c0caf5",
        "border": "#7aa2f7",
        "title": "#bb9af7",
        "vu_low": "#9ece6a",
        "vu_mid_low": "#73daca",
        "vu_mid": "#2ac3de",
        "vu_mid_high": "#7dcfff",
        "vu_high": "#7aa2f7",
        "vu_very_high": "#bb9af7",
        "vu_critical_low": "#f7768e",
        "vu_critical": "#ff757f",
    },
    # Additional popular themes
    "gruvbox-light": {
        "bg": "#fbf1c7",
        "fg": "#3c3836",
        "border": "#b57614",
        "title": "#d79921",
        "vu_low": "#79740e",
        "vu_mid_low": "#98971a",
        "vu_mid": "#b57614",
        "vu_mid_high": "#d79921",
        "vu_high": "#d65d0e",
        "vu_very_high": "#cc241d",
        "vu_critical_low": "#9d0006",
        "vu_critical": "#cc241d",
    },
    "catppuccin-latte": {
        "bg": "#eff1f5",
        "fg": "#4c4f69",
        "border": "#04a5e5",
        "title": "#1e66f5",
        "vu_low": "#40a02b",
        "vu_mid_low": "#179299",
        "vu_mid": "#04a5e5",
        "vu_mid_high": "#1e66f5",
        "vu_high": "#8839ef",
        "vu_very_high": "#ea76cb",
        "vu_critical_low": "#d20f39",
        "vu_critical": "#e64553",
    },
    "solarized-light": {
        "bg": "#fdf6e3",
        "fg": "#657b83",
        "border": "#268bd2",
        "title": "#b58900",
        "vu_low": "#859900",
        "vu_mid_low": "#b58900",
        "vu_mid": "#cb4b16",
        "vu_mid_high": "#dc322f",
        "vu_high": "#d33682",
        "vu_very_high": "#6c71c4",
        "vu_critical_low": "#268bd2",
        "vu_critical": "#2aa198",
    },
    "github-light": {
        "bg": "#ffffff",
        "fg": "#24292e",
        "border": "#0969da",
        "title": "#8250df",
        "vu_low": "#1a7f37",
        "vu_mid_low": "#1f883d",
        "vu_mid": "#0969da",
        "vu_mid_high": "#8250df",
        "vu_high": "#bf3989",
        "vu_very_high": "#cf222e",
        "vu_critical_low": "#a40e26",
        "vu_critical": "#d1242f",
    },
    "one-light": {
        "bg": "#fafafa",
        "fg": "#383a42",
        "border": "#4078f2",
        "title": "#c18401",
        "vu_low": "#50a14f",
        "vu_mid_low": "#4078f2",
        "vu_mid": "#0184bc",
        "vu_mid_high": "#a626a4",
        "vu_high": "#c18401",
        "vu_very_high": "#e45649",
        "vu_critical_low": "#ca1243",
        "vu_critical": "#e45649",
    },
    "material-light": {
        "bg": "#FAFAFA",
        "fg": "#545454",
        "border": "#2962ff",
        "title": "#00c853",
        "vu_low": "#00c853",
        "vu_mid_low": "#00acc1",
        "vu_mid": "#2962ff",
        "vu_mid_high": "#6200ea",
        "vu_high": "#aa00ff",
        "vu_very_high": "#d50000",
        "vu_critical_low": "#c51162",
        "vu_critical": "#d50000",
    },
    "everforest-dark": {
        "bg": "#2d353b",
        "fg": "#d3c6aa",
        "border": "#a7c080",
        "title": "#e69875",
        "vu_low": "#a7c080",
        "vu_mid_low": "#83c092",
        "vu_mid": "#7fbbb3",
        "vu_mid_high": "#d3c6aa",
        "vu_high": "#e69875",
        "vu_very_high": "#e67e80",
        "vu_critical_low": "#f85552",
        "vu_critical": "#e67e80",
    },
    "palenight": {
        "bg": "#292D3E",
        "fg": "#A6ACCD",
        "border": "#82AAFF",
        "title": "#C792EA",
        "vu_low": "#C3E88D",
        "vu_mid_low": "#89DDFF",
        "vu_mid": "#82AAFF",
        "vu_mid_high": "#C792EA",
        "vu_high": "#FFCB6B",
        "vu_very_high": "#F78C6C",
        "vu_critical_low": "#FF5370",
        "vu_critical": "#F07178",
    },
    "horizon": {
        "bg": "#1C1E26",
        "fg": "#E0E0E0",
        "border": "#E95378",
        "title": "#FAB795",
        "vu_low": "#27D796",
        "vu_mid_low": "#25B0BC",
        "vu_mid": "#26BBD9",
        "vu_mid_high": "#FAC29A",
        "vu_high": "#FAB795",
        "vu_very_high": "#F43E5C",
        "vu_critical_low": "#E95378",
        "vu_critical": "#EC6A88",
    },
    "kanagawa": {
        "bg": "#1F1F28",
        "fg": "#DCD7BA",
        "border": "#7E9CD8",
        "title": "#957FB8",
        "vu_low": "#76946A",
        "vu_mid_low": "#7AA89F",
        "vu_mid": "#7E9CD8",
        "vu_mid_high": "#7FB4CA",
        "vu_high": "#957FB8",
        "vu_very_high": "#D27E99",
        "vu_critical_low": "#E82424",
        "vu_critical": "#FF5D62",
    },
    "rose-pine": {
        "bg": "#191724",
        "fg": "#e0def4",
        "border": "#31748f",
        "title": "#eb6f92",
        "vu_low": "#9ccfd8",
        "vu_mid_low": "#3e8fb0",
        "vu_mid": "#31748f",
        "vu_mid_high": "#c4a7e7",
        "vu_high": "#ebbcba",
        "vu_very_high": "#f6c177",
        "vu_critical_low": "#eb6f92",
        "vu_critical": "#e74c3c",
    },
    "rose-pine-moon": {
        "bg": "#232136",
        "fg": "#e0def4",
        "border": "#3e8fb0",
        "title": "#ea9a97",
        "vu_low": "#9ccfd8",
        "vu_mid_low": "#3e8fb0",
        "vu_mid": "#c4a7e7",
        "vu_mid_high": "#f6c177",
        "vu_high": "#ea9a97",
        "vu_very_high": "#eb6f92",
        "vu_critical_low": "#e85b7a",
        "vu_critical": "#e74c3c",
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
        "vu_low": _THEMES[_active_name].get("vu_low", "#50c878"),
        "vu_mid_low": _THEMES[_active_name].get("vu_mid_low", "#7ae582"),
        "vu_mid": _THEMES[_active_name].get("vu_mid", "#a4ff8c"),
        "vu_mid_high": _THEMES[_active_name].get("vu_mid_high", "#ffeb3b"),
        "vu_high": _THEMES[_active_name].get("vu_high", "#ffc107"),
        "vu_very_high": _THEMES[_active_name].get("vu_very_high", "#ff9800"),
        "vu_critical_low": _THEMES[_active_name].get("vu_critical_low", "#ff5722"),
        "vu_critical": _THEMES[_active_name].get("vu_critical", "#f44336"),
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


def get_ui_width() -> int:
    try:
        cols = shutil.get_terminal_size(fallback=(C64_WIDTH, 24)).columns
        # keep within sensible bounds
        return max(85, min(cols - 2, 120))
    except Exception:
        return C64_WIDTH


def themed_console(width: int | None = None, record: bool = False, file=None) -> Console:
    # Let Rich use the terminal width by default
    return Console(
        theme=_theme,
        width=width,  # None -> auto
        record=record,
        file=file,
        force_terminal=True,
        color_system="truecolor",
    )

# Back-compat alias (deprecated)
c64_console = themed_console


def make_panel(body, title: str = "", width: int | None = None) -> Panel:
    # Accept any Rich renderable; coerce only plain strings
    content = body if isinstance(body, Text) or not isinstance(body, str) else Text(body)
    width = width or get_ui_width()
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
    width = get_ui_width()
    table = Table(
        show_header=True,
        header_style="ui.title",
        min_width=width,
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
