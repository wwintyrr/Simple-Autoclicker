from pynput.mouse import Controller, Button

from PySide6.QtCore import QTimer, QObject, QPoint
from PySide6.QtGui import QCursor

import time

# button mapping
map = {
    "left": Button.left,
    "right": Button.right,
    "middle": Button.middle,
}

# main
class Autoclicker(QObject):
    def __init__(self, window, settings, overlay, bridge):
        super().__init__()

        self.window = window
        self.settings = settings
        self.overlay = overlay

        self.mouse = Controller()

        self.timer = QTimer()
        self.timer.timeout.connect(self._click_loop)

        self.running = False
        self.clicks_remaining = None

        self.start_time = None

        self.window.start_button.clicked.connect(self.toggle)
    
    # control
    def start(self):
        if self.running:
            return
        
        interval = self._get_interval()

        repeat = self.settings.get_bool("Click", "repeat")
        button = self.settings.get("Click", "button")
        amount = self.settings.get_int("Click", "amount")

        self.at_mouse = self.settings.get_bool("Click", "at_mouse")
        self.mouse_x = None
        self.mouse_y = None
        if not self.at_mouse:
            self.mouse_x = self.settings.get_int("Click", "at_pos_x")
            self.mouse_y = self.settings.get_int("Click", "at_pos_y")

        self.mouse_button = map[button]

        self.clicks_remaining = None if repeat else amount
        self.interval_ms = int(interval * 1000)

        self.start_time = time.perf_counter()
        print(f"[{self.start_time:.3f}] : Starting (interval: {self.interval_ms} ms)")

        self.running = True

        self.timer.start(self.interval_ms)

        self.overlay.set_state(True)
        self.window.update_status(True)
    
    def stop(self):
        if not self.running:
            return
        
        self.running = False
        self.timer.stop()

        if self.start_time is not None:
            end_time = time.perf_counter()
            duration = end_time - self.start_time
            print(f"[{end_time:.3f}] : Stopped (ran {duration:.1f} s)")
        
        self.overlay.set_state(False)
        self.window.update_status(False)

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()
    
    # internals
    def _click_loop(self):
        if not self.running:
            return
        
        global_pos = QCursor.pos()
        local_pos = self.window.mapFromGlobal(global_pos)

        if not self.at_mouse:
            self.mouse.position = (self.mouse_x, self.mouse_y)

        if self.window.rect().contains(local_pos):
            return
        
        #limited clicks
        if self.clicks_remaining is not None:
            if self.clicks_remaining <= 0:
                self.stop()
                return
            self.clicks_remaining -= 1
        
        self.mouse.click(self.mouse_button)
    
    def _get_interval(self):
        mins = self.settings.get_int("Speed", "minutes")
        secs = self.settings.get_int("Speed", "seconds")
        ms = self.settings.get_int("Speed", "milliseconds")

        return (mins * 60) + secs + (ms / 1000)