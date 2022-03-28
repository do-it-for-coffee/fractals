import math
import numpy as np
import random
import os
from PIL import Image
import pyttsx3

class TopError(Exception):
    pass

class OddResolutionError(Exception):
    pass

class Fractal:


    '''
    Makes images of the Mandelbrot set given a center coordinate and the
    imaginary coordinate of the top row of pixels.
    '''


    # If the image directory doesn't exist, create it.
    IMAGE_DIR = os.path.dirname(os.path.realpath(__file__))
    IMAGE_DIR = os.path.join(IMAGE_DIR, 'PNG')
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
    # String for image progress.
    P_STRING = 'Your {cr}+{ci}i image is {p} percent complete.'


    def __init__(self):

        '''
        Initiate the TTS engine. These take a while to render, so I found, for
        while I wait, to hear the progress of the image helped.
        '''

        self.tts = pyttsx3.init()

    def mandelbrot(self, image_size, colors, center=None, top=1.6,
                   magnification=1, divergence_iterations=1600, speak=True):

        # Speech toggle.
        self.SPEAK = speak

        # Since the resolution of the image is divided by two, an even number is
        # required.
        if image_size[0]%2 == 1 or image_size[1]%2 == 1:
            raise OddResolutionError

        # This center with the default top place the whole Mandelbrot
        # visualisation centered in the image.
        if center is None:
            center = (-0.66, 0)

        # If the center of the image is set to the same value as the top of the
        # image, raise an error.
        if center[1] >= top:
            raise TopError

        '''
        Magnification is how many subpixels each pixel is divided into. This
        defines the brightness of the pixel. Divergence iterations define how
        many iterations the code executes until saying whether a coordinate
        diverges or not. Divergence levels are gradations of color for those
        coordinates who do end up diverging from the set.
        '''

        self.MAGNIFICATION = magnification
        self.DIVERGENCE_ITERATIONS = divergence_iterations
        self.DIVERGENCE_LEVELS = [self.DIVERGENCE_ITERATIONS//x for x in \
                                  reversed(range(1, 256))]

        for key, value in colors.items():
            colors[key] = np.array(value).reshape(1, 3)

        # Initiate a few variables for the image.
        self.IMAGE_SIZE = image_size
        self.CENTER = center
        self.TOP = top
        self.CENTER_PIXEL = (int(self.IMAGE_SIZE[0] / 2),
                             int(self.IMAGE_SIZE[1] / 2))

        image_array = np.zeros((self.IMAGE_SIZE[1], self.IMAGE_SIZE[0], 3),
                                dtype=np.uint8)

        # Variables for percent complete.
        i = 0
        p_complete = 0

        print(self.P_STRING.format(cr=self.CENTER[0],
                                   ci=self.CENTER[1],
                                   p=p_complete))

        if self.SPEAK:

            self.tts.say(self.P_STRING.format(cr=self.CENTER[0],
                                              ci=self.CENTER[1],
                                              p=p_complete))
            self.tts.runAndWait()

        '''
        Test each pixel of the image for divergence or inclusion in the
        Mandelbrot set.
        '''

        for pixel_y in range(self.IMAGE_SIZE[1]):

            for pixel_x in range(self.IMAGE_SIZE[0]):

                # Count for subpixels.
                tally = {'mandelbrot': 0,
                         'divergence': 0}

                # Reflects how many iterations a divergent coordinate hangs on.
                divergence_multipliers = []

                for magnification in range(1, self.MAGNIFICATION+1):
                    # Subpixel float values.
                    x = pixel_x + magnification/self.MAGNIFICATION
                    y = pixel_y + magnification/self.MAGNIFICATION

                    # Find the coordinates for a subpixel.
                    real, imaginary = self.pixels_to_coordinates(x, y)

                    # "Good" is defined as not already diverged from the circle
                    # of radius 2 that contains the Mandelbrot set so as to not
                    # spend time calculating what is already known.
                    if self.coordinates_good(real, imaginary):

                        # Iterate the equation to test for divergence.
                        c = real + imaginary * 1j
                        z = None
                        diverges = False

                        for d_i in range(self.DIVERGENCE_ITERATIONS):

                            z = self.next_mandelbrot(z, c)

                            if not self.coordinates_good(z.real, z.imag):

                                # Count for divergence.
                                tally['divergence'] += 1


                                # The divergence multiplier determines the
                                # brightness of a pixel in the image. If the
                                # divergent coordinate hangs on for more
                                # iterations, it gets a brighter color.
                                d_min = min([x for x in self.DIVERGENCE_LEVELS if d_i+1 <= x])
                                divergence_multiplier = self.DIVERGENCE_LEVELS.index(d_min)
                                divergence_multipliers.append(divergence_multiplier)

                                diverges = True
                                break

                        if not diverges:
                            # Count for the Mandelbrot set.
                            tally['mandelbrot'] += 1

                    else:
                        tally['divergence'] += 1
                        divergence_multipliers.append(0)

                '''
                Make a NumPy array with one of each color value for each tally.
                If there are 3 subpixels in the Mandelbrot set and 1 subpixel
                divergent, then the array has three RGB values of the Mandelbrot
                color and one RGB value for divergent subpixels. The divergent
                subpixel RGB value is brighter if the subpixel remained in the
                circle for more iterations. The average of these RGB values is
                what determines the RGB value for the entire pixel.
                '''
                
                color = np.empty((0, 3))

                if tally['mandelbrot'] > 0:
                    for _ in range(tally['mandelbrot']):
                        color = np.append(color, colors['m'], axis=0)

                if tally['divergence'] > 0:
                    for _ in range(tally['divergence']):
                        divergence_multiplier = np.average(divergence_multipliers)
                        divergence_multiplier /= len(self.DIVERGENCE_LEVELS)
                        color = np.append(color, colors['d'] * divergence_multiplier, axis=0)

                color = np.average(color, axis=0)
                image_array[pixel_y, pixel_x] = color

                # The calculations are complete for this iteration, so show the
                # percent complete if the percent complete is a multiple of 10.
                i += 1

                percent_complete = (i+1) / (self.IMAGE_SIZE[0] * \
                                    self.IMAGE_SIZE[1])

                p_complete_ = int(percent_complete*100)//10*10

                if p_complete_ > p_complete:

                    p_complete = p_complete_

                    print(self.P_STRING.format(cr=self.CENTER[0],
                                               ci=self.CENTER[1],
                                               p=p_complete))

                    if self.SPEAK:

                        self.tts.say(self.P_STRING.format(cr=self.CENTER[0],
                                                            ci=self.CENTER[1],
                                                            p=p_complete))
                        self.tts.runAndWait()

        # Finally, write the image.
        IMAGE_F = 'mandelbrot center=' + str(self.CENTER[0]) + '+' + \
                  str(self.CENTER[1]) + 'i, top=' + str(self.TOP) + 'i, ' + \
                  str(self.IMAGE_SIZE[0]) + '×' + str(self.IMAGE_SIZE[1]) + \
                  '.png'
        IMAGE_PATH = os.path.join(self.IMAGE_DIR, IMAGE_F)

        self.write_image(image_array, IMAGE_PATH)

    def write_image(self, image_array, IMAGE_PATH):

        '''
        Write the image array to an image.
        '''

        image = Image.fromarray(image_array)

        image.save(IMAGE_PATH)

    def next_mandelbrot(self, z, c):

        '''
        Iterate the Mandelbrot equation.
        '''

        if z is None:

            z = complex(0 + 0j)

        return z**2 + c

    def pixels_to_coordinates(self, pixel_x, pixel_y):

        '''
        Find the coordinate of a pixel or subpixel in the complex plane.
        '''

        unit_per_pixel = (self.TOP - self.CENTER[1]) / (self.IMAGE_SIZE[1] / 2)

        real = (pixel_x - self.CENTER_PIXEL[0]) * unit_per_pixel + \
               self.CENTER[0]

        imaginary = (pixel_y - self.CENTER_PIXEL[1]) * unit_per_pixel - \
               self.CENTER[1]

        return (real, imaginary)

    def coordinates_good(self, real,  imaginary):
        '''
        Return True if the coordinates are in a circle of radius 2 with the
        center at the origin of the complex plane and False if otherwise.
        '''

        return math.sqrt(real**2 + imaginary**2) <= 2


if __name__ == '__main__':
    pass
