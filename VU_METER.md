# VU Meter Feature

## Overview
A retro-style animated VU (Volume Unit) meter has been added to the radio-active UI, displaying between the INFO panel and the keyboard shortcuts row.

## Visual Design
- **20 vertical bars** that animate in real-time
- **Color-coded levels:**
  - 🟢 Green: Normal levels (bottom ~55%)
  - 🟡 Yellow: Medium-high levels (~55-78%)
  - 🔴 Red: High levels (top ~22%)
- **Animated:** Bars fluctuate randomly to simulate audio levels
- **Retro aesthetic:** Matches the C64-inspired theme of radio-active

## Features
- **Toggle on/off:** Press `v` or `V` during playback to enable/disable the VU meter
- **Enabled by default:** VU meter shows automatically when playing a station
- **Theme-aware:** Integrates seamlessly with the active color theme

## Usage

### Keyboard Shortcuts
During radio playback, the following keys control the VU meter:
- `v` / `V` - Toggle VU meter display on/off

### Updated Keyboard Hints
The keyboard shortcuts row now shows:
```
Keys: p=Play/Pause  i=Info  r=Record  n=RecordFile  f=Fav  w=List  t=Theme  v=VU  h=Help  q=Quit
```

### Help Menu
Press `h` or `?` during playback to see the updated help menu which includes:
```
v/vu: Toggle VU meter display
```

## Technical Details

### Implementation
- **Location:** `radioactive/utilities.py`
- **Functions:**
  - `_make_vu_meter()` - Generates the animated VU meter display
  - VU meter state stored in `_vu_meter_enabled` (global variable)
  - Integrated into `_make_now_playing_view()` layout function

### Layout Structure
The Live UI now has this structure (top to bottom):
1. **Header Panel** - "RADIO-ACTIVE" with help text
2. **Now Playing Panel** - Station name and current track
3. **INFO Panel** - Dynamic information display
4. **VU Meter** - Animated audio level visualization ← NEW
5. **Keyboard Hints** - Available hotkeys

### Animation
- VU meter updates every time the Live view refreshes (typically 4 times per second)
- Each bar's height randomly fluctuates ±3 levels to create smooth animation
- Bars range from 1-18 units in height

## Example
```
┌─────────────────────────── RADIO-ACTIVE ───────────────────────────┐
│       Play radios from your terminal — press h for help, q to quit       │
└─────────────────────────────────────────────────────────────────────┘
┌────────────────────────── Jazz FM 91.1 ─────────────────────────────┐
│                    🎶 Miles Davis - So What                              │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────── INFO ────────────────────────────────┐
│                 Playing smooth jazz from New York                        │
│                    Bitrate: 320kbps | Codec: MP3                         │
└─────────────────────────────────────────────────────────────────────┘
                     ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ █ ▁ █
                     ▁ ▁ ▁ ▁ █ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ ▁ █ ▁ █
                     ▁ ▁ ▁ ▁ █ ▁ ▁ ▁ ▁ ▁ ▁ █ ▁ ▁ ▁ ▁ ▁ █ ▁ █
                     ▁ ▁ ▁ ▁ █ ▁ █ ▁ ▁ ▁ ▁ █ █ ▁ ▁ ▁ ▁ █ ▁ █
                     ▁ ▁ ▁ ▁ █ ▁ █ ▁ ▁ ▁ ▁ █ █ █ ▁ ▁ ▁ █ ▁ █
                     ▁ ▁ ▁ ▁ █ ▁ █ ▁ ▁ ▁ ▁ █ █ █ ▁ ▁ █ █ ▁ █
                     ▁ ▁ ▁ ▁ █ ▁ █ ▁ ▁ █ ▁ █ █ █ ▁ █ █ █ ▁ █
                     ▁ ▁ █ ▁ █ ▁ █ ▁ ▁ █ ▁ █ █ █ █ █ █ █ ▁ █
                     ▁ ▁ █ ▁ █ ▁ █ ▁ ▁ █ █ █ █ █ █ █ █ █ ▁ █
                     █ ▁ █ ▁ █ █ █ ▁ ▁ █ █ █ █ █ █ █ █ █ █ █
                     █ █ █ █ █ █ █ ▁ ▁ █ █ █ █ █ █ █ █ █ █ █
                     █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █
                     ───────────────────────────────────────
Keys: p=Play/Pause  i=Info  r=Record  n=RecordFile  f=Fav  w=List  t=Theme  v=VU  h=Help  q=Quit
```

## Testing
The VU meter can be tested independently using:
```bash
python test_vu_meter.py
```

This displays just the animated VU meter for visual verification.

## Future Enhancements
Potential improvements for future versions:
- Real-time audio level analysis (requires additional audio processing libraries)
- Configurable number of bars
- Different visualization styles (horizontal bars, spectrum analyzer, etc.)
- Customizable color schemes per theme
- Save VU meter preference to config file

## Credits
Inspired by the retro sci-fi movie theme aesthetic shown in the reference image.
