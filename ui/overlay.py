from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor

class Overlay(QWidget):
    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        self.setFixedSize(80, 80)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.overlay_enabled = settings.get_bool("Overlay", "enabled")
        self.clicker_running = False

        self.move(10, 10)
        
        self.bind_settings()
        self.apply_settings()

    # only for startup
    def apply_settings(self):
        self.overlay_enabled = self.settings.get_bool("Overlay", "enabled")

        opacity = self.settings.get_int("Overlay", "opacity") / 100
        self.setWindowOpacity(opacity)

        if self.overlay_enabled:
            self.show()
        else:
            self.hide()

    # settings bind
    def bind_settings(self):
        self.settings.changed.connect(self.on_setting_changed)
    
    def on_setting_changed(self, section, key, value):
        if section != "Overlay":
            return

        if key == "enabled":
            if self.settings.get_bool("Overlay", "enabled"):
                self.show()
            else:
                self.hide()
        
        elif key == "opacity":
            self.setWindowOpacity(int(value) / 100)
    
    def set_state(self, enabled):
        self.clicker_running = enabled
        self.update()
    
    # qt stuff, dont touch the name
    def paintEvent(self, event):
        painter = QPainter(self)

        color = QColor("green") if self.clicker_running else QColor("red")

        painter.setBrush(color)
        painter.setPen(Qt.NoPen)

        painter.drawEllipse(0, 0, 20, 20)