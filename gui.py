from time import sleep
import matplotlib.pyplot as plt
from Board import Board
from Tile import Tile
import cv2
import numpy as np
import json
from utils import type_to_name, resources_matrix_to_string
import math


def load_and_resize(image_path, cell_width, cell_height):
    image = cv2.imread(image_path)
    return cv2.resize(image, (cell_width, cell_height))


class Gui:
    SELECTED_COORDINATES = [-1, -1]
    paths_dict = {
        'Car': './VEHICLES/Audi.png',
        'Truck': './VEHICLES/Mini_truck.png',
        'Helicopter': './VEHICLES/helicopter.png',
        'Person': './WALKING ASTRONOUT/',
        'Ground': './TILES/tile_ground.png',
        'BlocksMine': './TILES/tile_blocks_mine.png',
        'Forest': './TILES/tile_forest.png',
        'Field': './TILES/tile_field.png',
        'IronMine': './TILES/tile_iron_mine.png',
        'Water': './TILES/tile_water.png',
        'Road': './TILES/tile_road.png',
        'City': './Settlements/city.png',
        'Village': './Settlements/village.png'}
    HEIGHT_INDEX = 1
    WIDTH_INDEX = 0
    CELL_SIZE = 30
    SUB_CELL_SIZE = 5
    WINDOW_NAME = "BOARD"
    DRAWING = False
    CANVAS = None
    WAIT_KEY = 500
    HAS_REC = False
    HAS_MOVE = False

    def __init__(self, tiles, board):
        self.__selected_resources__ = []
        self.__resources_changed__ = False
        self.__score__ = 0
        self.__tiles = tiles
        self.__board = board
        self.__cell_width = Gui.CELL_SIZE
        self.__cell_height = Gui.CELL_SIZE
        with open('./configuration.json') as f:
            dict = json.load(f)
            self.__cell_width *= dict['Sizes']['Tile'][Gui.WIDTH_INDEX]
            self.__cell_height *= dict['Sizes']['Tile'][Gui.HEIGHT_INDEX]
        rows = len(tiles[0])
        cols = len(tiles)
        self.__canvas_height = rows * self.__cell_height
        self.__canvas_width = cols * self.__cell_width
        self.__canvas = np.zeros((self.__canvas_height, self.__canvas_width, 3), dtype=np.uint8)
        Gui.CANVAS = self.__canvas
        self.draw_background(rows, cols)
        self.__rec_coordinates__ = [-1, -1]
        self.__rec_size__ = [-1, -1]

    def draw_background(self, rows, cols):
        for i in range(rows):
            for j in range(cols):
                image_path = Gui.paths_dict[type_to_name(self.__tiles[i][j].__type__)]
                resized_image = load_and_resize(image_path, self.__cell_width, self.__cell_height)
                y_offset = i * self.__cell_height
                x_offset = j * self.__cell_width
                self.__canvas[y_offset:y_offset + self.__cell_height,
                x_offset:x_offset + self.__cell_width] = resized_image
        Gui.CANVAS = self.__canvas

    def draw_grid(self):
        canvas = Gui.CANVAS.copy()
        # Draw the main grid for the table
        for i in range(len(self.__tiles[0]) + 1):
            cv2.line(canvas, (0, i * self.__cell_height), (self.__canvas_width, i * self.__cell_height),
                     (0, 0, 0), 1)
        for j in range(len(self.__tiles) + 1):
            cv2.line(canvas, (j * self.__cell_width, 0), (j * self.__cell_width, self.__canvas_height), (0, 0, 0),
                     1)
        sub_grid_size = Gui.SUB_CELL_SIZE
        # Draw the sub-grid for each cell
        sub_cell_width = self.__cell_width // sub_grid_size
        sub_cell_height = self.__cell_height // sub_grid_size
        for i in range(len(self.__tiles[0])):
            for j in range(len(self.__tiles)):
                for m in range(1, sub_grid_size):
                    cv2.line(canvas, (j * self.__cell_width, i * self.__cell_height + m * sub_cell_height),
                             ((j + 1) * self.__cell_width, i * self.__cell_height + m * sub_cell_height),
                             (0, 0, 0), 1)
                    cv2.line(canvas, (j * self.__cell_width + m * sub_cell_width, i * self.__cell_height),
                             (j * self.__cell_width + m * sub_cell_width, (i + 1) * self.__cell_height),
                             (0, 0, 0), 1)
        return canvas

    def draw_rectangle(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN and not Gui.HAS_REC:
            Gui.DRAWING = True
            Gui.SELECTED_COORDINATES[Gui.WIDTH_INDEX] = x
            Gui.SELECTED_COORDINATES[Gui.HEIGHT_INDEX] = y
            Gui.SELECTED_COORDINATES = [x, y]
            Gui.WAIT_KEY = 0
        elif event == cv2.EVENT_LBUTTONUP and not Gui.HAS_REC:
            Gui.DRAWING = False
            cv2.rectangle(Gui.CANVAS,
                          (Gui.SELECTED_COORDINATES[Gui.WIDTH_INDEX], Gui.SELECTED_COORDINATES[Gui.HEIGHT_INDEX]),
                          (x, y), (255, 255, 255), -1)

            self.__rec_coordinates__ = [Gui.SELECTED_COORDINATES[Gui.WIDTH_INDEX] // Gui.CELL_SIZE,
                                        Gui.SELECTED_COORDINATES[Gui.HEIGHT_INDEX] // Gui.CELL_SIZE]
            self.__rec_size__ = [(x - Gui.SELECTED_COORDINATES[Gui.WIDTH_INDEX]) // Gui.CELL_SIZE+1,
                                 (y - Gui.SELECTED_COORDINATES[Gui.HEIGHT_INDEX]) // Gui.CELL_SIZE+1]
            Gui.SELECTED_COORDINATES = [x, y]
            Gui.HAS_REC = True

        elif event == cv2.EVENT_LBUTTONUP and Gui.HAS_REC:
            Gui.SELECTED_COORDINATES = [x // Gui.CELL_SIZE, y // Gui.CELL_SIZE]
            Gui.WAIT_KEY = 500
            Gui.HAS_MOVE = True

    def rotate_on_tile(self, image, target_x, target_y):

        # Coordinates of the object's current position (center of the image)
        (h, w) = image.shape[:2]
        object_center_x, object_center_y = w // 2, h // 2

        # Calculate the angle to the target point
        delta_x = target_x - object_center_x
        delta_y = target_y - object_center_y
        angle = math.degrees(math.atan2(delta_y, delta_x))

        # Create the rotation matrix
        M = cv2.getRotationMatrix2D((object_center_x, object_center_y), angle, 1.0)

        # Rotate the image
        rotated_image = cv2.warpAffine(image, M, (w, h))
        return rotated_image

    def draw_on_tile(self, canvas, image_path, x, y, height, width, on_tile):
        """
        Copies an image to a specified location on the canvas.

        Parameters:
        - canvas: The canvas image (numpy array).
        - image_path: The path to the image to be copied.
        - x: The x-coordinate of the top-left corner where the image will be placed.
        - y: The y-coordinate of the top-left corner where the image will be placed.
        """
        # Load the image
        image = load_and_resize(image_path, width * Gui.CELL_SIZE, height * Gui.CELL_SIZE)
        if on_tile and on_tile.__move_toward__ != on_tile.__coordinates__:
            image = self.rotate_on_tile(image, on_tile.__move_toward__[0], on_tile.__move_toward__[1])
        if image is None:
            print(f"Error: Unable to load image at {image_path}")
            return canvas

        # Get the dimensions of the image and canvas
        img_height, img_width, _ = image.shape[:3]
        canvas_height, canvas_width, _ = canvas.shape[:3]

        # Check if the image fits within the canvas at the specified position
        if y + img_height > canvas_height * Gui.CELL_SIZE or x + img_width > canvas_width * Gui.CELL_SIZE:
            print("Error: The image does not fit within the canvas at the specified position.")
            return canvas

        # Copy the image to the canvas
        canvas[y:y + img_height, x:x + img_width] = image

        return canvas

    def show_canvas(self, mouse_event=None):
        canvas = self.draw_grid()
        for element in self.__board.get_structure_elements():
            image_path = Gui.paths_dict[element.__type__]
            width, height = 0, 0
            with open('./configuration.json') as f:
                my_type = element.__type__
                if my_type == "Person":
                    my_type = "People"
                width, height = json.load(f)['Sizes'][my_type]
            x, y = element.__coordinates__
            canvas = self.draw_on_tile(canvas, image_path, (x - 1) * Gui.CELL_SIZE, (y - 1) * Gui.CELL_SIZE,
                                       height, width, None)
        for element in self.__board.get_moveable_elements():
            image_path = Gui.paths_dict[element.__type__]
            width, height = 0, 0
            with open('./configuration.json') as f:
                my_type = element.__type__
                if my_type == "Person":
                    image_path += str(len(element.__steps_left__) % 2 + 9) + '.png'
                    my_type = "People"
                width, height = json.load(f)['Sizes'][my_type]
            x, y = element.__coordinates__
            canvas = self.draw_on_tile(canvas, image_path, (x - 1) * Gui.CELL_SIZE, (y - 1) * Gui.CELL_SIZE,
                                       height, width, element)

        # font
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.rectangle(canvas,
                      (0, 0),
                      (50, 50), (255, 255, 255), -1)
        # org
        org = (10, 30)

        # fontScale
        fontScale = 1

        # Blue color in BGR
        color = (0, 0, 0)

        # Line thickness of 2 px
        thickness = 1

        # Using cv2.putText() method
        canvas = cv2.putText(canvas, str(self.__score__), org, font,
                             fontScale, color, thickness, cv2.LINE_AA)

        if len(self.__selected_resources__) > 0:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.rectangle(canvas,
                          (300, 0),
                          (450, 50), (255, 255, 255), -1)
            # org
            org = (300, 20)

            # fontScale
            fontScale = 1

            # Blue color in BGR
            color = (0, 0, 0)

            # Line thickness of 2 px
            thickness = 1

            # Using cv2.putText() method
            canvas = cv2.putText(canvas, resources_matrix_to_string(self.__selected_resources__), org, font,
                                 fontScale, color, thickness, cv2.LINE_AA)
            self.__resources_changed__ = False
        # Create a named window
        cv2.namedWindow(Gui.WINDOW_NAME)
        cv2.setMouseCallback(Gui.WINDOW_NAME, self.draw_rectangle)
        # Display the canvas in the window
        cv2.imshow(Gui.WINDOW_NAME, canvas)

        # Set the mouse callback function for the window
        # sleep(5)
        cv2.waitKey(Gui.WAIT_KEY)
        cv2.destroyAllWindows()
        return Gui.SELECTED_COORDINATES
