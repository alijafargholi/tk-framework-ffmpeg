import os

import ffmpeg


class FFmpegAPI:
    def __init__(self):
        pass

    @staticmethod
    def convert_video_format(
        input_path: str, output_path: str, codec: str = "libx264"
    ) -> None:
        """Convert a given video file to a different format using ffmpeg.

        Args:
            input_path (str): Path to the input video file.
            output_path (str): Path to the output video file.
            codec (str, optional): Video codec to use. Defaults to "libx264".

        Raises:
            FileNotFoundError: If the input file does not exist.

        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file {input_path} does not exist.")

        ffmpeg.input(input_path).output(output_path, vcodec=codec).run()

    @staticmethod
    def generate_thumbnail_by_frame(
        video_path: str, output_path: str, frame_number: int, width: int = 320
    ) -> None:
        """Generate a thumbnail image from a specific frame, scaled to a
        smaller size.

        Args:
            video_path (str): Path to the input video file.
            output_path (str): Path to save the thumbnail image
                               (e.g., 'thumb.jpg').
            frame_number (int): The zero-based frame index to extract.
            width (int, optional): The desired thumbnail width in pixels.
                                   Defaults to 320.

        Returns:
            None
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Input file {video_path} does not exist.")

        try:
            (
                ffmpeg.input(video_path)
                # Select the frame by frame index
                .filter("select", f"gte(n,{frame_number - 1})")
                # Apply scaling: keep the same aspect ratio and set the
                # height to -1
                .filter("scale", width, -1)
                # Output only one frame
                .output(output_path, vframes=1)
                .run(overwrite_output=True)
            )
            print(f"Thumbnail generated successfully: {output_path}")
        except Exception as error:
            print(f"Error generating thumbnail: {error}")

    def clip_video(
        self,
        input_path: str,
        output_path: str,
        start_frame: int,
        end_frame: int,
    ):
        """
        Cuts a video clip from start_frame to end_frame with precise frame
        accuracy.

        Args:
            input_path (str): The path to the input video file.
            output_path (str): The path to the output video file.
            start_frame (int): The start frame number.
            end_frame (int): The end frame number.
        """
        fps = self.get_video_fps(input_path) or 24.0

        # Calculate start and end time
        start_time = (start_frame - 1) / fps
        end_time = end_frame / fps  # Adjusted to avoid off-by-one

        try:
            # Use precise trimming with re-encoding for frame accuracy
            ffmpeg.input(input_path, ss=start_time, to=end_time).output(
                output_path,
                vcodec="libx264",
                acodec="aac",
                strict="experimental",
            ).run(overwrite_output=True)

            print(f"Clip saved to: {output_path}")
        except ffmpeg.Error as e:
            print(f"Error during clip extraction: {e.stderr.decode()}")

    @staticmethod
    def get_video_fps(video_file: str) -> float | None:
        """
        Get the frames per second (fps) of a video file.

        Args:
            video_file (str): Path to the video file.

        Returns:
            float: Frames per second (fps) of the video.
        """
        try:
            probe = ffmpeg.probe(video_file)
            for stream in probe["streams"]:
                if stream["codec_type"] == "video":
                    fps_str = stream["r_frame_rate"]
                    num, denom = map(int, fps_str.split("/"))
                    return num / denom
        except Exception as e:
            print(f"Error retrieving FPS: {e}")
            return None
