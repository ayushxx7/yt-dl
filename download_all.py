import ffmpeg
import os
import csv
import logging
import concurrent.futures
import pytube as yt
from datetime import datetime
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
today = datetime.now().strftime("%Y_%m_%d_%H_%M")
if not os.path.exists("Logs"):
    os.mkdir("Logs")
log_file = f"Logs\{today}.log"
logging.basicConfig(format=log_format, handlers=[logging.FileHandler(log_file), logging.StreamHandler()], level=logging.INFO)

FILENAME_EXT = ".mp4"
ILLEGAL_CHARACHTERS = ".,<>:\"/\\|?*\'[]()"


def download_video(video_url: str, out_path: str, prefix: str = None):
    """
    Download the YouTube video from video_url to out_path. If prefix is specified, add it to the filename.
    Return the path to the file if successfull, False otherwise.

    If not existing, out_path gets created.
    The audio and video tracks are downloaded separately and then combined with ffmpeg.
    Every video is downloaded with a quality of 1080p. If 1080p is not available, it tries 720p.
    """

    # Get the video from YouTube
    try:
        video = yt.YouTube(video_url)
    except Exception as e:
        logging.error("Could not retrieve YouTube video from: {}\n    {}".format(video_url, e))
        return False

    # If necessary, create the output directory
    if not os.path.isdir(out_path):
        os.makedirs(out_path)
        logging.info("Created directory: \"{}\"".format(out_path))
    else:
        logging.info("Directory already exists: \"{}\"".format(out_path))

    # Build the filename
    if prefix is None:
        prefix = ""
    filename = prefix + video.title
    for illegal_char in ILLEGAL_CHARACHTERS:
        filename = filename.replace(illegal_char, "")
    logging.info("Successfully retrieved video \"{}\" from url \"{}\"".format(video.title, video_url))

    # If a file already exists on the same path, do not download it again
    out_file_path = os.path.join(out_path, filename + FILENAME_EXT)
    if os.path.exists(out_file_path):
        logging.info("Video already downloaded: {}".format(out_file_path))
        return out_file_path

    video_suffix = "_video"
    audio_suffix = "_audio"
    video_filename = filename + video_suffix
    audio_filename = filename + audio_suffix

    # Download the audio and video stream for the video
    video_stream = None
    for res in ["1080p", "720p", "480p", "360p"]:
        video_stream = video.streams.filter(mime_type="video/mp4", res=res).first()
        if video_stream is not None:
            break
    logging.info("Download start: {}".format(video_filename))
    video_stream.download(filename=video_filename, skip_existing=False, output_path=out_path)
    logging.info("Download end: {}".format(video_filename))
    audio_stream = video.streams.filter(mime_type="audio/mp4").first()
    logging.info("Download start: {}".format(audio_filename))
    audio_stream.download(filename=audio_filename, skip_existing=False, output_path=out_path)
    logging.info("Download end: {}".format(audio_filename))


    # Merge audio and video tracks with ffmpeg
    temp_out_filepath = os.path.join(out_path, filename + "_temp" + FILENAME_EXT)
    video_path = os.path.join(out_path, video_filename + FILENAME_EXT)
    audio_path = os.path.join(out_path, audio_filename + FILENAME_EXT)

    logging.info("Merging start of \"{}\" and \"{}\"".format(video_path, audio_path))

    try:
        """
        Might need to make a subprocess call to make execution faster
        ffmpeg -i "Python Multiprocessing Tutorial Run Code in Parallel Using the Multiprocessing Module_audio.mp4" -i "Python Multiprocessing Tutorial Run Code in Parallel Using the Multiprocessing Module_video.mp4" -ar 4100 -y -vcodec copy test.mp4
        """
        ffmpeg.output(
                ffmpeg.input(os.path.abspath(video_path)),
                ffmpeg.input(os.path.abspath(audio_path)),
                temp_out_filepath)\
            .global_args("-y")\
            .global_args('-loglevel', "warning")\
            .run()
    except Exception as e:
        logging.error("Merging {} with {} failed. {}".format(video_path, audio_path, e))
        return False
    else:
        logging.info(f"Temp File: {os.path.abspath(temp_out_filepath)}")
        os.rename(temp_out_filepath, out_file_path)
        logging.info("Merging ended of \"{}\" and \"{}\"".format(video_path, audio_path))


    # Delete source audio and video tracks
    os.remove(video_path)
    os.remove(audio_path)
    logging.debug("Deleted source files \"{}\" and \"{}\"".format(video_path, audio_path))
    return out_file_path


def main():
    """
    Download the videos for the videos in single_videos.csv and the playlists in playlists.csv to the specified locations.
    """

    # Read single videos to download
    dwnld_list = []
    with open("single_videos.csv", "rt", newline="") as f:
        dwnld_list += [[row[0], row[1], None] for row in csv.reader(f, delimiter=",")]
    logging.info("Successfully read single videos to download.")

    ##Read videos in playlists to download
    #logging.info("Read Playlist File")
    #with open("playlists.csv", "rt", newline="") as f:
    #    for pl_url, out_path in csv.reader(f, delimiter=","):
    #        logging.info(f"{pl_url}::{out_path}")
    #        try:
    #            list_urls = yt.Playlist(pl_url).video_urls
    #            logging.info(f"Playlist Urls: {list_urls}")
    #            dwnld_list += [[video_url, out_path, "{:02d} - ".format(i)]
    #                              for video_url, i in zip(list_urls, range(1,len(list_urls) + 1))]
    #        except Exception as e:
    #            logging.error("Something when wrong when tryting to retireve a playlist: {}\n{}".format(pl_url, e))
    #        else:
    #            logging.info("Successfully retrieved video list from {}".format(pl_url))
    #            logging.info(f"\n\n***Download List***\n{dwnld_list}")

    # Queue and run a process for each video to download
    with concurrent.futures.ProcessPoolExecutor() as executor:
        running_proc = []
        for video_url, out_path, prefix in dwnld_list:
            logging.info("Appending process to download \"{}\" to \"{}\"".format(video_url, out_path))
            running_proc.append(executor.submit(download_video, video_url, out_path, prefix))

        # Log the results of download_video
        for future in concurrent.futures.as_completed(running_proc):
            try:
                response = future.result()
                if response:
                    logging.info("Successfully downloaded and rendered: {}".format(response))
                else:
                    logging.error("Caution, download_video failed somewhere, there should be signs of it in the logs.")
            except Exception as e:
                logging.error("Some process raised an exception:\n{}".format(e))

        logging.info("main function completed")

    return


if __name__ == "__main__":
    main()
