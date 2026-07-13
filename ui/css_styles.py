button_style = """
QPushButton {
    background-color: #2b2b2b;
    color: white;

    border: 1px solid #555;
    border-radius: 5px;

    padding: 6px 10px;

    min-height: 15px;
}

QPushButton:hover {
    background-color: #3a3a3a;
}

QPushButton:pressed {
    background-color: #1f1f1f;
}
"""

label_style = """
QLabel {
    background-color: #2b2b2b;
    color: white;

    border: 1px solid #555;
    border-radius: 5px;

    padding: 6px 10px;

    min-height: 15px;
}
"""

unbinded_style = """
QPushButton {
    background-color: #2b2b2b;
    color: grey;

    border: 1px solid #555;
    border-radius: 5px;

    padding: 6px 10px;

    min-height: 15px;
}

QPushButton:hover {
    background-color: #3a3a3a;
}

QPushButton:pressed {
    background-color: #1f1f1f;
}
"""

profile_label_style = """
QLabel {  
    background-color: #2b2b2b;
    color: white;

    border: 1px solid #555;
    border-radius: 5px;

    padding: 6px 10px;

    min-height: 10px;
}
"""

borderless_label_style = """
QLabel {
    background-color: transparent;
    color: white;  

    padding: 6px 10px;
    min-height: 15px;
}
"""

check_label_style = """
QLabel {
    background-color: transparent;
    color: grey;  

    padding: 6px 10px;
    min-height: 15px;
}
"""

combo_box_style = """
QComboBox {
    background-color: #2b2b2b;
    color: white;

    border: 1px solid #555;
    border-radius: 5px;

    padding: 6px 10px;

    min-height: 15px;
}

QComboBox::drop-down {
    border: 1px solid #555;
    border-radius: 5px;

    width: 18px;
    
    background-color: #3a3a3a;
}
QComboBox::drop-down:hover {
    background-color: #4a4a4a;
}

QComboBox::down-arrow {
    image: url(assets/down_arrow.png);

    width: 12px;
    height: 12px;
}
"""

spin_box_style = """
QSpinBox {
    background-color: #2b2b2b;
    color: white;

    border: 1px solid #555;
    border-radius: 5px;

    padding: 6px 10px;

    min-height: 15px;
}
QSpinBox::up-button {
    background-color: #3a3a3a;

    border-left: 1px solid #555;
    border-top-right-radius: 5px;
    border-top-left-radius: 5px;

    width: 16px;

    image: url(assets/up_arrow.png);
}
QSpinBox::down-button {
    background-color: #3a3a3a;

    border-left: 1px solid #555;
    border-bottom-right-radius: 5px;
    border-bottom-left-radius: 5px;

    width: 16px;

    image: url(assets/down_arrow.png);
}

QSpinBox::up-button:hover,
QSpinBox::down-button:hover {
    background-color: #4a4a4a;
}
"""

checkbox_style = """
QCheckBox {
    color: white;

    spacing: 6px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;

    border: 1px solid #555;
    border-radius: 4px;

    background-color: #2b2b2b;
}

QCheckBox::indicator:checked {
    image: url(assets/x_box.png);
    
}
"""

line_edit_style = {"focus":"""
QLineEdit {
    background-color: #2b2b2b;
    color: white;

    padding: 6px 10px;

    min-height: 15px;
}
""",
"no_focus": """
QLineEdit {
    background-color: #2b2b2b;
    color: grey;

    padding: 6px 10px;

    min-height: 15px;
}
"""}

spacer = """
QFrame {
    color: #555;
    background-color: #555;

    max-height: 1px;
}
"""