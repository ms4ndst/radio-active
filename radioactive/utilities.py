"""Handler functions for __main__.py"""

import datetime
import json
import os
import subprocess
import sys
from random import randint
from time import sleep
import time
import threading
import atexit
import io

import requests
from pick import pick
from rich import print
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from zenlog import log

# C64-inspired UI helpers
from radioactive.c64_theme import make_panel, make_table, themed_console, C64_WIDTH, available_themes, apply_theme, get_active_theme_name, active_style

# Windows single-key support
try:
    import msvcrt  # type: ignore
except Exception:
    msvcrt = None

# POSIX single-key support
try:
    import termios  # type: ignore
    import tty  # type: ignore
    import select  # type: ignore
except Exception:
    termios = None
    tty = None
    select = None

from radioactive.ffplay import kill_background_ffplays
from radioactive.last_station import Last_station
from radioactive.recorder import record_audio_auto_codec, record_audio_from_url

RED_COLOR = "\033[91m"
END_COLOR = "\033[0m"

global_current_station_info = {}

# Live UI globals
_global_now_playing_live = None
_global_now_playing_station = ""
_global_now_playing_title = ""
_global_now_playing_hints = ""
_global_now_playing_messages: list[str] = []
# Current stream URL for the Live worker
_global_now_playing_url = ""
# Optional: a Rich renderable to show in INFO panel instead of plain text lines
_global_info_renderable = None
_global_now_playing_input_active = False
_force_mp3_always = False


def ui_info(message: str):
    """Route info messages to the Live INFO panel when active, else log."""
    try:
        if _global_now_playing_live is not None:
            set_info_text(message)
        else:
            log.info(message)
    except Exception:
        log.info(message)


def ui_error(message: str):
    """Route error messages to the Live INFO panel when active, else log."""
    try:
        if _global_now_playing_live is not None:
            set_info_text(message)
        else:
            log.error(message)
    except Exception:
        log.error(message)


def handle_fetch_song_title(url):
    """Fetch currently playing track information"""
    log.info("Fetching the current track info")
    log.debug("Attempting to retrieve track info from: {}".format(url))
    # Run ffprobe command and capture the metadata
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_entries",
        "format=icy",
        url,
    ]
    track_name = ""

    try:
        output = subprocess.check_output(cmd).decode("utf-8")
        data = json.loads(output)
        log.debug(f"station info: {data}")

        # Extract the station name (icy-name) if available
        track_name = data.get("format", {}).get("tags", {}).get("StreamTitle", "")
    except:
        log.error("Error while fetching the track name")

    if track_name != "":
        log.info(f"🎶: {track_name}")
    else:
        log.error("No track information available")


def get_song_title(url: str) -> str:
    """Return current StreamTitle from ffprobe, else empty string."""
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_entries",
        "format=icy",
        url,
    ]
    try:
        output = subprocess.check_output(cmd).decode("utf-8")
        data = json.loads(output)
        return data.get("format", {}).get("tags", {}).get("StreamTitle", "")
    except Exception as e:
        log.debug(f"get_song_title error: {e}")
        return ""


def _make_now_playing_panel(station_name: str, track_title: str) -> Panel:
    title = Text(station_name or "Unknown Station", style="ui.title", justify="center")
    body = Text(f"🎶 {track_title or 'Fetching…'}", justify="center")
    return make_panel(body, title=title, width=C64_WIDTH)


def _make_header_panel() -> Panel:
    head = Text("Play radios from your terminal — press h for help, q to quit", justify="center")
    return make_panel(head, title="[ui.title]RADIO-ACTIVE[/]", width=C64_WIDTH)


