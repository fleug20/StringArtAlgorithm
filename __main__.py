#!/bin/python

"""
This python program is a mathematical approach to calculate and visualize string art based on a given input image. It allows users to create intricate geometric designs using virtual strings and nails, offering various customization options such as nail count, iterations, line thickness, and color inversion."""

import argparse
from pathlib import Path
from pstats import SortKey, Stats
import cProfile
import time
import datetime
import logging
from matplotlib import pyplot as plt
from PIL import Image
from StringArtAlgorithm import StringArtGenerator
import numpy as np


def main(args):
    # logging
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    time_start = time.process_time()

    generator = StringArtGenerator()
    MIN_NAILS = 50

    # evaluate arguments
    filepath = validatePath(args.filepath)
    if args.outputfolder != None:
        outputfolder = validatePath(args.outputfolder)
    else:
        outputfolder = Path.cwd()

    if args.nailcount and args.nailcount < MIN_NAILS:
        raise ValueError(f"Nail count must be at least {MIN_NAILS}.")
    if args.nailcount:
        generator.nailcount = args.nailcount
    if args.iterations:
        generator.iterations = args.iterations
    if args.linethickness:
        generator.line_thickness = args.linethickness
    if args.invert:
        generator.inverted = True

    #image preparation
    generator.loadImage(filepath)
    generator.calculateNailPositions()
    logger.info(f"\n image size: \t{generator.size} x {generator.size}\n")
    logger.info(f"\n calculated positions of {generator.nailcount} nails\n")

    # time estimation
    logger.info(f"\n estimated time: \t{generator.getTimeEstimation()} seconds\n")

    # generate
    generator.generate()

    # matplot setup
    size = generator.size
    nail_pos = generator.nail_pos
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    ax1.set(xlim=(0, size), ylim=(0, size))
    ax1.invert_yaxis()

    ax2.set(xlim=(0, size), ylim=(0, size))
    ax2.invert_yaxis()

    # matplot output
    image = Image.fromarray(generator.npInput_image)
    canvas = Image.fromarray(np.ones((size, size)) * 255)
    string_paths = generator.string_paths

    ax1.imshow(image, cmap="Greys_r")
    ax1.scatter(nail_pos[:, 0], nail_pos[:, 1], s=5)
    ax2.imshow(canvas, cmap="Greys_r")
    ax2.scatter(nail_pos[:, 0], nail_pos[:, 1], s=5)

    for path in string_paths:
        start_pos = path["start_pos"]
        end_pos = path["end_pos"]
        ax2.plot(
            [start_pos[0], end_pos[0]],
            [start_pos[1], end_pos[1]],
            color="black",
            linewidth=(generator.line_thickness * 0.1),
            alpha=0.8,
        )

    # finish
    time_end = time.process_time()
    logger.info(f" execution time: {int(time_end - time_start)}")
    now = datetime.datetime.now().strftime("%H%M%S")
    savepath = outputfolder / f"stringArt_{now}.png"
    saveStringPaths(outputfolder, string_paths, logger)
    plt.savefig(savepath, dpi=300)
    plt.show()


def getParser():
    parser = argparse.ArgumentParser(
        prog="StringArt Generator",
        description="this program will calculate stringart based on a given input image and visualize the result",
    )
    parser.add_argument("filepath", help="specify the path for the input image")
    parser.add_argument("-o", "--outputfolder", help="specify the path the output file")
    parser.add_argument(
        "-n",
        "--nailcount",
        help="set the amount of nails. Default is 250 / Minimum is 50",
        type=int,
    )
    parser.add_argument(
        "-i",
        "--iterations",
        help="set the amount iterations. Default is 1000",
        type=int,
    )
    parser.add_argument(
        "-l",
        "--linethickness",
        help="set the line thickness. Note: a thickness greater than 1 needs to use a different algorithm which results in longer execution time",
        type=int,
    )
    parser.add_argument(
        "--invert", help="invert the colors of the image", action="store_true"
    )

    return parser


def saveStringPaths(outputfolder, string_paths, logger):
    try:
        with open(outputfolder, "w") as file:
            for index in range(string_paths.size):
                line = f"string {index+1} // start: {string_paths['start_index'][index]}, end: {string_paths['end_index'][index]}"
                file.write(line + "\n")
    except:
        logger.warning("saving not possible\n")


def validatePath(path):
    path = Path(path)
    if path.exists() and path.is_absolute():
        return path
    if not path.is_absolute() and path.absolute().exists():
        return path.absolute()
    else:
        raise FileNotFoundError(f"path {path} not found.")


if __name__ == "__main__":
    parsed = getParser().parse_args()
    main(parsed)
