from PySide6.QtCore import Qt, QTimer, QThread
from PySide6.QtWidgets import (
    QMainWindow, QSizePolicy, 
    QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QCheckBox, QComboBox, QSpinBox, QSlider, QFrame, QLineEdit,
)
from PySide6.QtGui import QCloseEvent

from pynput import mouse, keyboard

import ui.css_styles as css_styles

import time

# thanks gpt for this
on_off = [
    'Off <span style="color:red;">○</span>',
    'On <span style="color:lime;">●</span>'
]

# ui elements
class LineEditor(QLineEdit):
    def __init__(self, default_text, typeable, parent=None):
        super().__init__(parent)

        self.default_text = default_text
        self.has_user_text = False
        self.typeable = typeable

        self.setPlaceholderText(default_text)

        if not typeable:
            self.setReadOnly(True)
        
        self.setText(default_text)
        self.setStyleSheet(css_styles.line_edit_style["no_focus"])
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)

    def focusInEvent(self, e):
        if self.typeable:
            if not self.has_user_text and self.text() == self.default_text:
                self.clear()
                self.setStyleSheet(css_styles.line_edit_style["focus"])

            super().focusInEvent(e)
    
    def focusOutEvent(self, e):
        if self.typeable:
            if not self.text().strip():
                self.setStyleSheet(css_styles.line_edit_style["no_focus"])
                self.setText(self.default_text)
                self.has_user_text = False
            else:
                self.has_user_text = True

            super().focusOutEvent(e)

class Setting(QWidget):
    def __init__(self, name: str, section=None, key=None, type="label", settings=None, options=None, range=None, parent=None):
        super().__init__(parent)

        self.value = None
        self.main_element = None

        self.row = QHBoxLayout()
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.row)

        self.label = QLabel(name)
        self.label.setStyleSheet(css_styles.borderless_label_style)

        self._updating = False

        self.section = section
        self.key = key
        self.settings = settings

        if settings:
            settings.changed.connect(self._on_external_change)

        # idek dont ask me why i did this like this, it just felt right at the time
        # composition would probably be a much better way of handling this
        if type == "checkbox":
            checkbox = QCheckBox()
            checkbox.setStyleSheet(css_styles.checkbox_style)
            self.state_label = QLabel("Placeholder")
            self.state_label.setStyleSheet(css_styles.check_label_style)

            self.main_element = checkbox

            value = settings.get_bool(section, key)
            checkbox.setChecked(value)
            self.state_label.setText("Enabled" if value else "Disabled")

            def _on_check():
                if self._updating:
                    return

                checked = checkbox.isChecked()
                self.state_label.setText("Enabled" if checked else "Disabled")
                settings.set(section, key, checked)

            checkbox.toggled.connect(_on_check)

            self.row.addWidget(self.label, 11)
            self.row.addWidget(checkbox, 2)
            self.row.addWidget(self.state_label, 5)
        elif type == "button":
            button = QPushButton("Edit")
            button.setStyleSheet(css_styles.button_style)

            self.main_element = button

            self.row.addWidget(self.label, 6)
            self.row.addWidget(button, 4)
        elif type == "text":
            text_edit = LineEditor("...", True)
            text_edit.setStyleSheet(css_styles.line_edit_style["focus"])

            self.main_element = text_edit

            self.row.addWidget(self.label, 6)
            self.row.addWidget(text_edit, 4)
        elif type == "combo":
            combo_box = QComboBox()
            combo_box.setStyleSheet(css_styles.combo_box_style)

            self.main_element = combo_box

            if options:
                combo_box.addItems(options)

            self.row.addWidget(self.label, 6)
            self.row.addWidget(combo_box, 4)

            value = settings.get(section, key)
            index = combo_box.findText(value.capitalize())
            if index != -1:
                combo_box.setCurrentIndex(index)

            combo_box.currentTextChanged.connect(
                lambda v: None if self._updating else settings.set(section, key, v.lower())
            )
        elif type == "spin":
            spin_box = QSpinBox()
            spin_box.setStyleSheet(css_styles.spin_box_style)
            if range:
                spin_box.setRange(*range)

            self.main_element = spin_box

            value = settings.get_int(section, key)
            spin_box.setValue(value)

            spin_box.valueChanged.connect(
                lambda v: None if self._updating else settings.set(section, key, v)
            )

            self.row.addWidget(self.label, 6)
            self.row.addWidget(spin_box, 4)
        elif type == "slider":
            slider = QSlider(Qt.Orientation.Horizontal)
            label = QLabel("0")
            label.setFixedWidth(40)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(css_styles.label_style)
            if range:
                slider.setRange(*range)

            self.main_element = slider

            value = settings.get_int(section, key)
            slider.setValue(value)
            label.setText(str(value))

            def _on_slider_change(v):
                settings.set(section, key, v)

                if self._updating:
                    return
                
                label.setText(str(v))

            slider.valueChanged.connect(_on_slider_change)

            self.row.addWidget(self.label, 13)
            self.row.addWidget(slider, 6)
            self.row.addWidget(label, 3)
        else:
            self.row.addWidget(self.label)
        
    def _on_external_change(self, section, key, value):
        if self.section and section != self.section:
            return

        if self.key and key != self.key:
            return

        self._updating = True
        try:
            if isinstance(self.main_element, QCheckBox):
                checked = self.settings.get_bool(section, key)
                self.main_element.setChecked(checked)
                if self.state_label:
                    self.state_label.setText("Enabled" if checked else "Disabled")

            elif isinstance(self.main_element, QComboBox):
                v = self.settings.get(section, key)
                index = self.main_element.findText(v.capitalize())
                if index != -1:
                    self.main_element.setCurrentIndex(index)

            elif isinstance(self.main_element, QSpinBox):
                self.main_element.setValue(self.settings.get_int(section, key))

            elif isinstance(self.main_element, QSlider):
                v = self.settings.get_int(section, key)
                self.main_element.setValue(v)
        
        finally:
            self._updating = False