def _make_now_playing_view(station_name: str, track_title: str, hints: str, messages):
    # Header (always visible at top)
    panel_head = _make_header_panel()
    # Station panel
    panel_now = _make_now_playing_panel(station_name, track_title)
    # Info panel below station
    if _global_info_renderable is not None:
        info_body = _global_info_renderable
    else:
        info_body = Text("\n".join(messages) if messages else "")
    panel_info = make_panel(info_body, title="[ui.title]INFO[/]", width=C64_WIDTH)
    # Keys row
    # Hints styled to match active theme colors
    if hints:
        hints_text = Text.from_markup(hints, style=active_style())
    else:
        hints_text = Text("", style=active_style())
    return Group(panel_head, panel_now, panel_info, hints_text)


def _update_live_view():
    if _global_now_playing_live:
        _global_now_playing_live.update(
            _make_now_playing_view(
                _global_now_playing_station,
                _global_now_playing_title,
                _global_now_playing_hints,
                _global_now_playing_messages,
            )
        )


def set_info_text(text: str):
    global _global_now_playing_messages, _global_info_renderable
    _global_info_renderable = None
    _global_now_playing_messages = [text.rstrip("\n")] if text else []
    _update_live_view()


def set_info_lines(lines: list[str]):
    global _global_now_playing_messages, _global_info_renderable
    _global_info_renderable = None
    _global_now_playing_messages = [l.rstrip("\n") for l in lines]
    _update_live_view()


def safe_input(prompt: str) -> str:
    """Prompt for input below the Live view (under the Keys row).

    Keep Live running (especially in alternate screen) to preserve the view.
    """
    global _global_now_playing_live, _global_now_playing_input_active
    if _global_now_playing_live is not None:
        _global_now_playing_input_active = True
        try:
            try:
                _global_now_playing_live.console.print("")
            except Exception:
                pass
            value = _global_now_playing_live.console.input(prompt)
        finally:
            _global_now_playing_input_active = False
            _update_live_view()
        return value
    # fallback if Live not running
    return input(prompt)


def set_force_mp3(flag: bool):
    global _force_mp3_always
    _force_mp3_always = bool(flag)


def _quick_pick_index(max_n: int, timeout: float = 0.7) -> int | None:
    """Capture numeric keys without Enter; supports multi-digit with a short timeout.
    Returns 0-based index or None to cancel/invalid.
    """
    global _global_now_playing_input_active
    _global_now_playing_input_active = True
    buf = ""
    last_ts = None
    try:
        while True:
            ch = _get_single_key()
            now = time.time()
            if ch is None:
                if buf and last_ts is not None and (now - last_ts) >= timeout:
                    break
                sleep(0.05)
                continue
            # cancel
            if ch in ("q", "Q", "\x1b"):
                buf = ""
                break
            # finalize
            if ch in ("\r", "\n"):
                break
            # collect digits
            if ch.isdigit():
                if not buf and ch == "0":
                    # ignore leading zero
                    continue
                buf += ch
                last_ts = now
                # if single-digit and within range, finalize immediately
                try:
                    val = int(buf)
                    if 1 <= val <= max_n and max_n <= 9:
                        break
                except Exception:
                    pass
                continue
            # any other key ends collection if we already have some digits
            if buf:
                break
            # otherwise ignore
    finally:
        _global_now_playing_input_active = False
    if not buf:
        return None
    try:
        val = int(buf)
        if 1 <= val <= max_n:
            return val - 1
    except Exception:
        pass
    return None


def set_info_renderable(renderable):
    global _global_info_renderable
    _global_info_renderable = renderable
    _update_live_view()


