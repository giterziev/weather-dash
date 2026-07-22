import os
import threading

from PIL import Image, ImageDraw
import pystray

from .config import ICON_FILE

def create_default_tray_image():
    image = Image.new("RGBA", (64, 64), (16, 24, 39, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((10, 10, 38, 38), fill=(251, 191, 36, 255))
    draw.ellipse((20, 32, 48, 52), fill=(56, 189, 248, 255))
    draw.ellipse((34, 26, 58, 52), fill=(56, 189, 248, 255))
    return image

def load_tray_image():
    if os.path.exists(ICON_FILE):
        try:
            return Image.open(ICON_FILE)
        except Exception:
            pass
    return create_default_tray_image()

class SystemTrayController:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.thread = None

    def start(self):
        if self.icon is not None:
            self.update_tooltip()
            return
        menu = pystray.Menu(
            pystray.MenuItem("Open Weather Dashboard", self.show_app, default=True),
            pystray.MenuItem("Refresh Weather", self.refresh_weather),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.quit_app)
        )
        self.icon = pystray.Icon("Weather Dashboard", load_tray_image(), self.app.get_tray_tooltip(), menu)
        self.thread = threading.Thread(target=self.icon.run, daemon=True)
        self.thread.start()

    def stop(self):
        if self.icon is not None:
            self.icon.stop()
            self.icon = None

    def update_tooltip(self):
        if self.icon is not None:
            self.icon.title = self.app.get_tray_tooltip()

    def show_app(self, icon=None, item=None):
        self.app.after(0, self.app.show_from_tray)

    def refresh_weather(self, icon=None, item=None):
        self.app.after(0, self.app.manual_refresh_weather)

    def quit_app(self, icon=None, item=None):
        self.app.after(0, self.app.quit_application)
