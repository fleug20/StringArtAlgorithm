import numpy as np
import math
import cv2
from PIL import Image, ImageOps, ImageDraw
import time


class StringArtGenerator:
    def __init__(self):
        # image variables
        self.nailcount = 250
        self.iterations = 10
        self.count = 0
        self.nails_to_skip = 10
        self.line_thickness = 1
        self.size = None
        self.inverted = False
        # data
        self.npInput_image = None
        self.npImage = None
        self.nail_pos = None
        self.string_paths = None
        # property's
        self._line_color = 0

    @property
    def line_color(self):
        return self._line_color

    @line_color.setter
    def line_color(self, value):
        color = np.clip(int(value), 0, 255)
        self._line_color = color

    # returns a time estimation in seconds
    def getTimeEstimation(self):
        start = time.process_time()
        self.calculateDarkestPath(0)
        time_passed = time.process_time() - start
        time_estimation = math.ceil(time_passed * (self.iterations) + 0.1 * time_passed)

        return time_estimation

    # stores nail coordinates into np array
    def calculateNailPositions(self):
        radius = self.size / 2
        nailcount = self.nailcount
        angles = np.linspace(0, 2 * np.pi, nailcount, endpoint=False)

        x = radius + radius * np.cos(angles)
        y = radius + radius * np.sin(angles)

        positions = np.column_stack((x, y))
        positions = np.round(positions).astype(np.int16)

        self.nail_pos = positions

    # prepares input image and stores needed data
    def loadImage(self, path):
        try:
            input_image = Image.open(path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file {path} not found.")
        except Exception as e:
            raise Exception(f"An error occurred while loading the image: {str(e)}")

        input_image = Image.open(path)
        self.npImage = self.getNpImage(input_image, self.inverted)
        self.npInput_image = self.npImage.copy()
        self.size = self.npImage.shape[0]
        self.prepareStringPathArray()


    # preallocates space for string_paths
    def prepareStringPathArray(self):
        dt = np.dtype(
            [
                ("start_pos", np.int16, (2,)),
                ("start_index", np.uint16),
                ("end_pos", np.int16, (2,)),
                ("end_index", np.int16),
            ]
        )
        self.string_paths = np.empty((self.iterations), dtype=dt)

    # adds a path to string_paths. These are the final values that will get plotted and stored in __main__.py
    def addPathToOutput(self, start, start_index, end, end_index):
        self.string_paths[self.count] = (start, start_index, end, end_index)

    # returns a 2-dimensional np array mask
    def getLineMask(self, start, end):
        pixels = self.bresenham_line(*start, *end)
        mask = np.full((self.size, self.size), False)
        mask[pixels[:, 1], pixels[:, 0]] = True
        return mask

    # returns a 2-dimensional np array mask for a thickness greater than 1. The use of cv2 results in longer calculation time
    def getLineMaskWithThickness(self, start, end):
        line = cv2.line(
            self.getEmptyCanvas(self.size),
            start,
            end,
            (self._line_color, 255),
            thickness=self.line_thickness,
        )
        mask = (line[:, :, 0] == self._line_color) & (line[:, :, 1] > 0)
        return mask

    # returns the average brightness below a line as float. A higher value equals a brighter path
    def getBrightness(self, mask):
        brightness = np.mean(self.npImage[mask, 0])
        return brightness

    # sets the brigness values of the given mask to 255
    def removePathFromImage(self, mask):
        self.npImage[mask, 0] = 255

    # calculates all paths and returns data for the optimal path
    def calculateDarkestPath(self, start_index):
        darkest_value = float("inf")
        darkest_index = -1
        darkest_mask = np.empty((self.size, self.size))
        nail = self.nail_pos[start_index]

        index = (start_index + self.nails_to_skip) % self.nailcount
        end = (start_index - self.nails_to_skip) % self.nailcount

        while index != end:
            if self.line_thickness > 1:
                mask = self.getLineMaskWithThickness(nail, self.nail_pos[index])
            else:
                mask = self.getLineMask(nail, self.nail_pos[index])
            brightness = self.getBrightness(mask)
            
            if brightness < darkest_value:
                darkest_value = brightness
                darkest_index = index
                darkest_mask = mask
            index = (index + 1) % self.nailcount

        return nail, self.nail_pos[darkest_index], darkest_index, darkest_mask

    # main function for generating the string art. Call this function after setting all variables
    def generate(self):
        while self.count < self.iterations:
            start_index = self.count % self.nailcount
            start, end, end_index, mask = self.calculateDarkestPath(start_index)

            self.addPathToOutput(start, start_index, end, end_index)
            self.removePathFromImage(mask)

            print(f"{self.iterations - self.count} iterations left")
            self.count += 1

    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end (x,y) points
    """

    def bresenham_line(self, x0, y0, x1, y1):
        points = []
        is_steep = abs(y1 - y0) > abs(x1 - x0)
        if is_steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        is_reversed = False
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
            is_reversed = True

        dx = x1 - x0
        dy = abs(y1 - y0)

        error = int(dx / 2.0)
        y = y0
        ydir = None
        if y0 < y1:
            ydir = 1
        else:
            ydir = -1

        for x in range(x0, x1 + 1):
            if is_steep:
                points.append((y, x))
            else:
                points.append((x, y))
            error -= dy
            if error < 0:
                y += ydir
                error += dx

        if is_reversed:
            points.reverse()

        npPixels = np.array(points)
        valid = ~np.any(npPixels >= self.size, axis=1)
        return npPixels[valid]

    """
    helper-functions
    """

    # Create same size alpha layer with circle
    @staticmethod
    def getEmptyCanvas(size, color=255):
        npImage = np.ones((size, size, 1), dtype=np.uint8) * color

        alpha = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([0, 0, size, size], 0, 360, fill=255)

        # Convert alpha Image to numpy array and apply alpha
        npAlpha = np.array(alpha)
        npImage = np.dstack((npImage, npAlpha))
        StringArtGenerator.setColorOfTransparentPixels(npImage, color=0)

        return npImage

    # sets all transparent pixels to the given color value
    @staticmethod
    def setColorOfTransparentPixels(npImage, color=0):
        npImage[npImage[:, :, 1] == 0] = np.array([color, 0])

    # returns a circular grayscale image as NP array
    @staticmethod
    def getNpImage(image, inverted):
        image = ImageOps.grayscale(image)

        # make a square image
        width, height = image.size
        print(f"Image dimensions: {width}, {height}")
        if width > height:
            left = int(width / 2 - height / 2)
            upper = 0
            right = int(height + (width / 2 - height / 2))
            lower = height

            image = image.crop((left, upper, right, lower))
            width = height
        elif width < height:
            left = 0
            upper = int(height / 2 - width / 2)
            right = width
            lower = width + int(height / 2 - width / 2)

            image = image.crop((left, upper, right, lower))
            height = width
        else:
            pass

        if inverted:
            image = ImageOps.invert(image)

        npImage = np.array(image)
        print("Image shape:", npImage.shape)

        # Create same size alpha layer with circle
        alpha = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([0, 0, height, width], 0, 360, fill=255)

        # Convert alpha Image to numpy array and apply alpha
        npAlpha = np.array(alpha)
        npImage = np.dstack((npImage, npAlpha))
        StringArtGenerator.setColorOfTransparentPixels(npImage, color=0)

        return npImage