def start_now_playing_live(station_name: str, target_url: str, interval_seconds: int = 15) -> Live:
    """Start Live UI and a background worker that updates song title."""
    global _global_now_playing_live, _global_now_playing_station, _global_now_playing_title
    global _global_now_playing_hints, _global_now_playing_messages, global_current_station_info, _global_now_playing_url

    _global_now_playing_station = station_name
    _global_now_playing_title = ""
    _global_now_playing_hints = "[dim]Keys:[/dim] p=Play/Pause  i=Info  r=Record  n=RecordFile  f=Fav  w=List  t=Theme  h=Help  q=Quit"
    _global_now_playing_messages = []
    _global_now_playing_url = target_url or ""

    # Ensure minimal station info is available for the Info panel
    try:
        global_current_station_info = {
            "name": station_name or "Unknown Station",
            "url": target_url or "",
        }
    except Exception:
        pass

    console = themed_console()
    live = Live(
        _make_now_playing_view(
            _global_now_playing_station,
            _global_now_playing_title,
            _global_now_playing_hints,
            _global_now_playing_messages,
        ),
        console=console,
        refresh_per_second=8,
        screen=True,
        transient=False,
    )
    live.start()
    _global_now_playing_live = live

    def _worker(interval):
        global _global_now_playing_title, _global_now_playing_input_active, _global_now_playing_url
        last_title = None
        last_url = None
        while True:
            try:
                if _global_now_playing_input_active:
                    sleep(0.1)
                    continue
                url = _global_now_playing_url
                if not url:
                    sleep(interval)
                    continue
                if url != last_url:
                    # reset title state when URL changes
                    last_title = None
                    _global_now_playing_title = ""
                    _update_live_view()
                    last_url = url
                title = get_song_title(url)
                if title and title != last_title:
                    _global_now_playing_title = title
                    _update_live_view()
                    last_title = title
            except Exception as e:
                log.debug(f"live worker error: {e}")
            sleep(interval)

    threading.Thread(target=_worker, args=(interval_seconds,), daemon=True).start()

    def _stop_live():
        try:
            if _global_now_playing_live:
                _global_now_playing_live.stop()
        except Exception:
            pass

    atexit.register(_stop_live)
    return live


def _default_record_filename(curr_station_name: str) -> str:
    now = datetime.datetime.now()
    month_name = now.strftime("%b").upper()
    am_pm = now.strftime("%p")
    ts = now.strftime(f"%d-{month_name}-%Y@%I-%M-%S-{am_pm}")
    return f"{curr_station_name.strip()}-{ts}".replace(" ", "-")


def _normalize_record_path(path_str: str) -> str:
    # Map Linux-style /home/<user>/... to Windows %USERPROFILE% on Windows
    if os.name == "nt" and path_str:
        # Collapse env and user
        path_str = os.path.expandvars(path_str)
        path_str = os.path.expanduser(path_str)
        if path_str.startswith("/home/"):
            parts = path_str.split("/", 3)
            # ['', 'home', '<user>', 'rest...']
            if len(parts) >= 4:
                remainder = parts[3]
                base = os.path.expanduser("~")
                path_str = os.path.join(base, remainder.replace("/", os.sep))
            else:
                path_str = os.path.expanduser("~")
    return os.path.abspath(path_str) if path_str else path_str


