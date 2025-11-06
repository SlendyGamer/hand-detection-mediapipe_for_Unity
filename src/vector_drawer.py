import cv2

class VectorDrawer:
    def draw_vector(self, image, coord1, coord2, color=(0, 255, 0), thickness=2):
        # Draw the connection points on the image
        start_point = (int(coord1.x * image.shape[1]), int(coord1.y * image.shape[0]))
        end_point = (int(coord2.x * image.shape[1]), int(coord2.y * image.shape[0]))
        cv2.line(image, start_point, end_point, color, thickness)