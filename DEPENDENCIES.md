# Nyxie Dependencies

This file lists everything needed to move and run `Nyxie` on another Ubuntu machine.

## Project paths Nyxie expects

- Assistant folder: `/var/www/project/nyxie/Nyxie`
- Piper binary currently referenced by the assistant: `/var/www/project/nyxie/quiet_partner_tts_env/bin/piper`
- Voice model: `/var/www/project/nyxie/piper_models/en_GB-cori-high.onnx`
- Voice config: `/var/www/project/nyxie/piper_models/en_GB-cori-high.onnx.json`

If you move the project elsewhere, update the path assumptions in [assistant.py](/var/www/project/nyxie/Nyxie/assistant.py:17).

## Required Python packages

These are installed into `Nyxie/nyxie_venv` by `install.sh`:

- `piper-tts`
- `SpeechRecognition`

Optional Python package for microphone capture:

- `PyAudio`

## Required Ubuntu system packages

For splash screen support:

- `python3-gi`
- `gir1.2-gtk-4.0`

For microphone support with `PyAudio`:

- `portaudio19-dev`
- `python3-dev`
- `build-essential`

For audio playback, install at least one of these tool providers:

- `pipewire-bin` for `pw-play`
- `alsa-utils` for `aplay`
- `sox` for `play`
- `pulseaudio-utils` for `paplay`

## Recommended install command on Ubuntu

```bash
sudo apt install \
  python3 python3-venv python3-pip python3-dev build-essential \
  python3-gi gir1.2-gtk-4.0 \
  portaudio19-dev \
  pipewire-bin alsa-utils sox pulseaudio-utils
```

## Python virtual environments involved

Nyxie currently depends on two environments:

1. `Nyxie/nyxie_venv`
   Used for Nyxie's own Python packages like `SpeechRecognition`.

2. `/var/www/project/nyxie/quiet_partner_tts_env`
   Used right now for the `piper` executable that speaks with your voice model.

When transferring the project, either:

1. Copy `quiet_partner_tts_env` too, or
2. Install `piper-tts` into the new machine and update `assistant.py` to point to that `piper` binary.

## Non-Python runtime requirements

- A working desktop session for the GTK splash screen
- An audio output device
- A microphone if you want wake/voice commands by speech
- Internet access may be needed by Google speech recognition used through `SpeechRecognition`

## Files to transfer

- `Nyxie/`
- `piper_models/en_GB-cori-high.onnx`
- `piper_models/en_GB-cori-high.onnx.json`
- `quiet_partner_tts_env/` if you want to preserve the current Piper executable path exactly

## Quick setup on another Ubuntu machine

```bash
cd /var/www/project/nyxie/Nyxie
bash install.sh
nyxie-assistant
```

If `PyAudio` fails with `portaudio.h: No such file or directory`, install:

```bash
sudo apt install portaudio19-dev python3-dev build-essential
```
