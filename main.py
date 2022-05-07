from video_color_scheme import VideoColorScheme

if __name__ == '__main__':
    video_path = 'videos/short.mp4'  # path to the video to process
    step = 1.  # get video frame each 'step' seconds
    number_of_colors = 5  # number of colors to extract from each image

    v = VideoColorScheme(video_path=video_path, result_path='.', temp_folder='tmp', delete_after=False)

    v.video_to_images(step=step)  # convert initial video to array of images
    v.images_to_colors(number_of_colors=number_of_colors)  # extract the most popular image colors
    v.compose_result_image(mode='popular')  # compose a result image from an array of colors
