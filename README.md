# MovieTools

A small suite of tools for managing large collections of TV and Movies
and ensuring that they're error-free.  Most of these tools work around
generating a md5 hash and storing this in a file along with any movie
or video files detected.  This hash is also used for indexing and
identifying the files in simple json "database" files.  

Along with moviechecker.py, are lookup.py and lookup-tv.py.  These
handle scanning for new video files and indexing them into the database
file.  They are also used to search for movies and tv shows within
the database, and return them in a simple table.

There are definitely some hard-coded things in these programs, and,
while the json database worked well for a small couple thousand movie
database, it doesn't scale well to tv shows that could be in the tens
of thousands, so I've planned to update it to sqlite.


## LOOKUP.PY

```shell
Usage: lookup.py [options] arg

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s SEARCH, --search=SEARCH
                        Search string []
  --resolution=S_RES    Search for files with [none] resolution
  --year=S_YEAR         Search for files with [none] year
  -d DELETE, --delete=DELETE
                        Delete hash key from database [none]
  --db=DBFILE           Database file [/d1/movies/db.json]
  --limit=LIMIT         Limit scan to only X entries
  --start-dir=STARTDIR  Start Directory to start processing movies
                        [/d1/movies/]
  -c, --check-videos    Check video MD5s to find bad ones [False]
  --scan                Scan files in addition to search db [False]
  --key                 Show Key value [False]
  --path                Show Filename Path [False]
  -l LOG_LEVEL, --log-level=LOG_LEVEL
                        change log level [info]
```

Example:
```shell
me@sa00:/d1/movies# time ~/lookup.py -s rings
lookup - INFO - Loaded 3282 movies from database=/d1/movies/db.json
|Genre     |  Title                                             |  Year  |  Duration  |  EXT  |         Resolution  |    Bitrate  |  Bits  |  AudioC  |                       Formats  |      Size|
+----------+----------------------------------------------------+--------+------------+-------+---------------------+-------------+--------+----------+--------------------------------+----------+
|Animated  |  Kubo and the Two Strings                          |  2016  |   1:41:36  |  MKV  |   1918x804 (1080p)  |  16.22Mb/s  |   8    |  6       |                      DTS/AC-3  |   12.72GB|
|Fantasy   |  The Lord of the Rings The Fellowship of the Ring  |  2001  |   3:48:18  |  MKV  |   1920x800 (1080p)  |  10.89Mb/s  |   8    |  7 / 6   |  DTS/AC-3/AC-3/AC-3/AC-3/AC-3  |   22.46GB|
|Fantasy   |  The Lord of the Rings The Fellowship of the Ring  |  2001  |   3:48:18  |  MKV  |  3840x2160 (2160p)  |  67.94Mb/s  |   10   |  8       |                   TrueHD/AC-3  |  114.22GB|
|Fantasy   |  The Lord of the Rings The Return of the King      |  2003  |   4:23:17  |  MKV  |   1920x800 (1080p)  |  16.75Mb/s  |   8    |  7 / 6   |  DTS/AC-3/AC-3/AC-3/AC-3/AC-3  |   36.91GB|
|Fantasy   |  The Lord of the Rings The Return of the King      |  2003  |   4:23:17  |  MKV  |  3840x2160 (2160p)  |  65.60Mb/s  |   10   |  8       |                   TrueHD/AC-3  |  127.31GB|
|Fantasy   |  The Lord of the Rings The Two Towers              |  2002  |   3:55:31  |  MKV  |   1920x800 (1080p)  |  13.24Mb/s  |   8    |  7 / 6   |  DTS/AC-3/AC-3/AC-3/AC-3/AC-3  |   27.13GB|
|Fantasy   |  The Lord of the Rings The Two Towers              |  2002  |   3:55:32  |  MKV  |  3840x2160 (2160p)  |  62.22Mb/s  |   10   |  8       |                   TrueHD/AC-3  |  108.52GB|
|Classic   |  The Postman Rings Twice                           |  1946  |   1:52:59  |  MKV  |    1280x720 (720p)  |   2.05Mb/s  |   8    |  1       |                          AC-3  |    1.74GB|
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ Total (8) --+

real    0m0.312s
user    0m0.260s
sys     0m0.052s
```