class Keybind(QWidget):
    def __init__(self, name: str, settings, key, parent=None):
        super().__init__(parent)

        self.main_element = None
        self.unbind = None

        self.settings = settings
        self.key = key

        self.row = QHBoxLayout()
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.row)

        self.label = QLabel(name)
        self.label.setStyleSheet(css_styles.borderless_label_style)

        self.main_element = QPushButton("Unbinded")

        self.unbind = QPushButton("𝖷")
        self.unbind.setStyleSheet(css_styles.button_style)

        self.row.addWidget(self.label, 12)
        self.row.addWidget(self.main_element, 7)
        self.row.addWidget(self.unbind, 1)

        self.current_bind = self.settings.get("Keybinds", key)
        if self.current_bind and self.current_bind != "None":
            self.main_element.setStyleSheet(css_styles.button_style)
            self.main_element.setText(self.current_bind)
        else:
            self.main_element.setStyleSheet(css_styles.unbinded_style)
            self.main_element.setText("Unbinded")

        self.main_element.clicked.connect(self._start_bind)
        self.unbind.clicked.connect(self._on_unbind)

    def update(self, value):
        pass  

    # binding logic
    def _on_unbind(self):
        self.main_element.setText("Unbinded")
        self.main_element.setStyleSheet(css_styles.unbinded_style)
        self.current_bind = "None"
        self.settings.set("Keybinds", self.key, "None")
    
    def _on_bind(self, value):
        self.main_element.setText(value)
        self.main_element.setStyleSheet(css_styles.button_style)
        self.current_bind = value
        self.settings.set("Keybinds", self.key, value.lower())
    
    # listener logic
    def _start_bind(self):
        self.main_element.setText("Press a key...")

        QTimer.singleShot(
            100,
            self._start_listener
        )
        
    def _start_listener(self):
        self.listener = keyboard.Listener(
            on_press=self._set_bind
        )
        self.listener.start()
    
    def _set_bind(self, key):
        try:
            value = key.char.upper()
        except AttributeError:
            value = str(key).replace("Key.","").lower()

        self._on_bind(value)

        self.listener.stop()

        return False

