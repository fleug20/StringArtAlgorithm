# String Art Generator

This python program is a mathematical approach to calculate and visualize string art based on a given input image. It allows users to create intricate geometric designs using strings and nails, offering various customization options such as nail count, iterations, line thickness, and color inversion.

![String Art example](/img/example.png)


## Features

- **Customizable Parameters**: Adjust the number of nails, iterations, and line thickness to create unique designs.
- **Inverted Colors**: Option to invert the colors of the input image for different visual effects.
- **Visualization**: Visualizes the string art using Matplotlib.
- **Export Options**: Saves the generated string art as an image file and provides a textual representation of the string paths.



## Installation

1. Clone the repository:
```
git clone [link]
```

2. Install requirements
```
pip install -r requirements.txt
```


## Usage
You can run the String Art Generator with the following command:
```
python __main__.py <path_to_image> [options]
```


## Options

| Option            | Description                                                                                   |
|-------------------|-----------------------------------------------------------------------------------------------|
| `-o, --outputfolder` | Specify the path to the output folder.                                                         |
| `-n, --nailcount`    | Set the number of nails (default is 250, minimum is 50).                                      |
| `-i, --iterations`   | Set the number of iterations (default is 1000).                                               |
| `-l, --linethickness`| Set the line thickness.                                                                       |
| `--invert`           | Invert the colors of the image.                                                               |


## example
```
python .\__main__.py input_image.jpg -n 300 -i 1500 -l 2 --invert
```

## Tips

Not every image is suitable for this algorithm. For the best results, consider the following things:
- The image should not be to complex.
- The algorithm works best on high contrast images
- The image should have a lot of contrast. Consider upping the contrast with a photo editing tool
- consider downscaling high-resolution images. This will result in better performance of the algorithm

## Acknowledgments

special thanks to:
- Virtually Passed's youtube Video "The Mathematics of String Art": https://www.youtube.com/watch?v=WGccIFf6MF8&t=2s
- A Greedy Algorithm for Generative String Art, by Baptiste Demoussel, Caroline Larboulette, Ravi Dattatreya: https://hal.science/hal-03901755/document