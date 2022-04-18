# fractals
Makes images of fractals like [those in my gallery](https://nate.mrvichin.com/fractals/).

![sample](/sample.jpg)

# introduction
In the past, I had written Python code for Ulam spirals and line diagrams. When I turned to fractals, the Mandelbrot set is mandatory to make for just about any thought about fractals. The vast majority of Mandelbrot set visualizations I found were made with contrasting colors, so, naturally, I wanted to make some with a pleasant color palette. For each image, each pixel is divided into subpixels to find how many of the coordinates are a part of the Mandelbrot set or diverge. Those who do diverge still look cool when shown based on how long they could hang on until mathematics forced them to diverge from the Mandelbrot set.

# packages
This requires a few packages.
* numpy
* PIL
* pyttsx3

# run the script
`resolution` is the, well, the resolution of the image. These only take even numbers for the resolution to facilitate a division by 2 in the code.

`colors` is a Python dictionary that sets `'m'` as the color of the Mandelbrot set and `'d'` as the color of coordinates that diverge from the Mandelbrot set.

`center` is what coordinate of the complex plane is the center pixel of the image as a tuple. If the center pixel of the image is -0.66 + 0i, the `center` is (-0.66, 0).

`top` is what imaginary coordinate of the complex plane is the top row of pixels of the image. If very top of the image is 1.6i in the complex plane, `top` is 1.6.

`magnification` defines how many subpixels a pixel is divided into. I tended towards factors of 255 since their purpose is to effect the brightness of the color of a pixel. This has a great impact on how much time the render takes. To set magnification to 1 means no subpixels are calculated.

`divergence_iterations` define how many iterations of the Mandelbrot equation a coordinate is put through until the code says whether it diverges or is a part of the Mandelbrot set. This also has a great impact on how much time a render takes. More iterations of course mean more time.

A `magnification` of 1 and `divergence_iterations` of 20 makes render time fast but less accurate. A `magnification` of 17 subpixels and `divergence_iterations` of 1600 or 4000 makes for a better image, but the render time takes many hours. A good thing to do is to render a 50×50 or 100×100 pixel image first for a test.

To toggle speech off, set `speak` to `False`.

If you're running the program in a loop to make animation stills, you may pass the frame number as `image_number` to the program for numbered file names.

An image subdirectory is created in the same folder as the script for the images. To run the code.

```
f = Fractal()

resolution = (100, 100)

magnification = 17

divergence_iterations = 4000

colors = {'m': (252, 163, 17),
          'd': (174, 32, 18)}

center=(-0.78, 0.15)

top=0.2

f.mandelbrot(resolution,
             colors,
             center=center,
             top=top,
             magnification=magnification,
             divergence_iterations=divergence_iterations,
             speak=False)
```