def handle_record(
    target_url,
    curr_station_name,
    record_file_path,
    record_file,
    record_file_format,  # auto/mp3
    loglevel,
):
    log.info("Press 'q' to stop recording")
    force_mp3 = False
    if _force_mp3_always:
        force_mp3 = True
        record_file_format = "mp3"

    if record_file_format != "mp3" and record_file_format != "auto":
        record_file_format = "mp3"  # default to mp3
        log.debug("Error: wrong codec supplied!. falling back to mp3")
        force_mp3 = True
    elif record_file_format == "auto":
        log.debug("Codec: fetching stream codec")
        codec = record_audio_auto_codec(target_url)
        if codec is None:
            record_file_format = "mp3"  # default to mp3
            force_mp3 = True
            log.debug("Error: could not detect codec. falling back to mp3")
        else:
            record_file_format = codec
            log.debug("Codec: found {}".format(codec))
    elif record_file_format == "mp3":
        # always save to mp3 to eliminate any runtime issues
        # it is better to leave it on libmp3lame
        force_mp3 = True

    # Normalize target path (fix Linux-style path on Windows)
    if record_file_path:
        record_file_path = _normalize_record_path(record_file_path)

    if record_file_path and not os.path.exists(record_file_path):
        log.debug("filepath: {}".format(record_file_path))
        try:
            os.makedirs(record_file_path, exist_ok=True)
        except Exception as e:
            log.debug(f"Could not create specified path, falling back: {e}")
            record_file_path = os.path.join(os.path.expanduser("~"), "Music", "radioactive")
            os.makedirs(record_file_path, exist_ok=True)

    elif not record_file_path:
        log.debug("filepath: fallback to default path")
        record_file_path = os.path.join(
            os.path.expanduser("~"), "Music", "radioactive"
        )  # fallback path
        try:
            os.makedirs(record_file_path, exist_ok=True)
        except Exception as e:
            log.debug("{}".format(e))
            log.error("Could not make default directory")
            sys.exit(1)

    if not record_file_format.strip():
        record_file_format = "mp3"

    if not record_file:
        record_file = _default_record_filename(curr_station_name)

    tmp_filename = f"{record_file}.{record_file_format}"
    outfile_path = os.path.join(record_file_path, tmp_filename)

    log.info(f"Recording will be saved as: \n{outfile_path}")
    # Update Info panel with one-line status before and after
    try:
        set_info_text(f"Recording… to: {outfile_path}")
    except Exception:
        pass

    record_audio_from_url(target_url, outfile_path, force_mp3, loglevel)

    try:
        set_info_text(f"Recording complete: {outfile_path}")
    except Exception:
        pass


def handle_welcome_screen():
    welcome = make_panel(
        """
        LOAD "RADIO-ACTIVE",8,1

        Play radios around the globe right from your terminal.
        Type '--help' for commands. Press Ctrl+C to quit.
        Project: https://github.com/deep5050/radio-active
        """,
        title="[ui.title]RADIO-ACTIVE[/]",
        width=C64_WIDTH,
    )
    # Use themed console to avoid external theme overrides
    themed_console().print(welcome)


def handle_update_screen(app):
    if app.is_update_available():
        update_msg = (
            "\t[blink]An update available, run [green][italic]pip install radio-active=="
            + app.get_remote_version()
            + "[/italic][/green][/blink]\nSee the changes: https://github.com/deep5050/radio-active/blob/main/CHANGELOG.md"
        )
        update_panel = make_panel(
            update_msg,
            width=C64_WIDTH,
        )
        print(update_panel)
    else:
        log.debug("Update not available")


def handle_favorite_table(alias):
    # Render favorites inside the Live INFO panel
    table = make_table(["Station", "URL / UUID"]) 
    if len(alias.alias_map) > 0:
        for entry in alias.alias_map:
            table.add_row(entry["name"], entry["uuid_or_url"])
        set_info_renderable(table)
        ui_info(f"Your favorite stations are saved in {alias.alias_path}")
    else:
        set_info_lines(["You have no favorite station list"])


def handle_show_station_info():
    """Show important information regarding the current station"""
    global global_current_station_info
    try:
        info = {}
        # Add fields if present
        for k in ("name", "stationuuid", "url", "homepage", "country", "language", "tags", "codec", "bitrate"):
            if isinstance(global_current_station_info, dict) and k in global_current_station_info and global_current_station_info.get(k) not in (None, ""):
                # map key names for nicer labels
                label = {
                    "stationuuid": "uuid",
                    "homepage": "website",
                }.get(k, k)
                info[label] = global_current_station_info.get(k)
        if not info:
            ui_error("No station information available")
        else:
            import json as _json
            set_info_text(_json.dumps(info, indent=2))
    except Exception:
        ui_error("No station information available")


def handle_add_station(alias):
    try:
        left = input("Enter station name:")
        right = input("Enter station stream-url or radio-browser uuid:")
    except EOFError:
        print()
        log.debug("Ctrl+D (EOF) detected. Exiting gracefully.")
        sys.exit(0)

    if left.strip() == "" or right.strip() == "":
        log.error("Empty inputs not allowed")
        sys.exit(1)
    alias.add_entry(left, right)
    log.info("New entry: {}={} added\n".format(left, right))
    sys.exit(0)


