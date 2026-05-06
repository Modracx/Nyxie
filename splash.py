#!/usr/bin/env python3
"""Fullscreen splash screen for Nyxie."""

from __future__ import annotations

import html
import os
import sys


def show_splash(title: str, message: str, duration: float = 4.0) -> None:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        from gi.repository import GLib, Gdk, Gtk
    except Exception as exc:
        print(f"Splash unavailable: {exc}")
        return

    safe_title = html.escape(title)
    safe_message = html.escape(message)

    css = b"""
    window {
        background:
            radial-gradient(circle at top, rgba(88, 160, 255, 0.22), rgba(7, 10, 19, 0.96) 42%),
            linear-gradient(160deg, #050810 0%, #0a1020 52%, #04060b 100%);
    }
    #card {
        background: rgba(14, 22, 40, 0.84);
        border: 1px solid rgba(140, 184, 255, 0.18);
        border-radius: 28px;
        padding: 28px 34px;
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
    }
    #title {
        color: #e8f1ff;
        font-size: 36px;
        font-weight: 800;
        letter-spacing: 0.22em;
    }
    #message {
        color: #c7d8ff;
        font-size: 20px;
        font-weight: 500;
    }
    #hint {
        color: rgba(199, 216, 255, 0.68);
        font-size: 13px;
        letter-spacing: 0.08em;
    }
    """

    class SplashWindow(Gtk.ApplicationWindow):
        def __init__(self, app: Gtk.Application):
            super().__init__(application=app)
            self.set_title("Nyxie")
            self.set_decorated(False)
            self.fullscreen()
            self.set_hide_on_close(True)

            provider = Gtk.CssProvider()
            provider.load_from_data(css)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

            overlay = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            overlay.set_vexpand(True)
            overlay.set_hexpand(True)
            overlay.set_valign(Gtk.Align.CENTER)
            overlay.set_halign(Gtk.Align.CENTER)

            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
            card.set_widget_name("card")
            card.set_halign(Gtk.Align.CENTER)
            card.set_valign(Gtk.Align.CENTER)
            card.set_margin_top(40)
            card.set_margin_bottom(40)
            card.set_margin_start(40)
            card.set_margin_end(40)
            card.set_size_request(640, -1)

            title_label = Gtk.Label()
            title_label.set_widget_name("title")
            title_label.set_use_markup(True)
            title_label.set_markup(safe_title)
            title_label.set_justify(Gtk.Justification.CENTER)

            message_label = Gtk.Label()
            message_label.set_widget_name("message")
            message_label.set_use_markup(True)
            message_label.set_wrap(True)
            message_label.set_wrap_mode(2)
            message_label.set_justify(Gtk.Justification.CENTER)
            message_label.set_max_width_chars(34)
            message_label.set_markup(safe_message)

            hint_label = Gtk.Label(label="VOICE ASSISTANT ACTIVE")
            hint_label.set_widget_name("hint")
            hint_label.set_justify(Gtk.Justification.CENTER)

            card.append(title_label)
            card.append(message_label)
            card.append(hint_label)
            overlay.append(card)
            self.set_child(overlay)

    class SplashApp(Gtk.Application):
        def __init__(self):
            super().__init__(application_id="io.nyxie.splash")
            self.connect("activate", self.on_activate)

        def on_activate(self, app: Gtk.Application) -> None:
            window = SplashWindow(app)
            window.present()
            GLib.timeout_add(int(duration * 1000), self.quit)

    os.environ.setdefault("DISPLAY", ":0")
    app = SplashApp()
    app.run(None)


def main() -> int:
    title = sys.argv[1] if len(sys.argv) > 1 else "NYXIE"
    message = sys.argv[2] if len(sys.argv) > 2 else "Hello. Nyxie is listening."
    duration = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
    show_splash(title, message, duration)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
