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
        self.zone_mask = self.create_zone() # frame_shape надо получить
    
    def predict_person(self, img):
        result = self.person.predict(img, conf=0.5)
        data = result[0]
        state = False 
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
        if self.model is None:
            self.window.state.camera = False
            self.window.state.detect = False
            self.window.log("Выберите модель YOLO сначала")
        if not self.window.state.camera:
            return
        _, frame = self.capture.read()
        to_predict = self.items_to_predict()

        results = self.model.predict(frame, conf=0.4, classes=to_predict)[0]
        img = frame.copy()
        state = self.predict_person(img)
        

        return img, results, state
    
    def draw_masks(self, img, result, state):
        if not state and self.window.state.detect:
            if result.masks is None:
                return img
            masks = result.masks.data.cpu().numpy()
            boxes = result.boxes.xyxy.cpu().numpy()
            clss = result.boxes.cls.cpu().numpy().astype(int)
            confs = result.boxes.conf.cpu().numpy()
            names = self.model.names

            colors = {
                0: (255, 0, 0),
                1: (0, 255, 0),
                2: (0, 0, 255),
            }
            mask_layer = np.zeros_like(img, dtype=np.uint8)
            for mask, box, cls_id, conf in (zip(masks, boxes, clss, confs)):
                x1, y1, x2, y2 = box.astype(int)

                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)

                if self.zone_mask[x_center, y_center] == 255:
                    color = colors[cls_id]
                    mask_bin = (mask > 0.5).astype(np.uint8)
                    mask_layer[mask_bin == 1] = color
                    cv2.putText(img, f"{names[cls_id]} {conf:.2f}", (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 2)
            final_img = cv2.addWeighted(img, 1, mask_layer, 0.5, 0)
            
            return final_img
        return img
    
    def set_model(self, model_path):
        try:
            self.model = YOLO(model_path)
            self.window.log(f"Выбрана модель {model_path}")
        except Exception as e:
            self.window.log(f"Ошибка при выборе модели: {e}")
    
    def create_zone(self, frame_shape):
        mask = np.zeros(frame_shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [self.zone_coords], 255)
        return mask
    