def handle_add_to_favorite(alias, station_name, station_uuid_url):
    try:
        response = alias.add_entry(station_name, station_uuid_url)
        if not response:
            try:
                user_input = input("Enter a different name: ")
            except EOFError:
                print()
                log.debug("Ctrl+D (EOF) detected. Exiting gracefully.")
                sys.exit(0)

            if user_input.strip() != "":
                response = alias.add_entry(user_input.strip(), station_uuid_url)
    except Exception as e:
        log.debug("Error: {}".format(e))
        log.error("Could not add to favorite. Already in list?")


def handle_station_uuid_play(handler, station_uuid):
    log.debug("Searching API for: {}".format(station_uuid))

    handler.play_by_station_uuid(station_uuid)

    log.debug("increased click count for: {}".format(station_uuid))

    handler.vote_for_uuid(station_uuid)
    try:
        station_name = handler.target_station["name"]
        station_url = handler.target_station["url"]
    except Exception as e:
        log.debug("{}".format(e))
        log.error("Something went wrong")
        sys.exit(1)

    return station_name, station_url


def check_sort_by_parameter(sort_by):
    accepted_parameters = [
        "name",
        "votes",
        "codec",
        "bitrate",
        "lastcheckok",
        "lastchecktime",
        "clickcount",
        "clicktrend",
        "random",
    ]

    if sort_by not in accepted_parameters:
        log.warning("Sort parameter is unknown. Falling back to 'name'")

        log.warning(
            "choose from: name,votes,codec,bitrate,lastcheckok,lastchecktime,clickcount,clicktrend,random"
        )
        return "name"
    return sort_by


def handle_search_stations(handler, station_name, limit, sort_by, filter_with):
    log.debug("Searching API for: {}".format(station_name))

    return handler.search_by_station_name(station_name, limit, sort_by, filter_with)


def handle_station_selection_menu(handler, last_station, alias):
    # Add a selection list here. first entry must be the last played station
    # try to fetch the last played station's information
    last_station_info = {}
    try:
        last_station_info = last_station.get_info()
    except Exception as e:
        log.debug("Error: {}".format(e))
        # no last station??
        pass

    # log.info("You can search for a station on internet using the --search option")
    title = "Please select a station from your favorite list:"
    station_selection_names = []
    station_selection_urls = []

    # add last played station first
    if last_station_info:
        station_selection_names.append(
            f"{last_station_info['name'].strip()} (last played station)"
        )
        try:
            station_selection_urls.append(last_station_info["stationuuid"])
        except Exception as e:
            log.debug("Error: {}".format(e))
            station_selection_urls.append(last_station_info["uuid_or_url"])

    fav_stations = alias.alias_map
    for entry in fav_stations:
        station_selection_names.append(entry["name"].strip())
        station_selection_urls.append(entry["uuid_or_url"])

    options = station_selection_names
    if len(options) == 0:
        log.info(
            f"{RED_COLOR}No stations to play. please search for a station first!{END_COLOR}"
        )
        sys.exit(0)

    _, index = pick(options, title, indicator="-->")

    # check if there is direct URL or just UUID
    station_option_url = station_selection_urls[index]
    station_name = station_selection_names[index].replace("(last played station)", "")

    if station_option_url.find("://") != -1:
        # direct URL
        station_url = station_option_url
        return station_name, station_url

    else:
        # UUID
        station_uuid = station_option_url
        return handle_station_uuid_play(handler, station_uuid)


def handle_save_last_station(last_station, station_name, station_url):
    last_station = Last_station()

    last_played_station = {}
    last_played_station["name"] = station_name
    last_played_station["uuid_or_url"] = station_url

    log.debug(f"Saving the current station: {last_played_station}")
    last_station.save_info(last_played_station)


