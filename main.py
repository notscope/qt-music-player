import sys
import os
import hashlib
import tempfile

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QIcon, QAction, QDragEnterEvent, QDropEvent, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog

from components.about_dialog import AboutDialog
from components.slider import CustomSlider

ICON_PLAYBACK_START = "icons/media-playback-start.svg"
ICON_PLAYBACK_STOP = "icons/media-playback-stop.svg"
ICON_PLAYBACK_PAUSE = "icons/media-playback-pause.svg"
ICON_VOLUME_HIGH = "icons/audio-volume-high.svg"
ICON_VOLUME_MUTE = "icons/audio-volume-muted.svg"


class PlaybackDetail(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(7)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Configure font
        font = QFont()
        font.setPointSize(14)

        self.titleLabel = QLabel(f"Title: -")
        self.artistLabel = QLabel(f"Artist: -")
        self.albumLabel = QLabel(f"Album: -")

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
        self.playbackSlider = CustomSlider(Qt.Orientation.Horizontal)
        self.playbackSlider.setRange(0, 100)
        self.playbackSlider.setDisabled(True)

        layout.addWidget(self.currentLabel)
        layout.addWidget(self.playbackSlider)
        layout.addWidget(self.totalLabel)

        self.setLayout(layout)
        self.setFixedHeight(30)

class PlaybackControl(QWidget):
    def __init__(self):
        super().__init__()

        # Layout
        layout = QHBoxLayout()
        audio_volume_layout = QHBoxLayout()
        media_button_layout = QHBoxLayout()

        # Button
        self.button_play_pause = QPushButton()
        self.button_stop = QPushButton()
        self.button_mute = QPushButton()

        layout.setSpacing(5)
        audio_volume_layout.setSpacing(5)
        media_button_layout.setSpacing(10)

        layout.setContentsMargins(0, 0, 0, 0)
        audio_volume_layout.setContentsMargins(0, 0, 0, 0)
        media_button_layout.setContentsMargins(0, 0, 0, 0)

        audio_volume_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        media_button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.button_play_pause.setIcon(QIcon(ICON_PLAYBACK_START))
        self.button_stop.setIcon(QIcon(ICON_PLAYBACK_STOP))
        self.button_mute.setIcon(QIcon(ICON_VOLUME_HIGH))

        self.button_play_pause.setFixedSize(50, 50)
        self.button_stop.setFixedSize(50, 50)
        self.button_mute.setFixedSize(30, 30)

        self.button_play_pause.setDisabled(True)
        self.button_stop.setDisabled(True)

        self.volume_slider = CustomSlider(Qt.Orientation.Horizontal)
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
        # set window options
        self.setWindowTitle("My App")
        self.setFixedSize(700, 300)
        self.setAcceptDrops(True)

        # Initialize audio and player
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)

        # Initialize widgets
        self.progress_bar = ProgressBar()
        self.album_cover = albumCover()
        self.playback_detail = PlaybackDetail()
        self.playback_control = PlaybackControl()

        # Initialize layouts
        mainLayout = QHBoxLayout()
        playbackLayout = QVBoxLayout()
        playbackControlLayout = QVBoxLayout()

        self.current_audio_file = None
        self.temp_files = []

        # Setup menu bar and actions
        self.setup_menu_bar()

        # Setup layout
        mainLayout.setContentsMargins(10, 20, 10, 20)
        self.playback_control.button_play_pause.clicked.connect(self.play_pause_audio)
        self.playback_control.button_stop.clicked.connect(self.stop_audio)
        self.playback_control.button_mute.clicked.connect(self.mute_audio)
        self.playback_control.volume_slider.valueChanged.connect(self.set_volume)

        mainLayout.addWidget(self.album_cover)
        mainLayout.addSpacing(5)
        mainLayout.addStretch()
        playbackLayout.addWidget(self.playback_detail)
        playbackLayout.addLayout(playbackControlLayout)

        self.progress_bar.playbackSlider.setScrollEnabled(False)
        playbackControlLayout.addWidget(self.progress_bar)
        playbackControlLayout.addWidget(self.playback_control)
        self.progress_bar.playbackSlider.sliderMoved.connect(self.change_position)
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)

        mainLayout.addLayout(playbackLayout, 1)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

    def setup_menu_bar(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        help_menu = menu.addMenu("&Help")

        button_open = QAction("&Open", self)
        button_open.setStatusTip("Open a file")
        button_open.triggered.connect(self.load_audio)
        file_menu.addAction(button_open)

        file_menu.addSeparator()

        button_quit = QAction("&Quit", self)
        button_quit.setStatusTip("Quit the application")
        button_quit.triggered.connect(self.close)
        file_menu.addAction(button_quit)

        button_about = QAction("&About", self)
        button_about.setStatusTip("About")
        button_about.triggered.connect(self.show_about_dialog)
        help_menu.addAction(button_about)
    
    def show_about_dialog(self):
        dialog = AboutDialog()
        dialog.exec()
    
    def fetch_audio_info(self, file_name):
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


    def load_audio(self, file_name=None):
        if not file_name:
            # wav and ogg is not supported yet
            # file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.mp3 *.wav *.ogg)")
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.mp3)")
        if file_name:
            self.current_audio_file = file_name
            self.player.setSource(QUrl.fromLocalFile(file_name))
            print("Loading", file_name)
            self.fetch_audio_info(file_name)
            # audio = MP3(file_name, ID3=EasyID3)
            # info_title = audio.get("title", ["Unknown"])[0]
            # info_artist = audio.get("artist", ["Unknown"])[0]
            # info_album = audio.get("album", ["Unknown"])[0]
            # info_genre = audio.get("genre", ["Unknown"])[0]

            # audio = MP3(file_name, ID3=ID3)
            # album_cover_path = None

            # for tag in audio.tags.values():
            #     if isinstance(tag, APIC):
            #         cover_hash = hashlib.md5(tag.data).hexdigest()
            #         temp_dir = tempfile.gettempdir()
            #         album_cover_path = os.path.join(temp_dir, f"{cover_hash}.jpg")

            #         if not os.path.exists(album_cover_path):
            #             with open(album_cover_path, 'wb') as img:
            #                 img.write(tag.data)
            #             self.temp_files.append(album_cover_path)
            #             print(self.temp_files)
            #             print("Created new album cover:", album_cover_path)
            #         else:
            #             print("Using existing album cover:", album_cover_path)
            #         break
            
            # print(album_cover_path)
            # if album_cover_path:
            #     self.album_cover.update(album_cover_path)
            #     self.playback_detail.update(info_title, info_artist, info_album)
            # else:
            #     self.album_cover.update("placeholder.png")
            #     self.playback_detail.update(info_title, info_artist, info_album)


            self.playback_control.button_play_pause.setDisabled(False)
            self.playback_control.button_stop.setDisabled(False)
            self.progress_bar.playbackSlider.setDisabled(False)
            self.player.play()
            self.playback_control.button_play_pause.setIcon(QIcon(ICON_PLAYBACK_PAUSE))

    def mute_audio(self):
        if self.audio.isMuted():
            print("Unmuting audio")
            self.audio.setMuted(False)
            self.playback_control.button_mute.setIcon(QIcon(ICON_VOLUME_HIGH))
        else:
            print("Muting audio")
            self.audio.setMuted(True)
            self.playback_control.button_mute.setIcon(QIcon(ICON_VOLUME_MUTE))

    def set_volume(self, position):
        print("Setting volume to", position)
        self.audio.setVolume(position * 0.01)

    def stop_audio(self):
        print("Stopping audio")
        self.player.stop()
        self.playback_control.button_play_pause.setIcon(QIcon(ICON_PLAYBACK_START))
        self.playback_control.button_stop.setDisabled(True)

    def change_position(self, value):
        print("Position changed to", value)
        self.player.setPosition(value * 1000)


    def play_pause_audio(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            print("Pausing audio")
            self.player.pause()
            self.playback_control.button_play_pause.setIcon(QIcon(ICON_PLAYBACK_START))
        else:
            if self.current_audio_file:
                print("Playing audio")
                self.player.play()
                self.playback_control.button_play_pause.setIcon(QIcon(ICON_PLAYBACK_PAUSE))
                self.playback_control.button_stop.setDisabled(False)
        
    def duration_changed(self, duration):
        print("Duration changed to", duration)
        self.progress_bar.playbackSlider.setRange(0, duration)

    def update_position(self, position):
        # print("Position set to ", position)
        self.progress_bar.playbackSlider.setValue((position // 1000))
        self.progress_bar.currentLabel.setText(f"{position // 60000}:{(position // 1000) % 60:02}")

    def update_duration(self, duration):
        print("music duration is", duration // 1000)
        self.progress_bar.playbackSlider.setRange(0, (duration // 1000))
        self.progress_bar.totalLabel.setText(f"{duration // 60000}:{(duration // 1000) % 60:02}")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_name = url.toLocalFile()
            # wav and ogg is not supported yet
            # if file_name.lower().endswith(('.mp3', '.wav', '.ogg')):
            if file_name.lower().endswith(('.mp3')):
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
