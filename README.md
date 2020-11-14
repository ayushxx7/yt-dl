The script lets you download (hoard) a bunch of useful programming tutorials from YouTube.  
* Source files:
  * _single_videos.csv_ is a list of videos and relative paths.
  * _playlists.csv_ is a list of playlists and relative paths.
  * The paths of _*.csv_ save their contents to _./video_ or a subdirectory of it. 
  * Both files can be modified to download any kind of Youtube video and/or playlist.
* _download_all.py_ reads the csv files and saves the contents the specified directory.