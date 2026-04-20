from motion.core import LedLamp
import asyncio
from PyQt5.QtWidgets import QLabel

class Lamp(LedLamp):
    def __init__(self, lamp_label: QLabel, ip='192.168.2.101', port=8890):
        super().__init__(ip, port)
        self.lamp_label = lamp_label
    
    def _set(self, color, command="0000"):
        self.lamp_label.setStyleSheet(f"background-color: {color}")
        self.task = asyncio.create_task(asyncio.to_thread(self.setLamp, command))
    
    def red(self):
        self._set("red", "0001")
    
    def yellow(self):
        self._set("yellow", "0010")
    
    def green(self):
        self._set("green", "0100")
    
    def blue(self):
        self._set("blue", "1000")
    
    def clear(self):
        self._set("white")
    
    
