import sys
import os
import hashlib
import tempfile

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal, QTime
from PyQt6.QtGui import QColor, QPalette, QPixmap, QIcon, QAction, QDragEnterEvent, QDropEvent, QFont
from PyQt6.QtWidgets import QApplication, QToolBar, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QSizePolicy, QFileDialog, QDialog, QMessageBox


from components.about_dialog import AboutDialog
from components.color import Color


class ClickableSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            value = self.minimum() + (self.maximum() - self.minimum()) * event.position().x() / self.width()
            self.setValue(int(value))
            event.accept()
        super().mousePressEvent(event)

class PlaybackDetail(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(7)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.titleLabel = QLabel(f"Title: -")
        self.artistLabel = QLabel(f"Artist: -")
        self.albumLabel = QLabel(f"Album: -")

        font = QFont()
        font.setPointSize(14)

        self.titleLabel.setFont(font)
        self.artistLabel.setFont(font)
        self.albumLabel.setFont(font)


        layout.addWidget(self.titleLabel)
        layout.addWidget(self.artistLabel)
        layout.addWidget(self.albumLabel)

        self.setLayout(layout)

    def update(self, title, artist, album):
        self.titleLabel.setText(title)
        self.artistLabel.setText(artist)
        self.albumLabel.setText(album)


class ProgressBar(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        self.currentLabel = QLabel("--:--")
        self.totalLabel = QLabel("--:--")
        self.progressBar = QSlider(Qt.Orientation.Horizontal)
        self.progressBar.setRange(0, 100)

        layout.addWidget(self.currentLabel)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.totalLabel)

        self.setLayout(layout)
        self.setFixedHeight(30)

class PlaybackControl(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        audio_volume_layout = QHBoxLayout()
        audio_volume_layout.setSpacing(5)
        audio_volume_layout.setContentsMargins(0, 0, 0, 0)
        audio_volume_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        media_button_layout = QHBoxLayout()
        media_button_layout.setSpacing(10)
        media_button_layout.setContentsMargins(0, 0, 0, 0)
        media_button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.button_play_pause = QPushButton()
        self.button_play_pause.setIcon(QIcon("icons/media-playback-start.svg"))
        self.button_play_pause.setFixedSize(50, 50)
        self.button_play_pause.setDisabled(True)

        
        self.button_stop = QPushButton()
        self.button_stop.setIcon(QIcon("icons/media-playback-stop.svg"))
        self.button_stop.setIcon(QIcon("icons/media-playback-stop.svg"))
        self.button_stop.setFixedSize(50, 50)
        self.button_stop.setDisabled(True)

        self.button_mute = QPushButton()
        self.button_mute.setIcon(QIcon("icons/audio-volume-high.svg"))
        self.button_mute.setFixedSize(30, 30)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(100)


        media_button_layout.addWidget(self.button_play_pause)
        media_button_layout.addWidget(self.button_stop)

        audio_volume_layout.addWidget(self.button_mute)
        audio_volume_layout.addWidget(self.volume_slider)

        layout.addLayout(media_button_layout)
        layout.addLayout(audio_volume_layout)

        self.setLayout(layout)
        self.setFixedHeight(50)


class albumCover(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(7)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.imageLabel = QLabel()
        pixmap = QPixmap("placeholder.png")
        pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation) 
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.imageLabel)

        self.setLayout(layout)

    def update(self, image_path):
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation) 
        self.imageLabel.setPixmap(pixmap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setFixedSize(700, 300)
        self.setAcceptDrops(True)


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

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(10, 20, 10, 20)
        playbackLayout = QVBoxLayout()
        playbackControlLayout = QVBoxLayout()


        self.playback_control = PlaybackControl()
        self.playback_control.button_play_pause.clicked.connect(self.play_pause_audio)
        self.playback_control.button_stop.clicked.connect(self.stop_audio)
        self.playback_control.button_mute.clicked.connect(self.mute_audio)
        self.playback_control.volume_slider.sliderMoved.connect(self.set_volume)


        self.album_cover = albumCover()


        self.playback_detail = PlaybackDetail()
        self.progress_bar = ProgressBar()

        mainLayout.addWidget(self.album_cover)
        mainLayout.addSpacing(5)
        mainLayout.addStretch()
        playbackLayout.addWidget(self.playback_detail)
        playbackLayout.addLayout(playbackControlLayout)



        self.progress_bar = ProgressBar()
        playbackControlLayout.addWidget(self.progress_bar)
        playbackControlLayout.addWidget(self.playback_control)
        self.progress_bar.progressBar.sliderMoved.connect(self.position_changed)
        # self.progress_bar.progressBar.valueChanged.connect(self.value_changed)
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)

        mainLayout.addLayout(playbackLayout, 1)


        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

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
                self.album_cover.update(album_cover_path)
                self.playback_detail.update(info_title, info_artist, info_album)
            else:
                self.album_cover.update("placeholder.png")
                self.playback_detail.update(info_title, info_artist, info_album)

            self.playback_control.button_play_pause.setDisabled(False)
            self.playback_control.button_stop.setDisabled(False)
            self.player.play()
            self.playback_control.button_play_pause.setIcon(QIcon("icons/media-playback-pause.svg"))

    def mute_audio(self):
        if self.audio.isMuted():
            print("Unmuting audio")
            self.audio.setMuted(False)
            self.playback_control.button_mute.setIcon(QIcon("icons/audio-volume-high.svg"))
        else:
            print("Muting audio")
            self.audio.setMuted(True)
            self.playback_control.button_mute.setIcon(QIcon("icons/audio-volume-muted.svg"))

    def set_volume(self, position):
        print("Setting volume to", position)
        self.audio.setVolume(position * 0.01)

    def stop_audio(self):
        print("Stopping audio")
        self.player.stop()
        self.playback_control.button_play_pause.setIcon(QIcon("icons/media-playback-start.svg"))
        self.playback_control.button_stop.setDisabled(True)

    def play_pause_audio(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            print("Pausing audio")
            self.player.pause()
            self.playback_control.button_play_pause.setIcon(QIcon("icons/media-playback-start.svg"))
        else:
            if self.current_audio_file:
                print("Playing audio")
                self.player.play()
                self.playback_control.button_play_pause.setIcon(QIcon("icons/media-playback-pause.svg"))
                self.playback_control.button_stop.setDisabled(False)

    def position_changed(self, position):
        if self.progress_bar.progressBar.maximum() != self.player.duration():
            self.progress_bar.progressBar.setMaximum(self.player.duration())

        self.progress_bar.progressBar.setValue(position)
        self.player.setPosition(position)
        
    def duration_changed(self, duration):
        self.progress_bar.progressBar.setRange(0, duration)
    
    def value_changed(self, position):
        self.progress_bar.progressBar.setValue(position)
        self.player.setPosition(position)


    def update_position(self, position):
        self.progress_bar.progressBar.setValue(position)
        self.progress_bar.currentLabel.setText(f"{position // 60000}:{(position // 1000) % 60:02}")

    def update_duration(self, duration):
        self.progress_bar.progressBar.setRange(0, duration)
        self.progress_bar.totalLabel.setText(f"{duration // 60000}:{(duration // 1000) % 60:02}")

    def update_state(self):
        print("State changed")

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
