#!/bin/bash
# dotfiles install script
# creates symlinks from repo into correct locations

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

symlink() {
    local src="$1"
    local dst="$2"
    mkdir -p "$(dirname "$dst")"
    if [ -e "$dst" ] && [ ! -L "$dst" ]; then
        mv "$dst" "$dst.bak"
        echo "backed up existing $dst"
    fi
    ln -sf "$src" "$dst"
    echo "linked $dst"
}

# Shell
symlink "$DOTFILES/shell/bashrc"       "$HOME/.bashrc"
symlink "$DOTFILES/shell/bash_profile" "$HOME/.bash_profile"
symlink "$DOTFILES/shell/aliases"      "$HOME/.aliases"

# Git
symlink "$DOTFILES/git/gitconfig" "$HOME/.gitconfig"

# Neovim
symlink "$DOTFILES/nvim/init.lua" "$HOME/.config/nvim/init.lua"

# Hyprland
symlink "$DOTFILES/hypr/hyprland.conf"      "$HOME/.config/hypr/hyprland.conf"
symlink "$DOTFILES/hypr/hypridle.conf"      "$HOME/.config/hypr/hypridle.conf"
symlink "$DOTFILES/hypr/hyprlock.conf"      "$HOME/.config/hypr/hyprlock.conf"
symlink "$DOTFILES/hypr/scripts/lock-and-off.sh" "$HOME/.config/hypr/scripts/lock-and-off.sh"

# Waybar
symlink "$DOTFILES/waybar/config" "$HOME/.config/waybar/config"
symlink "$DOTFILES/waybar/style.css" "$HOME/.config/waybar/style.css"

echo "done"
