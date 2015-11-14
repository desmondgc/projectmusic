Renames audio files based on metadata

Usage: projectmusic.py [options]

Options:
  -d ...,   --directory=...             Specify which directory to work in
                                        (default is the current directory)
  -f ...,   --format=...                Specify the naming format
  -p X,     --padding=X                 Pad track number with leading zeros,
                                        total track number length will be X chars
  -l,       --flatten                   Move all files into the same root
                                        directory
  -r,       --recursive                 Work recursively on the specified
                                        directory
  -t,       --test                      Only display the new file names; nothing
                                        will be renamed
  -n,       --noconfirm                 Do not ask before renaming files
  -h,       --help                      Display this help

Formatting:
  The following information is available to be used in the file name:
  album    artist    composer    title    track    disc

  To specify a file name format, enter the desired format enclosed in quotation
  marks. The words album, artist, composer, title, track and disc will be replaced
  by values retrieved from the audio file's metadata.

  For example, --format="artist - album [track] title" will rename music files
  with the name format:
  Sample Artist - Sample Album [1] Sample Title

  The following characters are of special importance to the operating system
  and cannot be used in the file name:
  \    /    :    *    ?    "    <    >    |

  (=) is replaced by the directory path separator, so to move files into
  artist and album subdirectories, the following format can be used:
  "artist(=)album(=)track - title"

  If no format is provided, the default format is the same as used in the above
  example.

Examples:
  projectmusic.py                       Renames music files in the current
                                        directory
  projectmusic.py -d /music/path/       Renames music files in /music/path/
  projectmusic.py -f "title -- artist"  Renames music files in the current
                                        directory with the name format:
                                        Sample Title -- Sample Artist.mp3"""

