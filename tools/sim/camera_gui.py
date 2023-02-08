#




#The problem is that the function that obtains the image is executed only once and not updating the label.
#The correct way is to place it inside a loop, but it will result in blocking the main window. This blocking of main window can be solved by using the QThread class and send through a signal QImage to update the label. For example:

import cv2
import sys
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import numpy as np

from common.realtime import Ratekeeper

from cereal.visionipc import VisionIpcClient, VisionStreamType

H = 1208
W = 1928

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        self.client = VisionIpcClient("webcamguid", VisionStreamType.VISION_STREAM_DRIVER, False)
        self.client.connect(True)

        while True:
            frame = self.client.recv()
            frame = np.array(frame)

            if frame.any():
                frame = np.reshape(frame, (H, W, 3))

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                bytesPerLine = W * 3

                convertToQtFormat = QImage(frame.data, W, H, bytesPerLine, QImage.Format_RGB888)

                pixMap = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(pixMap)
        


class CameraWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel(self)
        self.label.resize(640, 480)
        th = Thread(self)
        th.changePixmap.connect(self.set_image)
        th.start()

    @pyqtSlot(QImage)
    def set_image(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = CameraWidget()

    widget.show()

    app.exit(app.exec_())
