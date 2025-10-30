<div align=center>
<p align=center><img src=https://user-images.githubusercontent.com/27947066/267328833-3e81a98e-2acb-4291-89cb-f3f9bed6c299.png width=250px></p>
<h1 align=center> RADIOACTIVE </h1>
<p> SEARCH - PLAY - RECORD - REPEAT </p>

 <p align=center >SUPPORT THE ORIGINAL DEVELOPER HERE!</p>
 <p>
<img width="500px" alt="UPI" src="https://raw.githubusercontent.com/deep5050/random-shits-happen-here/main/235618869-8c9d9bce-096d-469e-8f61-c29cc01eacc3%20(1).png">
</p>

<p align=center>
<img align=center src=https://github.com/ms4ndst/radio-active/blob/main/images/main%20gui.png  width=550px>
<hr>


</div>


### Features

- [x] Supports more than 40K stations !! :radio:
- [x] Record audio from live radio on demand :zap:
- [x] Get song information on run-time 🎶
- [x] Saves last station information
- [x] Favorite stations :heart:
- [x] Selection menu for favorite stations
- [x] Theme chooser with multiple color themes (Classic, Gruvbox, Catppuccin, One Dark Pro, Dracula, Solarized, Nord, Monokai, GitHub Dark, Material, Night Owl, Ayu, Tokyo Night)
- [x] Live UI hints/tooltip match the active theme colors
- [x] Supports user-added stations :wrench:
- [x] Looks minimal and user-friendly
- [x] Runs on Raspberry Pi
- [x] Finds nearby stations
- [x] Discovers stations by genre
- [x] Discovers stations by language
- [x] VLC, MPV player support
- [x] Default config file
- [ ] I'm feeling lucky! Play Random stations



### Why radioactive?

