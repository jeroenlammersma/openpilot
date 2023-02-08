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

class Thread(QThread):
    rk = Ratekeeper(10)
    changePixmap = pyqtSignal(QImage)

    def run(self):
        self.client = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_DRIVER, False)
        self.client.connect(True)

        print(self.client.is_connected())

        while frame := self.client.recv():
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_YUV420p2RGB)

            if frame != None:
                print('asdfasdfasdfasdf')

            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)
            self.rk.keep_time()
        


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

    app.exit(app.exec_())
