from PyQt6.QtWidgets import QSlider
from PyQt6.QtCore import Qt

class CustomSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.scroll_enabled = True

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            value = self.minimum() + (self.maximum() - self.minimum()) * event.position().x() / self.width()
            self.setValue(int(value))
            self.sliderMoved.emit(int(value))
            event.accept()
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        if self.scroll_enabled:
            super().wheelEvent(event)
        else:
            event.ignore()

    def setScrollEnabled(self, enabled):
        self.scroll_enabled = enabled