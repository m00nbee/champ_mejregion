from ultralytics import YOLO
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
import asyncio
from qasync import QApplication, QEventLoop, run
import cv2

from moduleA import MainWindowA
from utils.model import Model
from utils.predict_move import PredictMove

class MainWindowB(MainWindowA):
    def __init__(self):
        super().__init__()
        self.model = Model(self)
        self.camera_timer = QTimer()
        self.camera_timer.start(200)
        self.camera_timer.timeout.connect(self.predict)

        # self.predict_move = PredictMove(self)
    
    def init_ui(self):
        super().init_ui()
        self.ui.camera_button.clicked.connect(self.switch_camera)
        self.ui.detection_button.clicked.connect(self.switch_detect)
        self.ui.choose_model_button.clicked.connect(self.select_model)

    # def neiro_life(self):
    #     ...

    def switch_camera(self):
        self.state.camera = not self.state.camera
        self.log(f"Камера включена: {self.state.camera}")
    
    def switch_detect(self):
        self.state.detect = not self.state.detect
        self.log(f"Детекция включена: {self.state.detect}")

    def select_model(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выберете модель YOLO для детекции объектов", "", "(*.pt)")
        if filename:
            try:
                self.model.set_model(filename)
            except:
                self.log("Ошибка выбора модели")
    
    def predict(self):
        if self.state.detect:
            img, result, state = self.model.predict()
            img = self.model.draw_masks(img, result)
            if state:
                self.log("Распознан человек")
            if img is not None:
                self.ui.camera_label.setPixmap(self.convert_cv_qt(img))
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(400, 300)
        return QPixmap.fromImage(p)


async def main(window: MainWindowB, event: asyncio.Event):
    while not event.is_set():
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = MainWindowB()
    MainWindow.show()
    event = asyncio.Event()
    app.aboutToQuit.connect(event.set)
    run(main(MainWindow, event))