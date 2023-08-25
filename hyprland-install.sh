#!/bin/bash

cd /opt

pacman -S --needed base-devel git
git clone https://aur.archlinux.org/paru.git
cd paru
makepkg -si

paru -S alacritty wofi thunar google-chrome-stable
