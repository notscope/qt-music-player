from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")

        self.setFixedSize(360, 120)

        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowTitleHint)

        layout = QVBoxLayout()

        label_description = QLabel("This is a simple music player app")
        label_version = QLabel("Version 0.1")
        label_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label_description)
        layout.addWidget(label_version)

        self.setLayout(layout)