While there are various CLI-based radio players like [PyRadio](https://github.com/coderholic/pyradio) and [TERA](https://github.com/shinokada/tera), Radioactive stands out for its simplicity. It's designed to work seamlessly right from the start. You don't need to be a hardcore Linux or Vim expert to enjoy radio stations with Radioactive. The goal of Radioactive is to offer a straightforward user interface that's easy to grasp and comes preconfigured, without unnecessary complexities.

### Credits

This project is a maintained fork of Radio-Active created by Dipankar Pal (deep5050). Huge credit to the original author and contributors for building the foundation.

- Original project: https://github.com/deep5050/radio-active
- This fork focuses on an enhanced Live UI, theming, dynamic width, and improved recording UX while keeping the CLI workflow familiar.

### Install

Console commands installed: `radioactive` and `radio`.

From source:
```
git clone https://github.com/ms4ndst/radio-active.git
cd radio-active
python -m pip install --user -e .
```

On Windows, if the command isn’t found after install, add your user Scripts directory to PATH:
```
python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
```
Add the printed path to your PATH, then restart the terminal.

### External Dependency

It needs [FFmpeg](https://ffmpeg.org/download.html) to be installed on your
system in order to record the audio

on Ubuntu-based system >= 20.04 Run

```
sudo apt update
sudo apt install ffmpeg
```

For other systems including Windows see the above link

#### Installing FFmpeg

FFmpeg is required for this program to work correctly. Install FFmpeg by following these steps:-

- On Linux - <https://www.tecmint.com/install-ffmpeg-in-linux/>
- On Windows - <https://www.wikihow.com/Install-FFmpeg-on-Windows>


### Run

Search a station with `radio --search [STATION_NAME]` or simply `radio` :zap: to select from the favorite menu.

### Tips

1. Use a modern terminal emulator, otherwise the UI might break! (gets too ugly sometimes)
2. On Windows, instead of the default Command Prompt, use the new Windows Terminal or web-based emulators like Hyper, Cmdr, Terminus, etc. for better UI
3. Let the app run for at least 5 seconds (not a serious issue though, for better performance)


### Live UI Prompt

When running with the Live UI (default, including when using `--auto-track`), the input prompt is rendered inside the Live panel, directly below the Now Playing info. You can type commands immediately without losing the panel.

### Themes

- Press `t` during playback to open the Theme chooser inside the INFO window. Select by number to apply instantly.
- The tooltip/hints row automatically adopts the active theme’s colors.
- Available themes:
  - classic (default), gruvbox-dark, catppuccin-mocha
  - one-dark-pro, dracula, solarized-dark, nord, monokai, github-dark
  - material-darker, night-owl, ayu-dark, tokyo-night

### What's New since 2.9.2

- 2.10.1
  - Recording runs in background; press `r` again to stop. INFO shows progress (elapsed, size, bitrate, speed).
  - Filename prompt (`n`) appears inside the INFO window.
  - Panels and keys row auto-size to terminal width (keeps shortcuts on one line).
  - Theme choice is persisted to the config and applied at startup.
- 2.10.0
  - Theme system with in-app Theme chooser (press `t` in playback; choose by number).
  - 13 themes available (classic, gruvbox-dark, catppuccin-mocha, one-dark-pro, dracula, solarized-dark, nord, monokai, github-dark, material-darker, night-owl, ayu-dark, tokyo-night).
  - Tooltip/hints row adopts the active theme colors.
  - INFO panel is cleared after selecting a theme or switching to a favorite for a cleaner view.
- 2.9.3
  - Live layout improvements: persistent header, Now Playing panel, INFO panel below.
  - Favorites (`w`) render inside the INFO panel with numeric selection (no Enter needed; multi-digit supported).
  - Auto-updating track titles; fewer stray logs; improved Windows path handling for recordings.
- 2.9.2
  - Live UI prompt appears inside the Live panel below Now Playing, so you can type without losing the view.
  - Recording UX: INFO shows “Recording…” with full path, then “Recording complete”.
  - New `--force-mp3` flag and matching `force_mp3` config; safer codec autodetect.

### Options


| Options            | Note     | Description                                    | Default       | Values                 |
| ------------------ | -------- | ---------------------------------------------- | ------------- | ---------------------- |
| (No Option)        | Optional | Select a station from menu to play             | False         |                        |
| `--search`, `-S`   | Optional | Station name                                   | None          |                        |
| `--play`, `-P`     | Optional | A station from fav list or url for direct play | None          |                        |
| `--country`, `-C`  | Optional | Discover stations by country code              | False         |                        |
| `--state`          | Optional | Discover stations by country state             | False         |                        |
| `--language`       | optional | Discover stations by                           | False         |                        |
| `--tag`            | Optional | Discover stations by tags/genre                | False         |                        |
| `--uuid`, `-U`     | Optional | ID of the station                              | None          |                        |
| `--record` , `-R`  | Optional | Record a station and save to file              | False         |                        |
| `--filename`, `-N` | Optional | Filename to used to save the recorded audio    | None          |                        |
| `--filepath`       | Optional | Path to save the recordings                    | <DEFAULT_DIR> |                        |
|| `--filetype`, `-T` | Optional | Format of the recording                        | mp3           | `mp3`,`auto`           |
|| `--force-mp3`     | Optional | Force MP3 output for recordings (overrides auto/extension) | False         |                        |
|| `--last`           | Optional | Play last played station                       | False         |                        |
| `--random`         | Optional | Play a random station from favorite list       | False         |                        |
| `--sort`           | Optional | Sort the result page                           | votes         |                        |
| `--filter`         | Optional | Filter search results                          | None          |                        |
| `--limit`          | Optional | Limit the # of results in the Discover table   | 100           |                        |
| `--volume` , `-V`  | Optional | Change the volume passed into ffplay           | 80            | [0-100]                |
| `--favorite`, `-F` | Optional | Add current station to fav list                | False         |                        |
| `--add` , `-A`     | Optional | Add an entry to fav list                       | False         |                        |
| `--list`, `-W`     | Optional | Show fav list                                  | False         |                        |
| `--remove`         | Optional | Remove entries from favorite list              | False         |                        |
| `--flush`          | Optional | Remove all the entries from fav list           | False         |                        |
| `--kill` , `-K`    | Optional | Kill background radios.                        | False         |                        |
| `--loglevel`       | Optional | Log level of the program                       | Info          | `info`,  `warning`, `error`, `debug` |
| `--player`         | Optional | Media player to use                            |  ffplay       | `vlc`, `mpv`, `ffplay`              |

<hr>


> [!NOTE]
> Once you save/play at least one station, invoking `radio` without any options will show a selection menu.
> During playback, press `w` to see your favorites inside the INFO panel; press a number to play it immediately.

> `--search`, `-S`: Search for a station online.

> `--play`, `-P`: You can pass an exact name from your favorite stations or alternatively pass any direct stream URL. This would bypass any user selection menu (useful when running from another script)

> `--uuid`,`-U`: When station names are too long or confusing (or multiple
> results for the same name) use the station's uuid to play. --uuid gets the
> greater priority than `--search`. Example: 96444e20-0601-11e8-ae97-52543be04c81. type `u` on the runtime command to get the UUID of a station.

> `--loglevel`,: Don't need to specify unless you are developing it. `info`, `warning`, `error`, `debug`

> `-F`: Add the current station to your favorite list. Example: `-F my_fav_1`

> `-A`: Add any stations to your list. You can add stations that are not currently available on our API. When adding a new station enter a name and direct URL to the audio stream.

> `--limit`: Specify how many search results should be displayed.

> `--filetype`: Specify the extension of the final recording file. default is `mp3`. you can provide `-T auto` to autodetect the codec and set file extension accordingly (in original form).

> DEFAULT_DIR: Linux/macOS: `/home/user/Music/radioactive`; Windows: `%USERPROFILE%\\Music\\radioactive`

### Runtime Commands

Input a command during the radio playback to perform an action. Available commands are:

```
Enter a command to perform an action: ?

p: Play/Pause current station
i/info: Station information
r/record: Start/Stop recording (background; progress shown in INFO)
n: Record with custom filename (prompt inside INFO)
f/fav: Add station to favorite list
w/list: Show favorites inside INFO and select by number (no Enter needed)
t/theme: Theme chooser (applies instantly, hints recolor)
h/help/?: Show this help message
q/quit: Quit radioactive
```

### Sort Parameters

you can sort the result page with these parameters:
- `name` (default)
- `votes` (based on user votes)
- `codec`
- `bitrate`
- `lastcheckok` (active stations)
- `lastchecktime` (recent active)
- `clickcount` (total play count)
- `clicktrend` (currently trending stations)
- `random`

### Filter Parameters

Filter search results with `--filter`. Some possible expressions are
- `--filter "name=shows"`
- `--filter "name=shows,talks,tv"`
- `--filter "name!=news,shows"`
- `--filter "country=in"`
- `--filter "language=bengali,nepali"`
- `--filter "bitrate>64"`
- `--filter "votes<500"`
- `--filter "codec=mp3"`
- `--filter "tags!=rock,pop"`

Allowed operators are: 

-  `=`
- `,`
- `!=`
- `>`
- `<`
- `&`

Allowed keys are: `name`, `country` (countrycode as value), `language`, `bitrate`, `votes`, `codec`, `tags`

Provide multiple filters at one go, use `&`

A complex filter example: `--filter "country!=CA&tags!=islamic,classical&votes>500"`

> [!NOTE]
> set `--limit` to a higher value while filtering results


### Default Configs

Default configuration file is added into your home directory as `.radio-active-configs.ini`

```bash
[AppConfig]
loglevel = info
limit = 100
sort = votes
filter = none
volume = 80
filepath = /home/{user}/recordings/radioactive/
filetype = mp3
force_mp3 = false
player = ffplay
theme = classic
```

> [!WARNING]
> Do NOT modify the keys, only change the values. you can give any absolute or relative path as filepath.

### Bonus Tips

1. Recording format: all recordings are saved as MP3 by default (libmp3lame). Just enter a filename without any extension (e.g., "talk-show"), and the app will save it as "talk-show.mp3". Supplying another extension is not necessary and will still result in an MP3 file.

2. You don't have to pass the exact option name, a portion of it will also work. for example `--sea` for `--search`, `--coun` for `--country`, `--lim` for `--limit`

3. It's better to leave the `--filetype` as mp3 when you need to record something quickly. The autocodec takes a few milliseconds extra to determine the codec.

### Changes

see [CHANGELOG](./CHANGELOG.md)

### Community

Share you favorite list with  community 🌐 ➡️ [Here](https://github.com/deep5050/radio-active/discussions/10)

> Your favorite list `.radio-active-alias` is under your home directory as a hidden file :)


### Support

<p>
<a href=https://deep5050.github.io/payme>Visit the original creators contribution page for more payment options.
</p>
<p align=center><a href="https://www.buymeacoffee.com/deep5050" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 117px !important;" ></a></p>

### Acknowledgements

<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>


<div align=center>
<img src=https://github.com/deep5050/random-shits-happen-here/assets/27947066/83d08065-c209-4012-abb7-9c0aa64d761b width=400px >
<p align=center> Happy Listening </p>

</div>


## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://www.bjoli.com"><img src="https://avatars.githubusercontent.com/u/48383?v=4?s=100" width="100px;" alt="Joe Smith"/><br /><sub><b>Joe Smith</b></sub></a><br /><a href="https://github.com/deep5050/radio-active/commits?author=Yasumoto" title="Tests">⚠️</a> <a href="https://github.com/deep5050/radio-active/commits?author=Yasumoto" title="Code">💻</a> <a href="#ideas-Yasumoto" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/salehjafarli"><img src="https://avatars.githubusercontent.com/u/81613563?v=4?s=100" width="100px;" alt="salehjafarli"/><br /><sub><b>salehjafarli</b></sub></a><br /><a href="https://github.com/deep5050/radio-active/commits?author=salehjafarli" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/marvoh"><img src="https://avatars.githubusercontent.com/u/5451142?v=4?s=100" width="100px;" alt="marvoh"/><br /><sub><b>marvoh</b></sub></a><br /><a href="https://github.com/deep5050/radio-active/commits?author=marvoh" title="Code">💻</a> <a href="https://github.com/deep5050/radio-active/issues?q=author%3Amarvoh" title="Bug reports">🐛</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

<div align=center>
<p>
<img src=https://stars.medv.io/deep5050/radio-active.svg align=center>
</p>
</div>
