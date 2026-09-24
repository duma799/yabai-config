# YabaDuma Config

MacOS tiling WM setup with dynamic color theming. Built with Yabai, SketchyBar, and [tint](https://github.com/duma799/tint). All scripts are Python-driven for maintainability.

**Tested on MacBook Air M4, macOS 26.2 Tahoe.**

## Showcase

<div align="center">
  <img src="screenshots/1.jpeg" alt="Desktop with tiling windows" width="800"/>
  <p><i>Tiling window management with dynamic wallpaper theming</i></p>
</div>

<div align="center">
  <img src="screenshots/2.png" alt="SketchyBar and window borders" width="800"/>
  <p><i>Custom SketchyBar with system info and JankyBorders integration</i></p>
</div>

### Features
- **Dynamic theming** - Change the wallpaper and everything re-colours: [tint](https://github.com/duma799/tint) watches it (built-in wallpapers too) and builds a readable scheme
- **Tiling window management** - BSP-like layout with Yabai
- **Custom status bar** - SketchyBar with battery, bluetooth, wifi, volume, and workspace indicators
- **Window borders** - JankyBorders with gradient colors from the wallpaper
- **Editor integration** - tint's hook updates VS Code, Zed, Antigravity and Gemini CLI themes to match
- **Keyboard-driven** - Extensive keybinds for window manipulation (see [Keybinds.md](Keybinds.md))

## What's in here

- **Yabai** - tiling WM
- **SKHD** - keyboard shortcuts (see [Keybinds.md](Keybinds.md))
- **JankyBorders** - window borders that pull colors from the wallpaper
- **SketchyBar** - status bar
- **tint** - generates the color scheme from your wallpaper and reloads everything (replaces pywal)


## Dependencies

| Tool | Purpose | Install Command |
|------|---------|-----------------|
| yabai | Tiling window manager | `brew install koekeishiya/formulae/yabai` |
| skhd | Hotkey daemon | `brew install koekeishiya/formulae/skhd` |
| borders | Window borders | `brew install FelixKratz/formulae/borders` |
| sketchybar | Status bar | `brew install FelixKratz/formulae/sketchybar` |
| tint | Color scheme from the wallpaper | `brew tap duma799/tint https://github.com/duma799/tint && brew install duma799/tint/tint` |

**Optional:** `blueutil` for bluetooth status, `kitty` terminal.

**Python:** Scripts use standard library only, no `requirements.txt` needed.

**Font:** Hack Nerd Font for icons - `brew install --cask font-hack-nerd-font`

## Quick Start (Recommended)

1. **Disable SIP partially** for yabai scripting addition. Follow the [yabai wiki](https://github.com/koekeishiya/yabai/wiki/Disabling-System-Integrity-Protection) guide - requires rebooting into recovery mode.

2. **Run the automated installer:**
   ```bash
   git clone https://github.com/duma799/yabaduma-config.git ~/projects/yabaduma-config
   cd ~/projects/yabaduma-config
   ./install.py
   ```

3. **Post-installation:**
   - Grant accessibility permissions when prompted (System Settings → Privacy & Security → Accessibility)
   - Change the wallpaper (System Settings, or `reload-theme backgrounds/koi.jpg`) — tint themes everything
   - `tint doctor` shows what's wired up

## Manual Installation

```bash
# Homebrew (if you don't have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Taps
brew tap koekeishiya/formulae
brew tap FelixKratz/formulae

# Install everything
brew install yabai skhd borders sketchybar
brew tap duma799/tint https://github.com/duma799/tint
brew install duma799/tint/tint

# Clone and link
git clone https://github.com/duma799/yabaduma-config.git ~/projects/yabaduma-config
cd ~/projects/yabaduma-config

ln -sf ~/projects/yabaduma-config/yabairc ~/.yabairc
ln -sf ~/projects/yabaduma-config/skhdrc ~/.skhdrc
mkdir -p ~/.config/skhd
ln -sf ~/projects/yabaduma-config/scripts ~/.config/skhd/scripts
ln -sf ~/projects/yabaduma-config/bordersrc ~/.config/borders/bordersrc
ln -sf ~/projects/yabaduma-config/sketchybar ~/.config/sketchybar

# reload-theme command
mkdir -p ~/.local/bin
ln -sf ~/projects/yabaduma-config/reload-theme.py ~/.local/bin/reload-theme
chmod +x ~/projects/yabaduma-config/reload-theme.py
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

# Editor themes after every colour change
mkdir -p ~/.config/tint/hooks
ln -sf ~/projects/yabaduma-config/reload-theme.py ~/.config/tint/hooks/post-apply

# Start services
brew services start yabai
brew services start skhd
brew services start borders
brew services start sketchybar
tint service install     # re-theme on every wallpaper change, from login
```

After manual install, follow the same post-installation steps as in Quick Start above.



## Usage

Just change the wallpaper — the tint service themes everything from it. Or by hand:

```bash
reload-theme                     # re-theme from the current wallpaper
reload-theme /path/to/image.jpg  # set it as the wallpaper and theme from it
tint apply -m light              # light scheme (also: dark, auto; saved in the tint app)
tint app                         # preview and tweak in the desktop app
tint doctor                      # check the setup
```

tint writes pywal-compatible colors to `~/.cache/wal` (`colors.json`, `colors.sh`…), reloads SketchyBar and borders, then runs `reload-theme` as its hook for the editors. SketchyBar plugins read colors via `colors.py`. Borders reads color6/color4 for the gradient.

To change which colors borders uses, edit `bordersrc`:
```bash
active_color1=$(echo "$color6" | sed 's/#/0xff/')  # try color0-15
active_color2=$(echo "$color4" | sed 's/#/0xff/')
```

## Troubleshooting

**Keybinds not working:** `skhd --restart-service`

**Colours not changing:** run `tint doctor` — it checks wallpaper access, the service, SketchyBar, borders and the hook. The service log is `~/Library/Logs/tint.log`.

**Borders not using the colors:** Check `~/.cache/wal/colors.sh` exists, then `brew services restart borders`

**Bluetooth shows N/A:** Install blueutil - `brew install blueutil`

**Autofocus not working (focus doesn't follow mouse):** The `autofocus` mode requires the yabai scripting addition, which needs passwordless sudo. Create a sudoers entry:
```bash
# Get the hash of your yabai binary
YABAI_HASH=$(shasum -a 256 $(which yabai) | awk '{print $1}')
echo "$(whoami) ALL=(root) NOPASSWD: sha256:${YABAI_HASH} $(which yabai) --load-sa"

# Add it to sudoers (copy the output of the command above)
sudo visudo -f /private/etc/sudoers.d/yabai
```
Without this, `sudo yabai --load-sa` fails silently on launch and autofocus falls back to disabled. You'll need to update the hash after each `brew upgrade yabai`.

**Services acting up:** Restart everything:
```bash
brew services restart yabai skhd borders sketchybar
```

## Links

- [Yabai Wiki](https://github.com/koekeishiya/yabai/wiki)
- [SKHD](https://github.com/koekeishiya/skhd)
- [SketchyBar](https://github.com/FelixKratz/SketchyBar)
- [tint](https://github.com/duma799/tint)
