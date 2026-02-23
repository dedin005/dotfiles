# dotfiles

Arch Linux / Hyprland desktop configuration.

## contents

- `hypr/` - Hyprland, hypridle, hyprlock configs
- `waybar/` - statusbar config and styles
- `nvim/` - neovim config (lazy.nvim)
- `shell/` - bashrc, bash_profile, aliases
- `git/` - gitconfig
- `scripts/` - standalone tools (recon.py etc)

## install

```bash
git clone https://github.com/dedin005/dotfiles.git ~/dotfiles
cd ~/dotfiles
bash install.sh
```

First run of neovim will auto-install plugins via lazy.nvim.

## notes

- Hyprland keybinds use ALT as main modifier
- Lock: SUPER+L, display off: SUPER+SHIFT+L
- Audio via PipeWire/WirePlumber, default sink set to HDMI
