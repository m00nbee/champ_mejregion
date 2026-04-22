import asyncio
from pydantic import BaseModel
from motion.core import Waypoint, InterpreterStates, Modes
import time 
from datetime import datetime 
from enum import Enum
if __name__ == "__main__":
    from moduleA import MainWindowA

class Palette:
    cells = [[False] * 3] * 3
    
class OneAction(BaseModel):
    name: str
    actions: list[list|str]
    obj_name: str 
    start: str 
    end: str
    def dump(self):
        return {
            "name": self.name,
            "obj_name": self.obj_name,
            "start": self.start,
            "end": self.end,
            "actions": [act for act in self.actions],
        }

class Coordinates(Enum):
    UPPER_TAKE_POSITION = []
    UPPER_TARGET_POSITION = []
    NEXT_ACTION_POSITION = []

    TAKE_POSITION_1 = []
    TAKE_POSITION_2 = []
    TAKE_POSITION_3 = []
    TAKE_POSITION_4 = []
    TAKE_POSITION_5 = []
    TAKE_POSITION_6 = []
    TAKE_POSITION_7 = []
    TAKE_POSITION_8 = []
    TAKE_POSITION_9 = []

    TARGET_POSITION_1 = []
    TARGET_POSITION_2 = []
    TARGET_POSITION_3 = []
    TARGET_POSITION_4 = []
    TARGET_POSITION_5 = []
    TARGET_POSITION_6 = []
    TARGET_POSITION_7 = []
    TARGET_POSITION_8 = []
    TARGET_POSITION_9 = []
    
    GRIPPER_ON = "self.window.robot.addToolState(1)"
    GRIPPER_OFF = "self.window.robot.addToolState(0)"

    
class Algoritm:
    def __init__(self, window: "MainWindowA"):
        self.window = window 
        self.algoritm: list[OneAction] = []
        self.task = None
        self.palette = Palette 
    
    def save(self):
        return [action.dump() for action in self.algoritm]
    
    def add(self, obj_name, start, end):
        self.algoritm.append(
            OneAction(
                name = f"Объект {obj_name} из ячейки {start} в ячейку {end}",
                actions = [
                    Coordinates.UPPER_TAKE_POSITION.value,
                    getattr(Coordinates, f"TAKE_POSITION_{start}").value,
                    Coordinates.GRIPPER_ON.value,
                    Coordinates.UPPER_TARGET_POSITION.value,
                    getattr(Coordinates, f"TARGET_POSITION_{end}").value,
                    Coordinates.GRIPPER_OFF.value,
                    Coordinates.NEXT_ACTION_POSITION.value
                ],
                obj_name=obj_name,
                start=start,
                end=end
            )
        )
        
    def remove(self):
        try:
            self.algoritm.pop()
        except:
            ...
    
    def clear(self):
        self.algoritm.clear()
        self.window.ui.full_cell_label.setStyleSheet("background-color: white")
        self.palette.cells = [[False] * 3] * 3

    
    def task_(self, alg: OneAction):
        self.window.log(f"Робот принял задачу {alg.name}")
        result = True
        if self.palette.cells[(int(alg.end) - 1) // 2][(int(alg.end) - 1) % 2]:
            return False
        for action in alg.actions:
            if isinstance(action, str):
                eval(action)
            else:
                self.window.robot.addMoveToPointL([Waypoint(action)])
        
        if alg.name.startswith("Объект"):
            result = int(alg.name[-1])
        
        # self.window.log(f"Начало выполнения действия: {alg.name}")
        return result
    
    def start(self, clear=False):
        self.window.state.pause = False 
        if self.task is None:
            self.clear_alg = clear 
            self.task = asyncio.create_task(self.runner())
    
    def stop(self):
        if not self.task is None:
            self.task.cancel()
    
    def wait(self):
        target = time.time()
        while (not self.task is None and not self.window.robot.getRobotMode() is InterpreterStates.PROGRAM_IS_DONE.value):
            sc = time.time()
            if (sc - target) < 5:
                break
            
            if self.window.robot.getRobotMode() is Modes.MOVE_TO_START_M.value and self.window.robot.getRobotMode() is InterpreterStates.MOTION_NOT_ALLOWED_S.value:
                self.window.robot.activateMoveToStart()
            else:
                self.window.robot.play()
            
            print("в wait")
            time.sleep(0.1)
    
    async def runner(self):
        try:
            self.window.lamp.green()
            # if not self.window.robot.engage():
            #     return
            self.window.robot.reset()
            if len(self.algoritm) != 0:
                self.window.log("Начало выполнения программы")
                for action in self.algoritm:
                    await asyncio.sleep(.4)
                    while self.window.state.pause:
                        await asyncio.sleep(0.5)

                    result = await asyncio.to_thread(self.task_, action)
                    if result == False:
                        self.window.log(f"Попытка перемещения двух объектов в одну ячейку")
                        self.window.ui.full_cell_label.setStyleSheet("background-color: yellow")
                        break 
                    elif result == True:
                        pass
                    self.window.robot.play()
                    await asyncio.sleep(0.5)
                    self.window.robot.activateMoveToStart()
                    await asyncio.sleep(0.5)
                    self.window.robot.moveToInitialPose()
                    await asyncio.sleep(0.5)
                    self.window.robot.activateMoveToStart()
                    await asyncio.sleep(0.5)
                    self.window.log(f"Текущая позиция робота: {self.window.robot.getToolPosition()}")
                    await asyncio.to_thread(self.wait)
            
        except asyncio.CancelledError:
            self.window.log("Остановка программы")

        except Exception as e:
            self.window.log(f"Ошибка выполнения программы: {e}")
        
        finally:
            self.task = None 
            try:
                await asyncio.sleep(0.1)
                self.window.log("Робот закончил выполнение программы")
                self.window.lamp.blue()
                self.window.robot.reset()
            
            except:
                ...

            if self.clear_alg:
                self.clear()
                self.clear_alg = False
    
    def show(self):
        return [
            task.name for task in self.algoritm
        ]
