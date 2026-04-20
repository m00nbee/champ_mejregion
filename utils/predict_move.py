import cv2
import numpy as np
if __name__ == "__main__":
    from moduleB import MainWindowB

class PredictMove:
    def __init__(self, window: MainWindowB):
        self.window = window
        self.matrix, _ = self.compute_homography() # понять какие координаты на изображении надо
        self.move = False

    def compute_homography(self, image_points, world_points):
        src = np.array(image_points, dtype=np.float32).reshape(-1, 1, 2)
        dst = np.array(world_points, dtype=np.float32).reshape(-1, 1, 2)

        H, _ = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
        return H
    
    def image_to_world(self, image_coord):
        p_world = self.matrix @ image_coord
        return p_world
    
    