def _get_single_key() -> str | None:
    # Windows
    if os.name == "nt" and msvcrt is not None:
        if msvcrt.kbhit():
            try:
                return msvcrt.getwch()
            except Exception:
                return None
        return None
    # POSIX
    if termios and tty and select and sys.stdin.isatty():
        try:
            r, _, _ = select.select([sys.stdin], [], [], 0)
            if r:
                return sys.stdin.read(1)
        except Exception:
            return None
        return None
    return None


class _PosixKeyReader:
    def __enter__(self):
        if os.name != "nt" and termios and tty and sys.stdin.isatty():
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
        else:
            self.fd = None
            self.old = None
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self.fd is not None and self.old is not None:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
        except Exception:
            pass


def _handle_keypress_loop_hotkeys(
    alias,
    handler,
    player,
    target_url,
    station_name,
    station_url,
    record_file_path,
    record_file,
    record_file_format,
    loglevel,
    volume,
):
    def _handle(ch: str):
        nonlocal record_file_format, player, target_url, station_name, station_url
        if ch in ("p", "P"):
            player.toggle()
        elif ch in ("i", "I"):
            handle_show_station_info()
        elif ch in ("r", "R"):
            # Stop live, run recording, then restart live
            if _global_now_playing_live:
                try:
                    _global_now_playing_live.stop()
                except Exception:
                    pass
            handle_record(
                target_url,
                station_name,
                record_file_path,
                record_file,
                record_file_format,
                loglevel,
            )
            if _global_now_playing_live:
                try:
                    _global_now_playing_live.start()
                except Exception:
                    pass
                _update_live_view()
        elif ch in ("n", "N"):
            default_name = _default_record_filename(station_name)
            try:
                fname = safe_input(f"Enter output filename [default: {default_name}]: ")
            except EOFError:
                fname = ""
            if not fname.strip():
                file_name = default_name
                rec_fmt = record_file_format
            else:
                rec_fmt = record_file_format
                try:
                    file_name, file_ext = fname.split(".")
                    if file_ext.lower() == "mp3":
                        rec_fmt = "mp3"
                    else:
                        log.warning("You can only specify mp3 as file extension.")
                        log.warning("Do not provide any extension to autodetect the codec.")
                except Exception:
                    file_name = fname
            if _global_now_playing_live:
                try:
                    _global_now_playing_live.stop()
                except Exception:
                    pass
            handle_record(
                target_url,
                station_name,
                record_file_path,
                file_name,
                rec_fmt,
                loglevel,
            )
            if _global_now_playing_live:
                try:
                    _global_now_playing_live.start()
                except Exception:
                    pass
                _update_live_view()
        elif ch in ("f", "F"):
            handle_add_to_favorite(alias, station_name, station_url)
            set_info_text(f"Added to favorites: {station_name}")
        elif ch in ("w", "W"):
            # Show favorites inside INFO with indices and prompt for selection
            alias.generate_map()
            if not alias.alias_map:
                set_info_text("You have no favorite station list")
                return
            fav_table = Table(show_header=True, header_style="ui.title", expand=True, min_width=C64_WIDTH, box=None)
            fav_table.add_column("ID", justify="right")
            fav_table.add_column("Station", justify="left")
            fav_table.add_column("URL / UUID", justify="left")
            for i, entry in enumerate(alias.alias_map, start=1):
                fav_table.add_row(str(i), entry["name"], entry["uuid_or_url"]) 
            set_info_renderable(fav_table)
            idx0 = _quick_pick_index(len(alias.alias_map))
            if idx0 is None:
                _update_live_view()
                return
            chosen = alias.alias_map[idx0]
            chosen_name = chosen["name"].strip()
            chosen_val = chosen["uuid_or_url"].strip()
            # Resolve to URL if UUID
            if "://" in chosen_val:
                new_name, new_url = chosen_name, chosen_val
            else:
                new_name, new_url = handle_station_uuid_play(handler, chosen_val)
            # Switch playback
            try:
                player.stop()
            except Exception:
                pass
            try:
                from radioactive.ffplay import Ffplay
                if hasattr(player, "program_name") and getattr(player, "program_name", "") == "ffplay":
                    player = Ffplay(new_url, volume, loglevel)
                else:
                    player.start(new_url)
            except Exception as e:
                set_info_text(f"Failed to start: {e}")
                return
            # Update current context and Live header and URL for worker
            station_name = new_name
            station_url = new_url
            target_url = new_url
            try:
                global _global_now_playing_station, _global_now_playing_title, _global_now_playing_url
                _global_now_playing_station = station_name
                _global_now_playing_title = ""
                _global_now_playing_url = new_url
            except Exception:
                pass
            _update_live_view()
            set_info_lines([])
            _update_live_view()
        elif ch in ("t", "T"):
            # Theme chooser inside INFO panel
            names = available_themes()
            theme_table = Table(show_header=True, header_style="ui.title", expand=True, min_width=C64_WIDTH, box=None)
            theme_table.add_column("ID", justify="right")
            theme_table.add_column("Theme", justify="left")
            current = get_active_theme_name()
            for i, name in enumerate(names, start=1):
                label = f"{name} [dim](current)[/]" if name == current else name
                theme_table.add_row(str(i), label)
            set_info_renderable(theme_table)
            idx0 = _quick_pick_index(len(names))
            if idx0 is None:
                _update_live_view()
                return
            chosen = names[idx0]
            # Apply theme to the live console and re-render, then clear INFO
            try:
                if _global_now_playing_live and _global_now_playing_live.console:
                    apply_theme(chosen, console=_global_now_playing_live.console)
                else:
                    apply_theme(chosen, console=None)
            except Exception:
                apply_theme(chosen, console=None)
            set_info_lines([])
            _update_live_view()
        elif ch in ("h", "H", "?"):
            set_info_lines([
                "p: Play/Pause current station",
                "i/info: Station information",
                "r/record: Record a station",
                "n: Record with custom filename",
                "f/fav: Add station to favorite list",
                "w/list: Show favorites and select",
                "t/theme: Theme chooser",
                "h/help/?: Show this help message",
                "q/quit: Quit radioactive",
            ])
        elif ch in ("q", "Q"):
            player.stop()
            sys.exit(0)

    with _PosixKeyReader():
        while True:
            ch = _get_single_key()
            if ch is not None:
                _handle(ch)
            sleep(0.05)


