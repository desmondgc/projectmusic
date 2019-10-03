#!/usr/bin/env python2
#
# Copyright 2010 Desmond Cox <desmondgc AT gmail DOT com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Desmond Cox
# September 5, 2010

"""Project Music

Renames MP3 files based on ID3 tags

Usage: projectmusic.py [options]

Options:

  -d ...,   --directory=...             Specify which directory to work in 
                                        (default is the current directory)
  -f ...,   --format=...                Specify the naming format
  -l,       --flatten                   Move all files into the same root
                                        directory
  -r,       --recursive                 Work recursively on the specified 
                                        directory
  -t,       --test                      Only display the new file names; nothing
                                        will be renamed
  -h,       --help                      Display this help
  
Formatting:

  The following information is available to be used in the file name:

    * album
    * artist
    * title
    * track
    * year
  
  To specify a file name format, enter the desired format enclosed in quotation
  marks. The words album, artist, title, track, and year will be replaced by
  values retrieved from the MP3 files' ID3 tags.
  
  For example, --format="artist - album [track] title" will rename music files
  with the name format:

    Sample Artist - Sample Album [1] Sample Title
  
  The following characters are of special importance to the operating system 
  and cannot be used in the file name:

    /  \  :  <  >  |  ?  *  "

  (sep) is replaced by the directory path separator, so to move files into
  artist and album subdirectories, the following format can be used:

    "artist(sep)album(sep)track - title"
  
  If no format is provided, the default format is the same as used in the above
  example ("artist - album [track] title").

Examples:

  projectmusic.py                       Renames music files in the current 
                                        directory
  projectmusic.py -d /music/path/       Renames music files in /music/path/
  projectmusic.py -f "title -- artist"  Renames music files in the current
                                        directory with the name format:
                                        Sample Title -- Sample Artist.mp3"""

### Imports ###

import getopt, os, re, sys, time
from mutagen.easyid3 import EasyID3

### Constants ###

RESERVED_CHARS = re.compile(r'[/\\:<>|?*"]')
REPLACE_CHAR = '+'
PATH_SEPARATOR = '(sep)'
FORMAT_OPTIONS = re.compile(r'album|artist|title|track|year')

### Exceptions ###
    
class FormatError(Exception):
    """Exception raised due to improper formatting
    """
    pass

### Definitions ###

def scan(directory, recursive=False):
    result = []

    # http://docs.python.org/howto/unicode.html#unicode-filenames
    #
    # os.listdir(), which returns filenames, raises an issue: should it return
    # the Unicode version of filenames, or should it return 8-bit strings
    # containing the encoded versions? os.listdir() will do both, depending on
    # whether you provided the directory path as an 8-bit string or a Unicode
    # string. If you pass a Unicode string as the path, filenames will be
    # decoded using the filesystem's encoding and a list of Unicode strings will
    # be returned, while passing an 8-bit path will return the 8-bit versions of
    # the filenames.
    u_dir = unicode(directory)
    
    for root, dirs, files in os.walk(u_dir):
        result += [os.path.join(root, name) for name in files if name.lower().endswith('mp3')]
        if not recursive: break

    return result

def get_key(audio, key, default):
    try:
        return audio[key][0]
    except KeyError:
        return default

def get_disc(audio):
    return int(get_key(audio, 'discnumber', '1').split('/')[0])

def get_album(audio):
    # http://support.microsoft.com/kb/320081
    #
    # If you use typical Win32 syntax to open a file that has trailing spaces
    # or trailing periods in its name, the trailing spaces or periods are
    # stripped before the actual file is opened.
    return get_key(audio, 'album', 'No Album').rstrip('.')

def get_artist(audio):
    return get_key(audio, 'artist', 'No Artist')

def get_title(audio):
    return get_key(audio, 'title', 'No Title')

def get_track(audio):
    """audio['tracknumber'] returns strings in a variety of formats:

    * 1
    * 1/13
    * 01
    * 01/13"""
    return int(get_key(audio, 'tracknumber', '0').split('/')[0])

def get_year(audio):
    """audio['date'] returns strings in a variety of formats:

    * 2010-01-19
    * 2010"""
    return int(get_key(audio, 'date', '0').split('-')[0])

def generate_name(audio, fmt=u'%(artist)s - %(album)s [%(track)s] %(title)s'):
    raw_name = fmt % {
        'artist': get_artist(audio),
        'album': get_album(audio),
        'disc': get_disc(audio),
        'title': get_title(audio),
        'track': get_track(audio),
        'year': get_year(audio)
    }

    #x = raw_name.encode('ascii', 'replace') # for maximum portability?
    clean_name = re.sub(RESERVED_CHARS, REPLACE_CHAR, raw_name)
    name = clean_name.replace(PATH_SEPARATOR, os.path.sep)

    return name + os.path.splitext(audio.filename)[1]

def generate_format(fmt):
    if re.search(RESERVED_CHARS, fmt):
        raise FormatError, 'supplied format contains restricted characters'

    if not re.search(FORMAT_OPTIONS, fmt):
        # The supplied format must contain at least one of 'artist', 'album'
        # 'title', 'track', or 'year' or all files will be named identically.
        raise FormatError, 'supplied format does not contain any metadata keys'

    fmt = fmt.replace('album', '%(album)s')
    fmt = fmt.replace('artist', '%(artist)s')
    fmt = fmt.replace('disc', '%(disc)d')
    fmt = fmt.replace('title', '%(title)s')
    fmt = fmt.replace('track', '%(track)d')
    fmt = fmt.replace('year', '%(year)d')
    
    return fmt

def main():
    fmt = u'%(artist)s(sep)%(year)d - %(album)s(sep)%(disc)d.%(track)d - %(title)s'
    files = scan(os.getcwd(), recursive=True)
    skip_count = 0
    rename_count = 0
    
    if raw_input('Discovered %d files. Continue? ' % len(files)) != 'y':
        return
    else:
        print 'Started: %s\n' % time.ctime()

    for f in files:
        audio = EasyID3(f)
        name = generate_name(audio, fmt)

        if os.path.abspath(name) == f:
            # Name unchanged; skip.
            skip_count += 1
            #print 'Skip: %s' % f.encode('ascii', 'replace')
        elif os.path.exists(name):
            # Name changed, but target exists; skip.
            skip_count += 1
            print 'Exists: %s' % name.encode('ascii', 'replace')
            print 'Skip: %s' % f.encode('ascii', 'replace')
            raw_input('\nPress Enter to acknowledge.\n')
        else:
            # Name changed; rename.
            rename_count += 1
            print 'Rename: %s' % name.encode('ascii', 'replace')
            os.renames(f, name)

    print '\nStats:'
    print 'Skipped %d files' % skip_count
    print 'Renamed %d files' % rename_count
    
    raw_input('\nPress Enter to exit.')

if __name__ == "__main__":
    main()
