#!/usr/bin/env python3
"""Nyxie Ubuntu assistant with wake word, splash screen, and Piper TTS."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import wave
import webbrowser
from contextlib import contextmanager, redirect_stderr
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent
PIPER_BIN = ROOT / "quiet_partner_tts_env/bin/piper"
VOICE_MODEL = ROOT / "piper_models/en_GB-cori-high.onnx"
VOICE_CONFIG = ROOT / "piper_models/en_GB-cori-high.onnx.json"
SAMPLE_RATE = 22050
WAKE_ALIASES = {
    "nyx",
    "nyxie",
    "nix",
    "nixi",
    "nixie",
}

try:
    import speech_recognition as sr  # type: ignore
except Exception:
    sr = None

@dataclass(frozen=True)
class CommandResult:
    spoken_text: str
    should_exit: bool = False


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


def is_wake_phrase(text: str) -> bool:
    normalized = normalize_text(text)
    if not normalized:
        return False

    words = normalized.split()
    for word in words:
        if word in WAKE_ALIASES:
            return True

    for first, second in zip(words, words[1:]):
        if first == "hey" and second in WAKE_ALIASES:
            return True

    return False


def _find_audio_player() -> str | None:
    for player in ("pw-play", "paplay", "aplay", "play"):
        path = shutil.which(player)
        if path:
            return path
    return None


def _write_wav(raw_pcm: bytes, wav_path: Path) -> None:
    with wave.open(str(wav_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(raw_pcm)


def speak(text: str) -> None:
    text = text.strip()
    if not text:
        return

    if not PIPER_BIN.exists():
        print(f"Missing Piper binary: {PIPER_BIN}")
        return
    if not VOICE_MODEL.exists() or not VOICE_CONFIG.exists():
        print(f"Missing voice model files: {VOICE_MODEL} / {VOICE_CONFIG}")
        return

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        wav_path = Path(temp_file.name)

    try:
        proc = subprocess.run(
            [str(PIPER_BIN), "-m", str(VOICE_MODEL), "-c", str(VOICE_CONFIG), "--output-raw"],
            input=text.encode("utf-8"),
            capture_output=True,
            check=True,
        )
        if not proc.stdout:
            raise RuntimeError("Piper produced no audio.")
        _write_wav(proc.stdout, wav_path)

        player = _find_audio_player()
        if not player:
            print(text)
            print("No audio player found. Install pw-play, paplay, aplay, or play.")
            return

        subprocess.run([player, str(wav_path)], check=False, timeout=30)
    except Exception as exc:
        print(f"TTS playback failed: {exc}")
        print(text)
    finally:
        wav_path.unlink(missing_ok=True)


def speak_async(text: str) -> threading.Thread:
    thread = threading.Thread(target=speak, args=(text,), daemon=True)
    thread.start()
    return thread


class _NullTextIO:
    def write(self, _: str) -> int:
        return 0

    def flush(self) -> None:
        return None


@contextmanager
def _suppress_stderr() -> TextIO:
    previous_stderr_fd = None
    devnull_fd = None
    stream: TextIO = _NullTextIO()
    try:
        previous_stderr_fd = os.dup(2)
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull_fd, 2)
    except OSError:
        previous_stderr_fd = None
        devnull_fd = None

    try:
        with redirect_stderr(stream):
            yield stream
    finally:
        if previous_stderr_fd is not None:
            os.dup2(previous_stderr_fd, 2)
            os.close(previous_stderr_fd)
        if devnull_fd is not None:
            os.close(devnull_fd)


def listen_with_microphone(prompt: str) -> str | None:
    if sr is None:
        return None

    try:
        recognizer = sr.Recognizer()
        with _suppress_stderr():
            with sr.Microphone() as source:
                print(prompt)
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
        heard = recognizer.recognize_google(audio)
        print(f"Heard: {heard}")
        return heard
    except Exception as exc:
        print(f"Voice input failed: {exc}")
        return None


def listen(prompt: str) -> str:
    heard = listen_with_microphone(prompt)
    if heard:
        return heard

    try:
        return input("Type a wake phrase or command: ").strip()
    except EOFError:
        return ""


def _open_terminal() -> bool:
    for terminal in (
        "gnome-terminal",
        "kgx",
        "x-terminal-emulator",
        "konsole",
        "xfce4-terminal",
    ):
        path = shutil.which(terminal)
        if path:
            subprocess.Popen([path])
            return True
    return False


def _open_file_manager() -> bool:
    for manager in ("nautilus", "xdg-open", "thunar", "dolphin"):
        path = shutil.which(manager)
        if path:
            target = str(Path.home())
            command = [path, target] if manager != "xdg-open" else [path, target]
            subprocess.Popen(command)
            return True
    return False


def _lock_screen() -> bool:
    for command in (
        ["loginctl", "lock-session"],
        ["gnome-screensaver-command", "--lock"],
        ["xdg-screensaver", "lock"],
    ):
        if shutil.which(command[0]):
            subprocess.Popen(command)
            return True
    return False


def process_command(command: str) -> CommandResult:
    normalized = normalize_text(command)
    if not normalized:
        return CommandResult("I did not catch that command.")

    if "time" in normalized:
        return CommandResult(datetime.now().strftime("It is %I:%M %p."))

    if any(phrase in normalized for phrase in ("what day", "what date", "today", "date")):
        return CommandResult(datetime.now().strftime("Today is %A, %B %d, %Y."))

    if any(phrase in normalized for phrase in ("your name", "who are you", "name")):
        return CommandResult("I am Nyxie, your Ubuntu assistant.")

    if any(phrase in normalized for phrase in ("open browser", "open web", "browser", "web")):
        webbrowser.open("https://www.google.com")
        return CommandResult("Opening the browser.")

    if any(phrase in normalized for phrase in ("open terminal", "terminal", "console")):
        if _open_terminal():
            return CommandResult("Opening a terminal.")
        return CommandResult("I could not find a terminal application.")

    if any(phrase in normalized for phrase in ("open files", "open file manager", "file manager", "files")):
        if _open_file_manager():
            return CommandResult("Opening your files.")
        return CommandResult("I could not find a file manager.")

    if any(phrase in normalized for phrase in ("lock screen", "lock computer", "lock")):
        if _lock_screen():
            return CommandResult("Locking the screen.")
        return CommandResult("I could not lock the screen from this session.")

    if any(phrase in normalized for phrase in ("goodbye", "good bye", "quit", "exit", "sleep", "stop listening")):
        return CommandResult("Goodbye. I will wait quietly.", should_exit=True)

    return CommandResult(
        "I can help with the time, date, browser, terminal, files, screen lock, or goodbye."
    )


def greet_and_show_splash() -> None:
    greeting = "Hello. Nyxie is listening."
    tts_thread = speak_async(greeting)
    subprocess.Popen(
        [shutil.which("python3") or "python3", str(APP_DIR / "splash.py"), "NYXIE", greeting, "3.8"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    tts_thread.join(timeout=8)


def check_runtime() -> int:
    if not PIPER_BIN.exists():
        print(f"Missing Piper binary: {PIPER_BIN}")
        return 1
    if not VOICE_MODEL.exists() or not VOICE_CONFIG.exists():
        print(f"Missing voice model files: {VOICE_MODEL} / {VOICE_CONFIG}")
        return 1
    return 0


def main() -> int:
    os.environ.setdefault("DISPLAY", ":0")
    if os.environ.get("XDG_SESSION_TYPE") == "wayland":
        os.environ.setdefault("WAYLAND_DISPLAY", "wayland-0")

    status = check_runtime()
    if status:
        return status

    print("Nyxie assistant started.")
    print("Wake phrases: hey nyx, hey nyxie, nyx, or nyxie.")
    if sr is None:
        print("SpeechRecognition is unavailable. Falling back to typed input.")

    try:
        while True:
            raw_text = listen("Listening for wake phrase...")
            if not raw_text:
                continue

            if not is_wake_phrase(raw_text):
                print("Waiting for wake phrase: hey nyx or hey nyxie.")
                continue

            greet_and_show_splash()
            command_text = listen("Please say one simple command.")
            if not command_text:
                speak("I did not hear a command.")
                continue

            result = process_command(command_text)
            speak(result.spoken_text)
            if result.should_exit:
                return 0
    except KeyboardInterrupt:
        print("Exiting Nyxie.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