## LOOKUP-TV.PY

```shell
Usage: lookup-tv.py [options] arg

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s SEARCH, --search=SEARCH
                        Search string []
  -S SEASON, --season=SEASON
                        Show just this season [none]
  -E EPISODE, --episode=EPISODE
                        Show just this epiosode [none]
  --show=SHOW           Search for this show exactly [none]
  -d DELETE, --delete=DELETE
                        Delete hash key from database [none]
  --db=DBFILE           Database file [/d1/tvshows/db.json]
  --limit=LIMIT         Limit scan to only X entries
  --start-dir=STARTDIR  Start Directory to start processing tvs [/d1/tvshows/]
  -c, --check-videos    Check video MD5s to find bad ones [False]
  --scan                Scan files in addition to search db [False]
  --key                 Show Key value [False]
  --path                Show Filename Path [False]
  -l LOG_LEVEL, --log-level=LOG_LEVEL
                        change log level [info]
```

Example:
```shell
me@sa00:/d1/movies# time ~/lookup-tv.py -s alf --show alf --season 2
lookup - INFO - Loaded 28300 tvs from database=/d1/tvshows/db.json
|Show  |  Title                              |  S/E     |  Duration  |  Ext  |      Resolution  |   Bitrate  |  Bits  |  AudioC  |     Formats  |      Size|
+------+-------------------------------------+----------+------------+-------+------------------+------------+--------+----------+--------------+----------+
|ALF   |  Working My Way Back to You         |  2 / 1   |   0:20:55  |  AVI  |  512x384 (320p)  |  1.02Mb/s  |   8    |  2       |  MPEG Audio  |  174.30MB|
|ALF   |  Somewhere Over the Rerun (a        |  2 / 2   |   0:20:37  |  AVI  |  512x384 (320p)  |  1.04Mb/s  |   8    |  2       |  MPEG Audio  |  174.52MB|
|ALF   |  Take a Look at Me Now              |  2 / 3   |   0:21:29  |  AVI  |  512x384 (320p)  |  0.99Mb/s  |   8    |  2       |  MPEG Audio  |  174.97MB|
|ALF   |  Wedding Bell Blues                 |  2 / 4   |   0:21:26  |  AVI  |  512x384 (320p)  |  1.00Mb/s  |   8    |  2       |  MPEG Audio  |  175.15MB|
|ALF   |  Prime Time                         |  2 / 5   |   0:21:26  |  AVI  |  512x384 (320p)  |  1.00Mb/s  |   8    |  2       |  MPEG Audio  |  175.14MB|
|ALF   |  Some Enchanted Evening             |  2 / 6   |   0:21:08  |  AVI  |  512x384 (320p)  |  1.01Mb/s  |   8    |  2       |  MPEG Audio  |  174.28MB|
|ALF   |  Oh, Pretty Woman                   |  2 / 7   |   0:21:28  |  AVI  |  512x384 (320p)  |  0.99Mb/s  |   8    |  2       |  MPEG Audio  |  175.12MB|
|ALF   |  Something's Wrong With Me          |  2 / 8   |   0:21:28  |  AVI  |  512x384 (320p)  |  1.00Mb/s  |   8    |  2       |  MPEG Audio  |  175.19MB|
|ALF   |  Night Train                        |  2 / 9   |   0:19:48  |  AVI  |  512x384 (320p)  |  1.09Mb/s  |   8    |  2       |  MPEG Audio  |  176.19MB|
|ALF   |  Isn't it Romantic                  |  2 / 10  |   0:21:25  |  AVI  |  512x384 (320p)  |  1.00Mb/s  |   8    |  2       |  MPEG Audio  |  174.24MB|
|ALF   |  Hail to the Chief                  |  2 / 11  |   0:21:15  |  AVI  |  512x384 (320p)  |  1.01Mb/s  |   8    |  2       |  MPEG Audio  |  175.88MB|
|ALF   |  The Boy Next Door                  |  2 / 14  |   0:21:13  |  AVI  |  512x384 (320p)  |  0.97Mb/s  |   8    |  2       |  MPEG Audio  |  174.39MB|
|ALF   |  Can I Get a Witness                |  2 / 15  |   0:21:28  |  AVI  |  512x384 (320p)  |  0.99Mb/s  |   8    |  2       |  MPEG Audio  |  175.23MB|
|ALF   |  We're So Sorry, Uncle Albert       |  2 / 16  |   0:21:28  |  AVI  |  512x384 (320p)  |  0.96Mb/s  |   8    |  2       |  MPEG Audio  |  174.38MB|
|ALF   |  Someone to Watch Over Me (1)       |  2 / 17  |   0:21:01  |  AVI  |  512x384 (320p)  |  1.02Mb/s  |   8    |  2       |  MPEG Audio  |  173.53MB|
|ALF   |  Someone to Watch Over Me (2)       |  2 / 18  |   0:21:29  |  AVI  |  512x384 (320p)  |  0.99Mb/s  |   8    |  2       |  MPEG Audio  |  173.55MB|
|ALF   |  We Gotta Get Out of This Place     |  2 / 19  |   0:21:06  |  AVI  |  512x400 (320p)  |  0.98Mb/s  |   8    |  2       |  MPEG Audio  |  174.37MB|
|ALF   |  You Ain't Nothin' But a Hound Dog  |  2 / 20  |   0:21:29  |  AVI  |  512x384 (320p)  |  0.99Mb/s  |   8    |  2       |  MPEG Audio  |  175.23MB|
|ALF   |  Hit Me With Your Best Shot         |  2 / 21  |   0:21:28  |  AVI  |  512x384 (320p)  |  0.99Mb/s  |   8    |  2       |  MPEG Audio  |  174.09MB|
|ALF   |  Movin' Out                         |  2 / 22  |   0:21:16  |  AVI  |  512x384 (320p)  |  1.01Mb/s  |   8    |  2       |  MPEG Audio  |  175.14MB|
|ALF   |  I'm Your Puppet                    |  2 / 23  |   0:21:26  |  AVI  |  512x384 (320p)  |  1.00Mb/s  |   8    |  2       |  MPEG Audio  |  175.69MB|
|ALF   |  Tequila                            |  2 / 24  |   0:21:28  |  AVI  |  512x384 (320p)  |  0.99Mb/s  |   8    |  2       |  MPEG Audio  |  175.03MB|
|ALF   |  We Are Family                      |  2 / 25  |   0:21:28  |  AVI  |  512x384 (320p)  |  1.00Mb/s  |   8    |  2       |  MPEG Audio  |  175.21MB|
|ALF   |  Varsity Drag                       |  2 / 26  |   0:21:28  |  AVI  |  512x400 (320p)  |  0.96Mb/s  |   8    |  2       |  MPEG Audio  |  174.33MB|
+-------------------------------------------------------------------------------------------------------------------------------------------- Total (24) --+

real    0m1.488s
user    0m1.333s
sys     0m0.152s
```

## MOVIECHECKER

```shell
Usage: moviechecker.py [options] arg

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s STARTDIR, --start-dir=STARTDIR
                        Start Directory to start processing movies
                        [/d1/movies/]
  -l LEVEL, --log-level=LEVEL
                        change log level [info]
  -c, --check-videos    Check video MD5's to find bad ones [False]
  --continuous=LOOP     Run continuously, and loop every [0] seconds

  Debug Options:
    -d, --debug         Print debug information
```