def handle_listen_keypress(
    alias,
    handler,
    player,
    target_url,
    station_name,
    station_url,
    record_file_path,
    record_file,
    record_file_format,
    loglevel,
    volume,
):
    # hotkey loop (cross-platform)
    return _handle_keypress_loop_hotkeys(
        alias,
        handler,
        player,
        target_url,
        station_name,
        station_url,
        record_file_path,
        record_file,
        record_file_format,
        loglevel,
        volume,
    )


def handle_current_play_panel(curr_station_name=""):
    panel_station_name = Text(curr_station_name, justify="center")

    station_panel = make_panel(panel_station_name, title="[ui.title]:radio:[/]", width=C64_WIDTH)
    console = Console()
    console.print(station_panel)


def handle_user_choice_from_search_result(handler, response):
    global global_current_station_info

    if not response:
        log.debug("No result found!")
        sys.exit(0)
    if len(response) == 1:
        # single station found
        log.debug("Exactly one result found")

        try:
            user_input = input("Want to play this station? Y/N: ")
        except EOFError:
            print()
            sys.exit(0)

        if user_input in ["y", "Y"]:
            log.debug("Playing UUID from single response")
            global_current_station_info = response[0]

            return handle_station_uuid_play(handler, response[0]["stationuuid"])
        else:
            log.debug("Quitting")
            sys.exit(0)
    else:
        # multiple station
        log.debug("Asking for user input")

        try:
            log.info("Type 'r' to play a random station")
            user_input = input("Type the result ID to play: ")
        except EOFError:
            print()
            log.info("Exiting")
            log.debug("EOF reached, quitting")
            sys.exit(0)

        try:
            if user_input in ["r", "R", "random"]:
                # pick a random integer withing range
                user_input = randint(1, len(response) - 1)
                log.debug(f"Radom station id: {user_input}")
            # elif user_input in ["f", "F", "fuzzy"]:
            # fuzzy find all the stations, and return the selected station id
            # user_input = fuzzy_find(response)

            user_input = int(user_input) - 1  # because ID starts from 1
            if user_input in range(0, len(response)):
                target_response = response[user_input]
                log.debug("Selected: {}".format(target_response))
                # log.info("UUID: {}".format(target_response["stationuuid"]))

                # saving global info
                global_current_station_info = target_response

                return handle_station_uuid_play(handler, target_response["stationuuid"])
            else:
                log.error("Please enter an ID within the range")
                sys.exit(1)
        except:
            log.err("Please enter an valid ID number")
            sys.exit(1)


