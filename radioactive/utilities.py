"""Handler functions for __main__.py"""

import datetime
import json
import os
import subprocess
import sys
from random import randint
from time import sleep
import threading
import atexit

import requests
from pick import pick
from rich import print
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from zenlog import log

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
_global_now_playing_input_active = False
_force_mp3_always = False


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
    title = Text(station_name or "Unknown Station", style="bold cyan", justify="center")
    body = Text(f"🎶 {track_title or 'Fetching…'}", justify="center")
    return Panel(body, title=title, width=85)


def _make_now_playing_view(station_name: str, track_title: str, hints: str, messages: list[str]):
    # Top: Now Playing panel
    panel_now = _make_now_playing_panel(station_name, track_title)
    # Middle: Info panel
    body = Text("\n".join(messages) if messages else "")
    panel_info = Panel(body, title="[b]Info[/b]", width=85)
    # Bottom: Keys
    hints_text = Text.from_markup(hints) if hints else Text("")
    return Group(panel_now, panel_info, hints_text)


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
    global _global_now_playing_messages
    _global_now_playing_messages = [text.rstrip("\n")] if text else []
    _update_live_view()


def set_info_lines(lines: list[str]):
    global _global_now_playing_messages
    _global_now_playing_messages = [l.rstrip("\n") for l in lines]
    _update_live_view()


def safe_input(prompt: str) -> str:
    """Prompt for input below the Live view (under the Keys row).

    Uses a stop/start cycle for Rich Live (pause is not available in rich==14.x).
    """
    global _global_now_playing_live, _global_now_playing_input_active
    if _global_now_playing_live is not None:
        _global_now_playing_input_active = True
        try:
            # Stop live rendering so the prompt can render beneath the Keys row
            try:
                _global_now_playing_live.stop()
            except Exception:
                pass
            # print a separator newline and prompt
            try:
                _global_now_playing_live.console.print("")
            except Exception:
                pass
            value = _global_now_playing_live.console.input(prompt)
        finally:
            # Restart live and restore the view
            try:
                _global_now_playing_live.start()
            except Exception:
                pass
            _global_now_playing_input_active = False
            _update_live_view()
        return value
    # fallback if Live not running
    return input(prompt)


def set_force_mp3(flag: bool):
    global _force_mp3_always
    _force_mp3_always = bool(flag)


def start_now_playing_live(station_name: str, target_url: str, interval_seconds: int = 15) -> Live:
    """Start Live UI and a background worker that updates song title."""
    global _global_now_playing_live, _global_now_playing_station, _global_now_playing_title
    global _global_now_playing_hints, _global_now_playing_messages

    _global_now_playing_station = station_name
    _global_now_playing_title = ""
    _global_now_playing_hints = "[dim]Keys:[/dim] p=Play/Pause  t=Track  i=Info  r=Record  n=RecordFile  f=Fav  w=List  h=Help  q=Quit"
    _global_now_playing_messages = []

    live = Live(
        _make_now_playing_view(_global_now_playing_station, _global_now_playing_title, _global_now_playing_hints, _global_now_playing_messages),
        refresh_per_second=8,
        screen=False,
        transient=False,
    )
    live.start()
    _global_now_playing_live = live

    def _worker(url, interval):
        global _global_now_playing_title, _global_now_playing_input_active
        last = None
        while True:
            try:
                if _global_now_playing_input_active:
                    sleep(0.1)
                    continue
                title = get_song_title(url)
                if title and title != last:
                    _global_now_playing_title = title
                    _update_live_view()
                    last = title
            except Exception as e:
                log.debug(f"live worker error: {e}")
            sleep(interval)

    threading.Thread(target=_worker, args=(target_url, interval_seconds), daemon=True).start()
    atexit.register(lambda: (_global_now_playing_live and _global_now_playing_live.stop()))
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
    welcome = Panel(
        """
        :radio: Play any radios around the globe right from this Terminal [yellow]:zap:[/yellow]!
        :smile: Author: Dipankar Pal
        :question: Type '--help' for more details on available commands
        :bug: Visit: https://github.com/deep5050/radio-active to submit issues
        :star: Show some love by starring the project on GitHub [red]:heart:[/red]
        :dollar: You can donate me at https://deep5050.github.io/payme/
        :x: Press Ctrl+C to quit
        """,
        title="[b]RADIOACTIVE[/b]",
        width=85,
        expand=True,
        safe_box=True,
    )
    print(welcome)


def handle_update_screen(app):
    if app.is_update_available():
        update_msg = (
            "\t[blink]An update available, run [green][italic]pip install radio-active=="
            + app.get_remote_version()
            + "[/italic][/green][/blink]\nSee the changes: https://github.com/deep5050/radio-active/blob/main/CHANGELOG.md"
        )
        update_panel = Panel(
            update_msg,
            width=85,
        )
        print(update_panel)
    else:
        log.debug("Update not available")


def handle_favorite_table(alias):
    # log.info("Your favorite station list is below")
    table = Table(
        show_header=True,
        header_style="bold magenta",
        min_width=85,
        safe_box=False,
        expand=True,
    )
    table.add_column("Station", justify="left")
    table.add_column("URL / UUID", justify="left")
    if len(alias.alias_map) > 0:
        for entry in alias.alias_map:
            table.add_row(entry["name"], entry["uuid_or_url"])
        # Render and replace Info panel
        cap = Console(record=True, width=85)
        cap.print(table)
        set_info_text(cap.export_text())
        log.info(f"Your favorite stations are saved in {alias.alias_path}")
    else:
        log.info("You have no favorite station list")


def handle_show_station_info():
    """Show important information regarding the current station"""
    global global_current_station_info
    custom_info = {}
    try:
        custom_info["name"] = global_current_station_info["name"]
        custom_info["uuid"] = global_current_station_info["stationuuid"]
        custom_info["url"] = global_current_station_info["url"]
        custom_info["website"] = global_current_station_info["homepage"]
        custom_info["country"] = global_current_station_info["country"]
        custom_info["language"] = global_current_station_info["language"]
        custom_info["tags"] = global_current_station_info["tags"]
        custom_info["codec"] = global_current_station_info["codec"]
        custom_info["bitrate"] = global_current_station_info["bitrate"]
        import json as _json
        set_info_text(_json.dumps(custom_info, indent=2))
    except:
        log.error("No station information available")


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
    player,
    target_url,
    station_name,
    station_url,
    record_file_path,
    record_file,
    record_file_format,
    loglevel,
):
    def _handle(ch: str):
        nonlocal record_file_format
        if ch in ("p", "P"):
            player.toggle()
        elif ch in ("t", "T"):
            # show track title once
            title = get_song_title(target_url)
            set_info_text(title if title else "No track information available")
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
            alias.generate_map()
            handle_favorite_table(alias)
        elif ch in ("h", "H", "?"):
            set_info_lines([
                "p: Play/Pause current station",
                "t/track: Current track info",
                "i/info: Station information",
                "r/record: Record a station",
                "n: Record with custom filename",
                "f/fav: Add station to favorite list",
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
    player,
    target_url,
    station_name,
    station_url,
    record_file_path,
    record_file,
    record_file_format,
    loglevel,
):
    # hotkey loop (cross-platform)
    return _handle_keypress_loop_hotkeys(
        alias,
        player,
        target_url,
        station_name,
        station_url,
        record_file_path,
        record_file,
        record_file_format,
        loglevel,
    )


def handle_current_play_panel(curr_station_name=""):
    panel_station_name = Text(curr_station_name, justify="center")

    station_panel = Panel(panel_station_name, title="[blink]:radio:[/blink]", width=85)
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
