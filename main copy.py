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

import vlc

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")

        self.setFixedSize(360, 120)

        layout = QVBoxLayout()

        label_description = QLabel("This is a simple music player app")
        label_version = QLabel("Version 0.1")
        label_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label_description)
        layout.addWidget(label_version)

        self.setLayout(layout)

class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class InfoWidget(QWidget):
    def __init__(self, title, artist, album):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(7)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.imageLabel = QLabel()
        pixmap = QPixmap("placeholder.jpg")
        pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)  # Set the size of the image
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.titleLabel = QLabel(f"Title: {title}")
        self.artistLabel = QLabel(f"Artist: {artist}")
        self.albumLabel = QLabel(f"Album: {album}")

        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artistLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.albumLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.imageLabel)
        layout.addSpacing(65)
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.artistLabel)
        layout.addWidget(self.albumLabel)

        self.setLayout(layout)

    def update(self, title, artist, album, image_path):
        self.titleLabel.setText(title)
        self.artistLabel.setText(artist)
        self.albumLabel.setText(album)
    
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)  # Set the size of the image
        self.imageLabel.setPixmap(pixmap)

class ProgressBar(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.currentLabel = QLabel("0:00")
        self.totalLabel = QLabel("4:00")
        self.progressBar = QSlider(Qt.Orientation.Horizontal)
        self.progressBar.setRange(0, 100)

        layout.addWidget(self.currentLabel)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.totalLabel)

        self.setLayout(layout)
        self.setFixedHeight(30)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setFixedSize(400, 600)
        self.setAcceptDrops(True)


        # self.vlc_instance = vlc.Instance()
        # self.player = self.vlc_instance.media_player_new()
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)

        self.current_audio_file = None
        self.temp_files = []

        button_open = QAction("&Open", self)
        button_open.setStatusTip("Open a file")
        button_open.triggered.connect(self.load_audio)

        button_quit = QAction("&Quit", self)
        button_quit.setStatusTip("Quit the application")
        button_quit.triggered.connect(self.close)

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_open)
        file_menu.addSeparator()
        file_menu.addAction(button_quit)

        help_menu = menu.addMenu("&Help")
        

        button_about = QAction("&About", self)
        button_about.setStatusTip("About")
        button_about.triggered.connect(self.show_about_dialog)

        help_menu.addAction(button_about)


        mainLayout = QVBoxLayout()
        bottomLayout = QHBoxLayout()



        self.button_play_pause = QPushButton()
        self.button_play_pause.setIcon(QIcon("media-playback-start.svg"))
        self.button_play_pause.setFixedSize(50, 50)
        self.button_play_pause.clicked.connect(self.play_pause_audio)
        self.button_play_pause.setDisabled(True)


        bottomLayout.addStretch()
        bottomLayout.addWidget(self.button_play_pause)
        bottomLayout.addStretch()


        self.info_widget = InfoWidget("Song Title", "Artist Name", "Album Name")

        mainLayout.addWidget(self.info_widget)

        self.progressBar = ProgressBar()
        mainLayout.addWidget(self.progressBar)

        mainLayout.addLayout(bottomLayout)


        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

        # self.player.positionChanged.connect(self.update_position)
        # self.player.durationChanged.connect(self.update_duration)
        # self.player.playbackStateChanged.connect(self.update_state)

        # self.player.positionChanged.connect(self.position_changed)
        # self.player.durationChanged.connect(self.duration_changed)
        

    def onToolbarButtonClick(self, s):
        print("Button clicked", s)
    
    def show_about_dialog(self):
        dialog = AboutDialog()
        dialog.exec()
    
    def load_audio(self, file_name=None):
        if not file_name:
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.mp3 *.wav *.ogg)")
        if file_name:
            self.current_audio_file = file_name
            self.player.setSource(QUrl.fromLocalFile(file_name))
            print("Loading", file_name)
            audio = MP3(file_name, ID3=EasyID3)
            info_title = audio.get("title", ["Unknown"])[0]
            info_artist = audio.get("artist", ["Unknown"])[0]
            info_album = audio.get("album", ["Unknown"])[0]
            info_genre = audio.get("genre", ["Unknown"])[0]

            audio = MP3(file_name, ID3=ID3)
            album_cover_path = None

            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    cover_hash = hashlib.md5(tag.data).hexdigest()
                    temp_dir = tempfile.gettempdir()
                    album_cover_path = os.path.join(temp_dir, f"{cover_hash}.jpg")

                    if not os.path.exists(album_cover_path):
                        with open(album_cover_path, 'wb') as img:
                            img.write(tag.data)
                        self.temp_files.append(album_cover_path)
                        print(self.temp_files)
                        print("Created new album cover:", album_cover_path)
                    else:
                        print("Using existing album cover:", album_cover_path)
                    break
            
            print(album_cover_path)
            if album_cover_path:
                self.info_widget.update(info_title, info_artist, info_album, album_cover_path)
            else:
                self.info_widget.update(info_title, info_artist, info_album, "placeholder.jpg")

            self.button_play_pause.setDisabled(False)
            self.player.play()
            self.button_play_pause.setIcon(QIcon("media-playback-pause.svg"))

    def play_pause_audio(self):
        # if self.player.mediaStatus == QMediaPlayer.PlaybackState.PlayingState:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            print("Pausing audio")
            self.player.pause()
            self.button_play_pause.setIcon(QIcon("media-playback-start.svg"))
        else:
            if self.current_audio_file:
                print("Playing audio")
                self.player.play()
                self.button_play_pause.setIcon(QIcon("media-playback-pause.svg"))

    def position_changed(self, position):
        if(self.progressBar.progressBar.maximum() != self.player.duration()):
            self.progressBar.progressBar.setMaximum(self.player.duration())

        self.progressBar.progressBar.setValue(position)

        seconds = (position / 1000) % 60
        minutes = (position / 60000) % 60
        hours = (position / 2600000) % 24

        time = QTime(hours, minutes, seconds)
        self.progressBar.currentLabel.setText(time.toString())
        
    def duration_changed(self, duration):
        self.progressBar.progressBar.setRange(0, duration)


    def update_position(self, position):
        self.progressBar.progressBar.setValue(position)
        self.progressBar.currentLabel.setText(f"{position // 60000}:{(position // 1000) % 60:02}")

    def update_duration(self, duration):
        self.progressBar.progressBar.setRange(0, duration)
        self.progressBar.totalLabel.setText(f"{duration // 60000}:{(duration // 1000) % 60:02}")

    def update_state(self):
        print("State changed")
        # print(QMediaPlayer.PlaybackState.PlayingState)
        # if QMediaPlayer.PlaybackState.StoppedState:
        #     self.button_play_pause.setIcon(QIcon("media-playback-start.svg"))
        # elif QMediaPlayer.PlaybackState.PlayingState:
        #     self.button_play_pause.setIcon(QIcon("media-playback-pause.svg"))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_name = url.toLocalFile()
            if file_name.lower().endswith(('.mp3', '.wav', '.ogg')):
                self.load_audio(file_name)
                break

    def cleanup_temp_files(self):
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"Deleted temporary file: {temp_file}")
            except Exception as e:
                print(f"Failed to delete temporary file {temp_file}: {e}")
        self.temp_files = []

    def closeEvent(self, event):
        print("Closing the app")
        print(self.temp_files)
        self.cleanup_temp_files()
        event.accept()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()