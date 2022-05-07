from video_color_scheme import VideoColorScheme

if __name__ == '__main__':
    video_path = 'videos/batman.mp4'

    v = VideoColorScheme(video_path=video_path)

    v.video_to_images()  # convert initial video to array of images
    v.images_to_colors()  # extract the most popular image colors
    v.compose_result_image()  # compose a result image from an array of colors
