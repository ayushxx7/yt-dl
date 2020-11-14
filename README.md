### Purpose
#### The script lets you download videos from YouTube.
* Source files:
  * _single_videos.csv_ is a list of videos and relative paths.
  * _playlists.csv_ is a list of playlists and relative paths.
  * The paths of _*.csv_ save their contents to _./video_ or a subdirectory of it.
  * Both files can be modified to download any kind of Youtube video and/or playlist.
* _download_all.py_ reads the csv files and saves the contents the specified directory.

### Technology under the hood:
- Uses pytube to download videos
- Uses ffmpeg to merge Audio and Video
  * The audio and video are downloaded in a separate process to increase efficiency
  * Leaving pytube to choose the download stream tends to favor the 720p resolution,
    hence to overcome this problem we ask the library to iterate over [1080p,720p,480p,360p]
    This way, it is forced to pick the 1080p stream for video if it's available
  * Multiplexed (muxed) streams are the type that contain both video and audio tracks in the same stream.
    YouTube provides these streams only in low qualities — the best they can be is 720p30.
