from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5 import QtGui
import threading, time

class gui:
    def __init__(self):
        app = QApplication([])
        self.label = QLabel('Hello World!')
        self.label.setPixmap(QtGui.QPixmap("C:/Users/Joost-Laptop/Pictures/bean.jpg"))
        self.label.resize(800,600)

        t1 = threading.Thread(target=self.changeimage)
        t1.start()

        self.label.show()
        app.exec()

    def changeimage(self):
        while True:
            self.label.setPixmap(QtGui.QPixmap("C:/Users/Joost-Laptop/Pictures/bean.jpg"))
            print("swapped")
            time.sleep(1)
            self.label.setPixmap(QtGui.QPixmap("C:/Users/Joost-Laptop/Pictures/bean2.jpg"))
            print("swapped")
            time.sleep(1)



if __name__ == "__main__":
    gui = gui()
