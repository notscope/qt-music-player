import sys
import os, hashlib

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

import tempfile
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal, QTime
from PyQt6.QtGui import QColor, QPalette, QPixmap, QIcon, QAction, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QApplication, QToolBar, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QSizePolicy, QFileDialog, QDialog, QMessageBox

from components.color import Color

class PlaybackControl(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)


        self.button_play_pause = QPushButton()
        self.button_play_pause.setIcon(QIcon("media-playback-start.svg"))
        self.button_play_pause.setFixedSize(50, 50)
        
        layout.addWidget(self.button_play_pause)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setFixedSize(700, 300)
        self.setAcceptDrops(True)

        mainLayout = QHBoxLayout()
        playbackLayout = QVBoxLayout()

        self.imageLabel = QLabel()
        pixmap = QPixmap("placeholder.jpg")
        pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)  # Set the size of the image
        self.imageLabel.setPixmap(pixmap)

        playback_control = PlaybackControl()
        mainLayout.addWidget(self.imageLabel)
        mainLayout.addSpacing(5)
        mainLayout.addStretch()
        playbackLayout.addWidget(Color("red"))
        playbackLayout.addWidget(playback_control)

        mainLayout.addLayout(playbackLayout, 1)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()