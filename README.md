# e-ink

Minimal driver for the Pimoroni **Inky Impression 7.3"** (7-colour, 800×480) running on a Raspberry Pi.

This project replaces a previous [InkyPi](https://github.com/fatihak/InkyPi) install with something small and direct: a thin wrapper around the official [`inky`](https://github.com/pimoroni/inky) Python library plus a few CLI commands.

## Layout

```
src/einkd/        Python package: display wrapper + CLI
scripts/install.sh   Provision a venv on the Pi
scripts/uninstall.sh Tear it back down
systemd/eink.service Optional template (not installed by default)
requirements.txt
```

## Hardware assumptions

- Raspberry Pi (tested on Pi Zero)
- Inky Impression 7.3" auto-detected via the HAT EEPROM.

## Install on the Pi

From your dev machine:

```bash
rsync -a --delete --exclude .git --exclude __pycache__ \
    ~/Github/e-ink/ lucas@192.168.86.53:/home/lucas/e-ink/
'cd ~/e-ink && bash scripts/install.sh'
```

`install.sh` creates `~/e-ink/.venv`, installs the `inky` library + Pillow with system site-packages enabled (so `RPi.GPIO`/`spidev` Just Work), and installs an `eink` console script into the venv.

## Use

```bash
source ~/e-ink/.venv/bin/activate

eink hello                       # render a hello-world test pattern
eink clear                       # blank the screen to white
eink text "Hello world"          # render some text, centred
eink image path/to/photo.jpg     # show an image (auto-fit + saturation)
eink info                        # print detected display info
```

## Uninstall

```bash
bash ~/e-ink/scripts/uninstall.sh
```
