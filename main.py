from video_color_scheme import VideoColorScheme

# TODO: parse arguments

if __name__ == '__main__':
    video_path = 'videos/short.mp4'  # path to the video to process
    step = 1.  # get video frame each 'step' seconds
    number_of_colors = 5  # number of colors to extract from each image
    height, weight = 100, 100  # size of the result image

    v = VideoColorScheme(video_path=video_path, result_path='.', temp_folder='tmp', delete_after=False)

    images_path = v.video_to_images(step)  # convert initial video to array of images
    colors_path = v.images_to_colors(images_path, number_of_colors)  # extract the most popular image colors
    result_colors = v.choose_colors(colors_path, mode='popular')  # choose the colors for the result image
    v.compose_result_image(result_colors, height, weight)  # compose a result image from an array of colors
