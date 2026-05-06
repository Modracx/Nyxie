# Nyxie

Nyxie is a simple Ubuntu voice assistant that uses your existing Piper voice model at `/var/www/project/nyxie/piper_models/en_GB-cori-high.onnx`.

## Features

- Wake phrases: `hey nyx`, `hey nyxie`, `nyx`, `nyxie`
- Greets you when woken
- Shows a fullscreen splash when woken
- Listens for one simple follow-up voice command
- Speaks replies with the Piper `en_GB-cori-high` model

## Starter commands

- `what time is it`
- `what is today's date`
- `what is your name`
- `open browser`
- `open terminal`
- `open files`
- `lock screen`
- `goodbye`

## Install

```bash
cd /var/www/project/nyxie/Nyxie
bash install.sh
```

Optional service install:

```bash
cd /var/www/project/nyxie/Nyxie
bash install.sh --enable-service
```

## Run

```bash
nyxie-assistant
```

If microphone recognition is unavailable, Nyxie falls back to typed input in the terminal.

The local virtual environment created by the installer is:

```bash
/var/www/project/nyxie/Nyxie/nyxie_venv
```

## Ubuntu packages you may need

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 portaudio19-dev pipewire-bin
```

If `PyAudio` fails to build with `fatal error: portaudio.h: No such file or directory`, install `portaudio19-dev` first, then rerun:

```bash
cd /var/www/project/nyxie/Nyxie
bash install.sh
```
