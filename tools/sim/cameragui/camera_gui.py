import cv2
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QSizePolicy
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
import cereal.messaging as messaging
from cereal.visionipc import VisionIpcClient, VisionStreamType

H = 1208
W = 1928


class Thread(QThread):
  changePixmap = pyqtSignal(QImage)
  client = None
  sm = None

  def run(self):
    self.init_connections()
    self.client.connect(True)

    while True:
      frame = self.get_frame()
      faceDetected, isDistracted = self.get_drivermonitoring_state()
      self.draw_text(faceDetected, isDistracted, frame)
      pixMap = self.convert_frame_to_pixmap(frame)
      self.changePixmap.emit(pixMap)

  def init_connections(self):
    self.client = VisionIpcClient("webcamguid", VisionStreamType.VISION_STREAM_DRIVER, False)
    self.sm = messaging.SubMaster(['driverMonitoringState'])
  def get_frame(self):
    frame = self.client.recv()
    frame = np.array(frame)

    if frame.any():
      frame = np.reshape(frame, (H, W, 3))
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      return frame

  def get_drivermonitoring_state(self):
    self.sm.update()
    data = self.sm['driverMonitoringState']
    faceDetected = data.faceDetected
    isDistracted = data.isDistracted
    return faceDetected, isDistracted

  def draw_text(self, faceDetected, isDistracted, frame):
    if faceDetected == True:
      color = (0, 255, 0)
    else:
      color = (255, 0, 0)
    cv2.putText(frame, 'faceDetected: ' + str(faceDetected), (50, 150), cv2.FONT_HERSHEY_PLAIN, 5, color, 5)

    if isDistracted == False and faceDetected == False:
      color = (255, 255, 0)
    elif isDistracted == False:
      color = (0, 255, 0)
    else:
      color = (255, 0, 0)
    cv2.putText(frame, 'isDistracted: ' + str(isDistracted), (60, 225), cv2.FONT_HERSHEY_PLAIN, 5, color, 5)

  def convert_frame_to_pixmap(self, frame):
    bytesPerLine = W * 3

    convertToQtFormat = QImage(frame.data, W, H, bytesPerLine, QImage.Format_RGB888)

    pixMap = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
    return pixMap


class CameraWidget(QWidget):
  def __init__(self):
    super().__init__()
    self.label = QLabel(self)
    self.label.resize(640, 480)
    self.label.setScaledContents(True)
    self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.pixmap = None
    th = Thread(self)
    th.changePixmap.connect(self.set_image)
    th.start()

  @pyqtSlot(QImage)
  def set_image(self, image):
    self.pixmap = QPixmap.fromImage(image)
    self.label.setPixmap(self.pixmap)

  def resizeEvent(self, event):
    if self.pixmap is not None:
      pixmap1 = self.pixmap
      self.pixmap = pixmap1.scaled(self.width(), self.height())
      self.label.setPixmap(self.pixmap)
      self.label.resize(self.width(), self.height())


if __name__ == "__main__":
  app = QApplication(sys.argv)

  widget = CameraWidget()

  widget.show()

  app.exit(app.exec_())
