from core.clicker import Autoclicker
from core.settings import Settings
from ui.main_window import MainWindow
from ui.overlay import Overlay

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QObject, QTimer

from pynput import keyboard

# helpers
class Bridge(QObject):
    start_requested = Signal()
    stop_reqested = Signal()
    exit_requested = Signal()

# main
def main():
    app = QApplication([])

    # setup
    settings = Settings()
    bridge = Bridge()

    overlay = Overlay(settings)
    window = MainWindow(settings)
    clicker = Autoclicker(window, settings, overlay, bridge)

    # helpers
    def normalize_key(key):
        if hasattr(key, "char") and key.char:
            return key.char.lower()
        return str(key).replace("Key.", "").lower()

    def shutdown():
        # print(f"[{time.perf_counter():.3f}] : Shutting down...", flush=True)

        clicker.stop()

        QTimer.singleShot(0, listener.stop)
        QTimer.singleShot(0, app.quit)

    def on_press(key):
        try:
            toggle_key = settings.get("Keybinds", "toggle")
            exit_key = settings.get("Keybinds", "kill")
            overlay_key = settings.get("Keybinds", "overlay")
            
            def _keybind_changed():
                nonlocal toggle_key, exit_key, overlay_key
                toggle_key = settings.get("Keybinds", "toggle")
                exit_key = settings.get("Keybinds", "kill")
                overlay_key = settings.get("Keybinds", "overlay")

            settings.changed.connect(_keybind_changed)

            # convert to str (mr gpt wrote this single line for me)
            key_str = normalize_key(key)

            if key_str == toggle_key:
                if clicker.running:
                    bridge.stop_reqested.emit()
                else:
                    bridge.start_requested.emit()

            elif key_str == exit_key:
                bridge.exit_requested.emit()
            
            elif key_str == overlay_key:
                current = settings.get_bool("Overlay", "enabled")
                settings.set_bool("Overlay", "enabled", not current)
        
        except Exception as e:
            print("callback error:", e)

    # function
    bridge.exit_requested.connect(shutdown)
    bridge.start_requested.connect(clicker.start)
    bridge.stop_reqested.connect(clicker.stop)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    window.show()
    app.exec()

# entry point
if __name__ == "__main__":
    main()