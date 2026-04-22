from design import Ui_Dialog
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem
from motion.core import RobotControl
from datetime import datetime
import csv
import json
import asyncio
from qasync import QApplication, QEventLoop, run

from utils.lamp import Lamp
from utils.automatic import Algoritm
from utils.state import State


class MainWindowA(QMainWindow, Ui_Dialog):
    def __init__(self):
        super().__init__()

        self.robot: RobotControl = None
        self.lamp = None
        self.algoritm = Algoritm(self)
        self.stats = {
            "1": [0, None],
            "2": [0, None],
            "3": [0, None],
            "defect": [0, None],
            }
        self.history: list[list] = []
        self.state = State()

        self.init_ui()
    
    def init_ui(self):
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.on_button.clicked.connect(self.on)
        self.ui.off_button.clicked.connect(self.off)
        self.ui.pause_button.clicked.connect(self.pause)
        self.ui.stop_button.clicked.connect(self.stop)
        self.ui.to_initial_button.clicked.connect(self.to_initial_pose)
        
        self.ui.save_log_button.clicked.connect(self.save_log)

        self.ui.class1_button.clicked.connect(lambda x: self.add_point_to_program("1"))
        self.ui.class2_button.clicked.connect(lambda x: self.add_point_to_program("2"))
        self.ui.class3_button.clicked.connect(lambda x: self.add_point_to_program("3"))

        self.ui.remove_last_button.clicked.connect(self.remove_point)
        self.ui.remove_all_button.clicked.connect(self.clear_algoritm)
        self.ui.run_program_button.clicked.connect(self.alg_start)

        self.ui.save_program_button.clicked.connect(self.save_algorimt)
        self.ui.save_cooord_button.clicked.connect(self.save_point)

    def on(self):
        if self.robot is None:
            self.robot = RobotControl()
            self.robot.connect()
            self.log("Подлючение к роботу")
            self.robot.engage()
            self.log("Включение моторов")
            self.lamp = Lamp(self.ui.lamp_label)
            self.lamp.blue()
        else:
            self.robot.engage()
            self.log("Включение моторов")
            self.lamp.blue()
        self.state.stop = False
    
    def off(self):
        if self.robot is None:
            self.log("Подключение к роботу не установлено")
        else:
            self.robot.disengage()
            self.log("Отключение моторов")
            self.lamp.blue()
        self.lamp.clear()

    def to_initial_pose(self):
        self.robot.moveToInitialPose()
        self.log("Возврат на исходную позицию")
        self.lamp.blue()
    
    def save_point(self):
        with open("points.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%x %X')} | {self.robot.getToolPosition()}")
    
    def log(self, msg: str):
        line = f"{datetime.now().strftime('%x %X')} {msg}"
        self.ui.log_list.addItem(line)
        self.ui.log_list.scrollToBottom()
        with open("auto_log.txt", "a", encoding="utf-8") as file:
            file.write(line + "\n")
    
    def stop(self):
        self.robot.stop()
        self.lamp.red()
        self.log("Аварийная остановка системы")
    
    def pause(self):
        self.robot.pause()
        self.lamp.yellow()
        self.log("Пауза")
        
    def save_log(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить логи в файл", self.ui.file_name_editor.toPlainText() + ".txt", "Text files (*.txt)")
        if filename:
            self.log("Сохранение логов")
            try:
                with open(filename, "w", encoding="utf-8") as file:
                    for i in range(self.ui.log_list.count()):
                        file.write(self.ui.log_list.item(i).text() + "\n")
            except:
                self.log("Ошибка сохранения логов в файл")
    
    def alg_start(self):
        self.algoritm.start()
    
    def alg_stop(self):
        self.algoritm.stop()
    
    def clear_algoritm(self):
        self.algoritm.clear()
        self.show_algoritm()
    
    def add_point_to_program(self, obj_name):
        self.algoritm.add(obj_name, self.ui.start_combobox.currentText(), self.ui.end_combobox.currentText())
        self.show_algoritm()
    
    def remove_point(self):
        self.algoritm.remove()
        self.show_algoritm()
    
    def save_algorimt(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить алгоритм в файл", self.ui.session_name_editor.toPlainText() + ".json", "(*.json)")
        if filename:
            self.log("Cохранение программы")
            try:
                with open(filename, "w", encoding='utf-8') as file:
                    json.dump(self.algoritm.save(), file, ensure_ascii=True, indent=4)
            except Exception as e:
                self.log(f"Ошибка сохранения программы: {e}")
    
    def show_algoritm(self):
        self.ui.current_task_list.clear()
        alg = self.algoritm.show()
        self.ui.current_task_list.addItems(alg)
    
    def closeEvent(self, event):  
        self.robot.conveyer_stop()
        self.robot.disengage()
        self.lamp.clear()
        print("Закрытие окна приложения")  
        event.accept()  

async def main(win: MainWindowA, event: asyncio.Event):
    while not event.is_set():
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = MainWindowA()
    MainWindow.show()
    event = asyncio.Event()
    app.aboutToQuit.connect(event.set)
    run(main(MainWindow, event))