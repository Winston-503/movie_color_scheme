import functools
import os
import pickle
from collections import Counter

import cv2
import moviepy.editor as mp
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from sklearn.cluster import KMeans
from tqdm import tqdm


class VideoColorScheme:
    def __init__(self, video_path, temp_folder='tmp', delete_after=True):
        """
        :param video_path: (str) path to the video to process
        :param temp_folder: (str) path to store temporary files
        :param delete_after: (bool) if true, delete temporary files after processing
        """

        self.video_path = video_path
        self.temp_folder = temp_folder
        self.delete_after = delete_after
        self.colors = None
        self.images = None

        self.video = self.__read_video(video_path)
        self.filename = os.path.basename(video_path)[:-4]

        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)  # create tmp directory if not exists

        # compose paths to store temp files
        self.images_path = os.path.join(self.temp_folder, f"{self.filename}_images.pkl")
        self.colors_path = os.path.join(self.temp_folder, f"{self.filename}_colors.pkl")

    @staticmethod
    def __read_video(video_path):
        """ Read video file using moviepy """

        video = None
        try:
            video = mp.VideoFileClip(video_path)
        except OSError:
            print("An error occurred while reading video file")
            print(f"File {video_path} doesn't exist")
        except Exception as e:
            print("An error occurred while reading video file")
            print(f"Error: {e}")

        print(f"\nVideo file '{video_path}' was successfully read\n")
        return video

    def video_to_images(self, start, step):
        """
        Convert video to the list of images. Get video frame each 'step' seconds.
        Save the list of images into 'self.images_path' file.

        :param start: (float) time to start video processing (seconds)
        :param step: (float) step in seconds
        :return (str) path to saved array of images
        """

        self.images = []
        video_duration = int(self.video.duration)  # in seconds

        print("Start converting video to images...")
        self.images = list(map(self.video.get_frame,
                               tqdm([t for t in np.arange(start, video_duration, step)])))
        # # the same as
        # for t in tqdm(np.arange(start, video_duration, step)):
        #     image = self.video.get_frame(t)  # get current video frame
        #     self.images.append(image)  # add it into list

        save(self.images, self.images_path)  # save images array to disk
        print(f"Video file '{self.video_path}' was successfully converted to an image array")
        print(f"Images saved into '{self.images_path}' file\n")

        return self.images_path

    def images_to_colors(self, images_path=None, number_of_colors=5, compress_to=300):
        """
        Read a list of images from 'images_path' and convert them into the most popular colors.
        Save the list of colors into 'self.colors_path' file.

        :param images_path: (str) path to saved numpy array of images produced by 'video_to_images()' function.
            If None, use the value stored in the current object.
        :param number_of_colors: (int) number of colors to cluster the image.
            Large values slow down the analysis
        :param compress_to: (int) number of pixels to resize the image during preprocessing, usually 200-500.
            Large values slow down the analysis, small values skew its results
        :return: (str) path to saved array of colors
        """

        if images_path is None:
            images_path = self.images_path

        print("Start extracting the most popular color from images")
        print(f"Images: '{images_path}', number of colors: {number_of_colors}, compress to: {compress_to}")

        self.images = load(images_path)  # read images file
        print(f"Images from '{images_path}' were successfully read")

        print("Start analysing images colors...")
        self.colors = list(map(functools.partial(self.image_to_colors,
                                                 number_of_colors=number_of_colors, compress_to=compress_to),
                               tqdm([image for image in self.images])))

        # # the same as
        # self.colors = []
        # for image in tqdm(self.images):
        #     image_colors = self.image_to_colors(image, number_of_colors, compress_to)
        #     self.colors.append(image_colors)

        save(self.colors, self.colors_path)  # save colors array to disk
        print(f"Images '{images_path}' were successfully converted to a colors array")
        print(f"Colors saved into '{self.colors_path}' file")

        return self.colors_path

    def image_to_colors(self, image, number_of_colors, compress_to):
        """ Extract the most popular colors from an image """

        modified_image = self.__preprocess(image, compress_to)
        return self.__analyze_colors(modified_image, number_of_colors)

    @staticmethod
    def __preprocess(image, compress_to):
        """ Preprocess the image for cluster analysis: compress it and reshape to 2D array """

        image = cv2.resize(image, (compress_to, compress_to))  # resize the image to speed up the analysis
        image = image.reshape(image.shape[0] * image.shape[1], 3)  # reshape image because KMeans expects 2D array
        return image

    @staticmethod
    def __analyze_colors(image, number_of_colors):
        """
        Return the list of colors for the image.
        List contains of tuples (color, ratio) and contains 'number_of_colors' elements
        """

        def rgb_to_hex(rgb_color):
            """ Helper function to convert RGB color to HEX """
            hex_color = "#"
            for i in rgb_color:
                hex_color += ("{:02x}".format(int(i)))
            return hex_color

        clustering = KMeans(n_clusters=number_of_colors)
        color_labels = clustering.fit_predict(image)  # clustering prediction for each pixel
        center_colors = clustering.cluster_centers_  # coordinates of the cluster centroids

        color_counts = Counter(color_labels)  # the number of times each colors occurs on the image
        total = sum(color_counts.values())
        ordered_colors = [center_colors[idx] for idx in color_counts.keys()]  # colors ordered by popularity
        if len(ordered_colors) != number_of_colors:
            # if the clustering algorithm predicts fewer colors than we expect
            # (for example, if the image is uni-color)
            return [(rgb_to_hex(ordered_colors[0]), 1)]
        hex_colors = [(rgb_to_hex(ordered_colors[idx]), value / total) for idx, value in color_counts.items()]
        return hex_colors

    def choose_colors(self, colors_path=None, mode='sample'):
        """
        Choose a list of colors based on color analysis

        :param colors_path: (str) path to saved numpy array of colors produced by 'images_to_colors()' function.
            If None, use the value stored in the current object.
        :param mode: (str) mode to choose a color.
            If 'popular' - return the most popular color, else sample a color according to distribution
        :return: result_colors: (list of str) colors that will be used to compose the result image
        """

        if colors_path is None:
            colors_path = self.colors_path

        print("\nStart composing the result image")
        print(f"Colors: '{colors_path}', mode: {mode}")

        # read colors file
        self.colors = load(colors_path)
        print(f"Colors from '{colors_path}' were successfully read")

        print("Choosing colors for the result image...")
        result_colors = list(map(functools.partial(self.__choose_color, mode=mode),
                                 tqdm([color_tuple for color_tuple in self.colors])))

        # # the same as
        # result_colors = []
        # for color_tuple in tqdm(self.colors):
        #     result_color = self.__choose_color(color_tuple, mode)
        #     result_colors.append(result_color)

        print("Colors were successfully chosen")
        return result_colors

    @staticmethod
    def __choose_color(color_tuple, mode):
        """
        Choose a color from the color tuple

        :param color_tuple: (list of tuples) containing colors and their ratios on image, sorted by popularity
        :param mode: (str) mode to choose a color.
            If 'popular' - return the most popular color, else sample a color according to distribution
        :return (str) HEX string of chosen color
        """

        if mode == 'popular':
            return color_tuple[0][0]  # the first color
        else:
            colors, prob = zip(*color_tuple)
            if isinstance(colors, str):
                return colors  # single color - uni-color image
            return np.random.choice(colors, p=prob)

    def compose_result_image(self, result_colors, width, height, result_path, verbose=False):
        """
        Create the result image from an array of colors and save it into 'result_path'

        :param result_colors: (list of str) list of the HEX colors to create an image
        :param height: (int) height of the result image, inch
        :param width: (int) weight of the result image, inch
        :param result_path: (str) path to save the result image
        :param verbose: (bool) if True, show the result image
        """

        total_colors = len(result_colors)
        rectangle_width = width / total_colors

        print("\nStart composing the result image...")
        fig, ax = plt.subplots(figsize=(width, height))
        # draw two invisible lines that define the size of the canvas
        ax.plot([0, width], [height, height], linewidth=0)
        ax.plot([0, width], [0, 0], linewidth=0)

        for i, color in enumerate(result_colors):
            # Rectangle parameters:
            # - xy: The (x, y) coordinates for the anchor point of the rectangle
            # - width: Rectangle width
            # - height: Rectangle height
            ax.add_patch(Rectangle((i * rectangle_width, 0),
                                   rectangle_width, height, color=color))

        plt.axis('off')
        plt.margins(x=0, y=0)  # remove blank space around the plot
        plt.savefig(result_path, dpi=300, bbox_inches='tight')
        if verbose:
            plt.show()
        print("The result images was successfully composed")

        if self.delete_after:
            import shutil
            shutil.rmtree(self.temp_folder)
            print(f"delete_after=True, so temporary files in '{self.temp_folder}' folder were successfully deleted")
        else:
            print(f"delete_after=False, so temporary files in '{self.temp_folder}' folder were not deleted ")


def save(obj, filename):
    """ Save a Python object using pickle """
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)


def load(filename):
    """ Load a Python object using pickle """
    with open(filename, 'rb') as f:
        return pickle.load(f)