def handle_direct_play(alias, station_name_or_url=""):
    """Play a station directly with UUID or direct stream URL"""
    if "://" in station_name_or_url.strip():
        log.debug("Direct play: URL provided")
        # stream URL
        # call using URL with no station name N/A
        # let's attempt to get station name from url headers
        # station_name = handle_station_name_from_headers(station_name_or_url)
        station_name = handle_get_station_name_from_metadata(station_name_or_url)
        return station_name, station_name_or_url
    else:
        log.debug("Direct play: station name provided")
        # station name from fav list
        # search for the station in fav list and return name and url

        response = alias.search(station_name_or_url)
        if not response:
            log.error("No station found on your favorite list with the name")
            sys.exit(1)
        else:
            log.debug("Direct play: {}".format(response))
            return response["name"], response["uuid_or_url"]


def handle_play_last_station(last_station):
    station_obj = last_station.get_info()
    return station_obj["name"], station_obj["uuid_or_url"]


# uses ffprobe to fetch station name
def handle_get_station_name_from_metadata(url):
    """Get ICY metadata from ffprobe"""
    log.info("Fetching the station name")
    log.debug("Attempting to retrieve station name from: {}".format(url))
    # Run ffprobe command and capture the metadata
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_entries",
        "format=icy",
        url,
    ]
    station_name = "Unknown Station"

    try:
        output = subprocess.check_output(cmd).decode("utf-8")
        data = json.loads(output)
        log.debug(f"station info: {data}")

        # Extract the station name (icy-name) if available
        station_name = (
            data.get("format", {}).get("tags", {}).get("icy-name", "Unknown Station")
        )
    except:
        log.error("Could not fetch the station name")

    return station_name


# uses requests module to fetch station name [deprecated]
def handle_station_name_from_headers(url):
    # Get headers from URL so that we can get radio station
    log.info("Fetching the station name")
    log.debug("Attempting to retrieve station name from: {}".format(url))
    station_name = "Unknown Station"
    try:
        # sync call, with timeout
        response = requests.get(url, timeout=5)
        if response.status_code == requests.codes.ok:
            if response.headers.get("Icy-Name"):
                station_name = response.headers.get("Icy-Name")
            else:
                log.error("Station name not found")
        else:
            log.debug("Response code received is: {}".format(response.status_code()))
    except Exception as e:
        # except requests.HTTPError and requests.exceptions.ReadTimeout as e:
        log.error("Could not fetch the station name")
        log.debug(
            """An error occurred: {}
    The response code was {}""".format(
                e, e.errno
            )
        )
    return station_name


def handle_play_random_station(alias):
    """Select a random station from favorite menu"""
    log.debug("playing a random station")
    alias_map = alias.alias_map
    index = randint(0, len(alias_map) - 1)
    station = alias_map[index]
    return station["name"], station["uuid_or_url"]