# main window
class MainWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()

        self.settings_ui = {}
        self.keybinds_ui = {}
        self.profiles_ui = {}

        self.status_ui = None
        self.start_button = None
        self.settings = settings
        
        # size
        self.setWindowTitle("Autoclicker")
        self.setFixedSize(400, 150)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        # center
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(5, 5, 5, 5)

        # tabs
        self.tabs = QTabWidget()

        self.tabs.addTab(self._create_main_tab(), "Main")
        self.tabs.addTab(self._create_settings_tab(), "Click Settings")
        self.tabs.addTab(self._create_keybinds_tab(), "Keybinds")
        self.tabs.addTab(self._create_profiles_tab(), "Profiles")

        layout.addWidget(self.tabs)

    # methods
    def update_status(self, status):
        if self.status_ui:
            if status:
                self.status_ui.setText("Autoclicker: " + on_off[1])
            else:
                self.status_ui.setText("Autoclicker: " + on_off[0])
        pass
    
    def closeEvent(self, event):
        print(f"[{time.perf_counter():.3f}] : Shutting down...", flush=True)

    # internals
    def _spacer(self):
        spacer = QFrame()
        spacer.setFixedHeight(1)
        spacer.setFrameShadow(QFrame.Shadow.Plain)
        spacer.setFrameShape(QFrame.Shape.HLine)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 5, 40, 5)

        layout.addWidget(spacer)

        return container

    def _create_main_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        layout.setContentsMargins(4, 4, 4, 4)

        label = QLabel("Autoclicker: " + on_off[0])
        label.setStyleSheet(css_styles.label_style)
        self.status_ui = label

        button = QPushButton(f"Press or toggle keybind ({self.settings.get("Keybinds", "toggle").upper()}) to start")
        self.settings.changed.connect(lambda: button.setText(f"Press or toggle keybind ({self.settings.get("Keybinds", "toggle").upper()}) to start"))

        button.setStyleSheet(css_styles.button_style)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.start_button = button

        layout.addWidget(label, 4)
        layout.addWidget(button, 6)

        return tab
    
    def _create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.verticalScrollBar().setSingleStep(5)
        scroll.verticalScrollBar().setPageStep(15)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # click settings
        button_type = Setting("Mouse click", "Click", "button", "combo", self.settings, options=["Left", "Right", "Middle"])
        repeat = Setting("Repeat untill stopped", "Click", "repeat", "checkbox", self.settings)
        amount = Setting("Amount to repeat (if not inf)", "Click", "amount", "spin", self.settings, options=None, range=(1, 10000))
        at_mouse = Setting("Click at mouse", "Click", "at_mouse", "checkbox", self.settings)
        at_position = Setting("Position to click", section=None, key=None, type="button")

        # position set logic
        self.at_pos_button = at_position.main_element
        self.at_pos_button.clicked.connect(
            self._start_position_pick
        )
        self.at_pos_button.setText(f"({self.settings.get_int("Click", "at_pos_x")}, {self.settings.get_int("Click", "at_pos_y")})")

        # overlay settings
        overlay_onoff = Setting("Overlay enabled", "Overlay", "enabled", "checkbox", self.settings)
        opacity = Setting("Overlay opacity", "Overlay", "opacity", "slider", self.settings, options=None, range=(0, 100))

        # repeat settings
        minutes = Setting("Minutes between clicks", "Speed", "minutes", "spin", self.settings, options=None, range=(0, 10))
        seconds = Setting("Seconds between clicks", "Speed", "seconds", "spin", self.settings, options=None, range=(0, 59))
        mili = Setting("Milliseconds between clicks", "Speed", "milliseconds", "spin", self.settings, options=None, range=(0, 999))

        # this sucks but oh well
        content_layout.addWidget(button_type)
        content_layout.addWidget(repeat)
        content_layout.addWidget(amount)
        content_layout.addWidget(at_mouse)
        content_layout.addWidget(at_position)

        content_layout.addWidget(self._spacer())

        content_layout.addWidget(overlay_onoff)
        content_layout.addWidget(opacity)

        content_layout.addWidget(self._spacer())

        content_layout.addWidget(minutes)
        content_layout.addWidget(seconds)
        content_layout.addWidget(mili)

        # profile saving split
        profile_row = QHBoxLayout()

        profile_name = LineEditor("Enter profile name", True)
        save_button = QPushButton("Save")
        save_button.setStyleSheet(css_styles.button_style)

        profile_row.addWidget(profile_name, 8)
        profile_row.addWidget(save_button, 2)

        content_layout.addWidget(self._spacer())
        content_layout.addLayout(profile_row)

        scroll.setWidget(content)

        layout.addWidget(scroll)

        return tab
    
    def _create_keybinds_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.verticalScrollBar().setSingleStep(5)
        scroll.verticalScrollBar().setPageStep(15)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # operational keybinds
        on_off_keybind = Keybind("Toggle autoclicker on/off", self.settings, "toggle")
        force_kill_keybind = Keybind("Exit autoclicker (force kill)", self.settings, "kill")

        # other keybinds
        toggle_overlay = Keybind("Toggle overlay on/off", self.settings, "overlay")

        content_layout.addWidget(on_off_keybind)
        content_layout.addWidget(force_kill_keybind)

        content_layout.addWidget(self._spacer())

        content_layout.addWidget(toggle_overlay)

        scroll.setWidget(content)

        layout.addWidget(scroll)

        return tab
    
    def _create_profiles_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # top split
        top_row = QHBoxLayout()

        profile_label = QLabel("Current profile: Default")
        profile_label.setStyleSheet(css_styles.profile_label_style)

        button = QComboBox()
        button.addItems(["Default"])
        button.setStyleSheet(css_styles.combo_box_style)

        top_row.addWidget(profile_label)
        top_row.addWidget(button)

        # bottom ui
        bottom_row = QHBoxLayout()
        bottom_left = QVBoxLayout()
        bottom_right = QHBoxLayout()

        # bottom left (profile quick settings display)
        click_settings_label = QLabel("Click settings: (...)")
        click_settings_label.setStyleSheet(css_styles.borderless_label_style)

        click_repeat_label = QLabel("Repeat settings: (...)")
        click_repeat_label.setStyleSheet(css_styles.borderless_label_style)
        click_repeat_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        bottom_left.addWidget(click_settings_label, 1)
        bottom_left.addWidget(click_repeat_label, 1)

        # bottom right (profile load/delete options)
        profile_load_button = QPushButton("Load")
        profile_load_button.setStyleSheet(css_styles.button_style)
        profile_load_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        profile_delete_button = QPushButton("Delete")
        profile_delete_button.setStyleSheet(css_styles.button_style)
        profile_delete_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        bottom_right.addWidget(profile_load_button, 1)
        bottom_right.addWidget(profile_delete_button, 1)

        # bottom cross split
        bottom_row.addLayout(bottom_left, 1)
        bottom_row.addLayout(bottom_right, 1)

        # all tg
        layout.addLayout(top_row, 1)
        layout.addLayout(bottom_row, 2)

        return tab
    
    # click pos logic
    def _start_position_pick(self):
        self.at_pos_button.setText("(Click anywhere)")

        QTimer.singleShot(100, self._start_listener)
    
    def _start_listener(self):
        self.position_listener = mouse.Listener(
            on_click=self._on_position_click
        )
        self.position_listener.start()
    
    def _on_position_click(self, x, y, button, pressed):
        if not pressed:
            return
        
        self.settings.set("Click", "at_pos_x", x)
        self.settings.set("Click", "at_pos_y", y)

        self.position_listener.stop()

        self.at_pos_button.setText(f"({x}, {y})")

        return False