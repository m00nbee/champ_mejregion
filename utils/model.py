from ultralytics import YOLO, solutions
import cv2
import numpy as np

if __name__ == "__main__":
    from moduleB import MainWindowB

class Model:
    def __init__(self, window: "MainWindowB"):
        self.model: YOLO = None
        self.person = YOLO("yolo11n-cls.pt")
        self.capture = cv2.VideoCapture(0)
        self.window = window 
        self.zone = [[50, 50], [450, 500]] # frame_shape надо получить
    
    def predict_person(self, img):
        result = self.person.predict(img, conf=0.5)
        data = result[0]
        state = False 
        if not data.boxes is None:
            for cls in data.boxes.cls:
                if self.window.ui.person_checkbox.isChecked() and int(cls) == 0:
                    state = True
                    self.window.log("Человек в рабочей зоне")
        
        return state 

    def items_to_predict(self):
        classes = []
        if self.window.ui.detect1_checkbox.isChecked():
            classes.append(0)
        if self.window.ui.detect2_checkbox.isChecked():
            classes.append(1)
        if self.window.ui.detect3_checkbox.isChecked():
            classes.append(2)
        return classes
    
    def predict(self):
        _, frame = self.capture.read()
        if self.model is None:
            self.window.state.detect = False
            self.window.log("Выберите модель YOLO сначала")
            return frame, [], False
        if not self.window.state.camera:
            return frame, [], False
        to_predict = self.items_to_predict()

        predict_result = self.model.predict(frame, conf=0.4)[0]
        img = frame.copy()
        state = self.predict_person(img)

        result = []
        masks = predict_result.masks
        boxes = predict_result.boxes
        if not masks is None and not boxes is None and not masks is None:
            for i in range(len(boxes)):
                box = boxes.xyxy[i].cpu().numpy()
                cls_id = int(boxes.cls[i].item())
                conf = float(boxes.conf[i].item())
                x1, x2, y1, y2 = box.astype(int)
                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)
                print(x_center, y_center)

                mask = masks.xy[i]
                if self.zone[0][0] < x_center < self.zone[1][0] and self.zone[0][1] < y_center < self.zone[1][1]:
                    result.append({"mask": mask, "box": box, "cls_id": cls_id, "conf": conf, "xy": [x_center, y_center]})
        

        return img, result, state
    
    def draw_masks(self, img, results):
        overlay = img.copy()
        for result in results:
            mask = result["mask"]
            pts = mask.reshape((-1, 1, 2)).astype(np.int32)
            x1, y1, x2, y2 = result["box"]
            # color = colors[result.cls_id]
            cv2.fillPoly(overlay, [pts], color=(255, 255, 255))
            cv2.putText(img, f"{result['cls_id']} {result['conf']:.2f}", (int(x1), int(y1)), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255))
        
        cv2.addWeighted(overlay, 0.5, img, 0.5, 0, img)
        cv2.rectangle(img, self.zone[0], self.zone[1], (255, 255, 255), thickness=3)

        return img
    
    def set_model(self, model_path):
        try:
            self.model = YOLO(model_path)
            self.window.log(f"Выбрана модель {model_path}")
        except Exception as e:
            self.window.log(f"Ошибка при выборе модели: {e}")
    
        
    
