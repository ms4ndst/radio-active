# WARP.md — radio-active developer guide

This repository contains the radio-active CLI: search, play, and record internet radio stations from your terminal.

Key facts
- Language: Python (>= 3.6)
- Entry points: radioactive, radio (both map to radioactive.__main__:main)
- External dependency: FFmpeg (ffplay and ffprobe used for playback/metadata)
- Packaging: setuptools (setup.py), Makefile with common tasks

Prerequisites
- Python 3.6+
- FFmpeg installed and available on PATH (ffplay, ffprobe)
  - Windows: add the FFmpeg bin directory to PATH. Verify with: ffplay -version and ffprobe -version

Recommended dev setup
- Create a virtual environment, install dependencies, and install the package in editable mode
  - Windows (PowerShell)
    - python -m venv .venv
    - .\.venv\Scripts\Activate.ps1
  - macOS/Linux (bash/zsh)
    - python3 -m venv .venv
    - source .venv/bin/activate
  - Install deps and package
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
    - pip install -e .[dev]
  - Alternative: use Makefile
    - make install-dev  # editable install + dev dependencies

Run the CLI
- Basic
  - radioactive --help
  - radioactive  # selection menu appears after you have favorites/last-station saved
- Common commands
  - Search by name
    - radioactive --search "jazz"
  - Direct play from favorites or a URL
    - radioactive --play "<favorite-name>"  or  radioactive --play "https://stream.example/playlist.m3u8"
  - Play by UUID (preferred when names are ambiguous)
    - radioactive --uuid <STATION_UUID>
  - Discover
    - radioactive --country <ISO2>      # e.g., SE, US, IN
    - radioactive --state "<state>"
    - radioactive --language "<lang>"
    - radioactive --tag "<genre>"
    - Limit/sort/filter examples: --limit 50 --sort votes --filter "hls:1,bitrate:>64"
  - Favorites
    - radioactive --add                 # add an entry interactively (name + URL/UUID)
    - radioactive --favorite "<name>"   # save current station under a favorite name
    - radioactive --list                # show favorites
    - radioactive --remove              # remove entries interactively
    - radioactive --flush               # clear all favorites
  - Last/random
    - radioactive --last
    - radioactive --random              # play a random station from favorites (if available)
  - Player options
    - radioactive --player ffplay|vlc|mpv
    - radioactive --volume 0..100 (step 10)
  - Recording
    - radioactive --record [-N "MyFile"] [--filepath "C:/path" | ~/Music/radioactive] [--filetype mp3|auto]
      - Use --filetype auto to auto-detect codec; falls back to mp3 if unknown
  - Process control
    - radioactive --kill                # kill background ffplay processes started by radio-active

Development workflow (Makefile)
- Formatting and imports
  - make format        # black formatting (setup.py and radioactive/*)
  - make isort         # sort imports
- Lint
  - make check         # flake8 (error-only + stats pass)
- Tests
  - make test          # runs pytest (tests under ./tests/ if present)
- Build and install locally
  - make build         # python setup.py build
  - make install       # pip install -e .
- Package distributions
  - make dist          # python setup.py sdist bdist_wheel (outputs under dist/)
- Upload (requires credentials)
  - make test-deploy   # upload to TestPyPI via twine
  - make deploy        # upload to PyPI via twine

Manual packaging (optional)
- python -m pip install --upgrade build twine
- python -m build                # produces sdist + wheel in dist/
- python -m twine upload dist/*  # or use -r testpypi for TestPyPI

Key files
- setup.py             # package metadata, entry points (radioactive, radio), extras_require["dev"]
- requirements.txt     # runtime dependencies (requests, psutil, pyradios==1.0.2, rich, pick, zenlog, ...)
- requirements-dev.txt # dev tools (flake8, black, twine)
- Makefile             # convenience targets for lint/format/test/build/release
- radioactive/         # application source (args, __main__, utilities, etc.)

Troubleshooting
- FFmpeg not found or playback doesn’t start
  - Ensure ffplay and ffprobe are installed and on PATH; relaunch terminal after PATH changes
- Terminal UI glitches
  - Use a modern terminal (Windows Terminal, Hyper, etc.). Legacy consoles may render poorly
- “No stations found” by name
  - Try exact name or UUID (radioactive --uuid <id>); you can display UUID during runtime via the UI prompts
- Log levels
  - Accepted values: error, warning, info (default), debug
- Recording
  - Default save dir (if none provided): ~/Music/radioactive; ensure it exists or is creatable

Notes
- On Windows, Ctrl+C triggers graceful shutdown; the app may sleep on the main thread to keep the process alive when using ffplay
- Volume applies to ffplay only; for VLC/MPV, their own volume behavior applies

