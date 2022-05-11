import argparse
import sys

from video_color_scheme import VideoColorScheme


def parse_args(_):
    parser = argparse.ArgumentParser()

    # required arguments
    parser.add_argument('--video_path', type=str, required=True,
                        default='videos/short.mp4', help='''Path to the video to process''')
    parser.add_argument('--result_path', type=str, required=True,
                        default='videos/short.png', help='''Path to save the result image (including .png)''')
    parser.add_argument('--width', type=float, required=True,
                        default=20, help='''Width of the result image, inches''')
    parser.add_argument('--height', type=float, required=True,
                        default=5, help='''Height of the result image, inches''')

    # less important arguments that can be leaved with default values
    parser.add_argument('--mode', type=str, required=False,
                        default='sample', help='''Mode to choose a color. 
                        If 'popular' - return the most popular color, else sample a color according to distribution''')
    parser.add_argument('--start', type=float, required=False,
                        default=1., help='''Time to start video processing (seconds)''')
    parser.add_argument('--step', type=float, required=False,
                        default=1., help='''Step in seconds''')
    parser.add_argument('--number_of_colors', type=float, required=False,
                        default=5, help='''Number of colors to extract from each image''')
    parser.add_argument('--delete_after', type=bool, required=False,
                        default=True, help='''If True, delete temporary files after processing''')

    return parser.parse_args()


def main(args):
    v = VideoColorScheme(video_path=args.video_path, temp_folder='tmp', delete_after=False)

    # convert initial video to array of images
    images_path = v.video_to_images(args.start, args.step)
    # extract the most popular image colors
    colors_path = v.images_to_colors(images_path, args.number_of_colors)
    # choose the colors for the result image
    result_colors = v.choose_colors(colors_path, mode=args.mode)
    # compose a result image from an array of colors
    v.compose_result_image(result_colors, width=args.width, height=args.height, result_path=args.result_path)


if __name__ == '__main__':
    main(parse_args(sys.argv[1:]))
