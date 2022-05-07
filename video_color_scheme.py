import os
import moviepy.editor as mp

import numpy as np
from tqdm import tqdm


class VideoColorScheme:
    def __init__(self, video_path, delete_after=True):
        self.images_path = None
        self.colors = None
        self.images = None
        self.video_path = video_path
        self.video = self.__read_video(video_path)

        # self.delete_after = delete_after

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

        return video

    def video_to_images(self, step, images_path):
        """
        Convert video to list of images. Get video frame each 'step' seconds.
        Saves list of images into 'images_path' file.

        Parameters:
            step (float): step in seconds
            images_path (str): filename to save a list of images including extension (.npy)
        """

        self.images = []
        video_duration = int(self.video.duration)  # in seconds

        for t in np.arange(0, video_duration, step):
            image = self.video.get_frame(t)  # get current video frame
            self.images.append(image)  # add it into list

        # save images array to disk
        self.images = np.array(self.images)
        # self.images_path = images_path
        np.save(images_path, self.images)

        print(f"Video file {self.video_path} was successfully converted to an image array")
        print(f"Images saved into {images_path} file")

    def images_to_colors(self, images_path, colors_path, mode):
        """
        Read a list of images from 'images_path' and convert them into the most popular colors.

        :param images_path:
        :param colors_path:
        :param mode:
        :return:
        """

        print("Start extracting the most popular color from images")
        print(f"Images: {images_path}, mode: {mode}")

        # read images file
        with open(images_path, 'rb') as file:
            self.images = np.load(file)
        print(f"Images from {images_path} were successfully read")

        self.colors = []
        for image in tqdm(self.images):
            color = self.__image_to_colors(image, mode)
            self.colors.append(color)

        # save colors array to disk
        self.colors = np.array(self.colors)
        np.save(colors_path, self.colors)

        print(f"Images {images_path} were successfully converted to an colors array")
        print(f"Colors saved into {colors_path} file")

    @staticmethod
    def __image_to_colors():
        """ Extract the most popular colors from an image """

        return 1

    def compose_result_image(self):

        pass
