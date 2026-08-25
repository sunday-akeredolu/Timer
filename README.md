# Timer

A professional-grade countdown timer with custom messaging, built with Python and Tkinter. Designed for streamers, presenters, and developers who need a clean, overlay-style countdown with transparency support.

## Features

- **Custom countdown timer** with hours, minutes, and seconds input
- **Overlay mode** — transparent, borderless window that stays on top
- **Presets** — save and manage frequently used timer durations
- **Custom message** — display overlay text during countdown with adjustable scale
- **Fullscreen toggle** — expand overlay to cover entire screen
- **Pause / Resume** — control the countdown mid-run
- **Danger alerts** — background flashing and audio beep when time is running low
- **Progress bar** — visual countdown progress at the bottom of the overlay
- **Draggable overlay** — move the countdown window anywhere on screen
- **Dynamic resizing** — fonts scale automatically when resizing the overlay
- **Dark mode title bar** — immersive dark theme on Windows
- **Welcome screen** — cinematic boot sequence on first launch
- **About dialog** — app info, credits, and developer portfolio

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `S` | Start timer |
| `P` | Pause / Resume |
| `R` | Reset timer |
| `Q` | Quit app |
| `Escape` | Exit fullscreen (main) / Close overlay (countdown) |
| `Space` | Pause / Resume (countdown overlay only) |

## Getting Started

### Prerequisites

- Python 3.x
- Windows (for `winsound` and DWM dark mode features)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/timer.git
   cd timer
   ```

2. Run the app:
   ```bash
   python timer.py
   ```

## Usage

1. Set the countdown duration using the **HOURS**, **MINS**, and **SECS** fields.
2. Optionally enter an **overlay message** and adjust its **scale**.
3. Click **START** or press `S` to begin the countdown.
4. A borderless overlay window appears — drag it to position.
5. Use `P` to pause/resume, `R` to reset, or `Q` to quit.
6. Toggle fullscreen with the ⛶ button or resize freely.

## Tech Stack

- **Python 3**
- **Tkinter** — GUI framework
- **ctypes** — Windows DWM dark mode integration
- **winsound** — audio alerts

## Configuration

Settings and presets are saved automatically to `timer_presets.json` in the app directory.

## Developer

Built by [sunday](https://lightskyblue-wolverine-224124.hostingersite.com/)
