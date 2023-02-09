import cv2
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
import cereal.messaging as messaging
from cereal.visionipc import VisionIpcClient, VisionStreamType

H = 1208
W = 1928


class Thread(QThread):
  changePixmap = pyqtSignal(QImage)

  def run(self):
    client = VisionIpcClient("webcamguid", VisionStreamType.VISION_STREAM_DRIVER, False)
    client.connect(True)
    sm = messaging.SubMaster(['driverMonitoringState'])

    while True:
      frame = client.recv()
      frame = np.array(frame)

      if frame.any():
        frame = np.reshape(frame, (H, W, 3))

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # get drivermonitoringstate data and draw on image
        sm.update()
        data = sm['driverMonitoringState']

        faceDetected = data.faceDetected
        isDistracted = data.isDistracted
        if faceDetected == True:
          color = (0, 255, 0)
        else:
          color = (255, 0, 0)
        cv2.putText(frame, 'faceDetected: ' + str(faceDetected), (100, 200), cv2.FONT_HERSHEY_PLAIN, 10, color, 10)

        if isDistracted == False and faceDetected == False:
          color = (255, 255, 0)
        elif isDistracted == False:
          color = (0, 255, 0)
        else:
          color = (255, 0, 0)
        cv2.putText(frame, 'isDistracted: ' + str(data.isDistracted), (100, 350), cv2.FONT_HERSHEY_PLAIN, 10, color, 10)

        # update image on display window
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
