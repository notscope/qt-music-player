from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

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