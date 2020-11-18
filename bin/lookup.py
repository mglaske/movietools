#!/usr/bin/env python

import os,sys,fnmatch,time
import optparse,logging
import enzyme
import hashlib
import json
from jsondb import JsonDB
import datetime
from pymediainfo import MediaInfo
#from hachoir_core.cmd_line import unicodeFilename
#from hachoir_core.i18n import getTerminalCharset
#from hachoir_metadata import extractMetadata
#from hachoir_parser import createParser


class MovieDB(JsonDB):

    def add(self, title, year, genre, filename,
            filetype="n/a", filesize=0,
            mkvinfo=None, md5sum=""):
        movie = {
            "title": title,
            "year": year,
            "genre": genre,
            "filename": filename,
            "filetype": filetype,
            "filesize": filesize,
            "mkvinfo": mkvinfo,
            "md5sum": md5sum,
            "valid": True
        }
        self.db[md5sum] = movie
        self.path_index[filename] = md5sum
        self.log.info("moviedb: adding filename=%s title=%s md5sum=%s to db!",
                      filename, title, md5sum)
        if self.write_immediate:
            self.save()
        return

    def remove(self, title=None, year=None, md5sum=None):
        remove = []
        remove_paths = []
        if md5sum:
            if md5sum in self.db:
                self.log.info("movideb: removing md5=%s title=%s year=%s",
                              md5sum, self.db[md5sum]['title'],
                              self.db[md5sum]['year'])
                remove.append(md5sum)
                remove_paths.append(self.db[md5sum]['filename'])
        if title and year:
            for md5sum, m in self.db.iteritems():
                if m['title'].lower() == title.lower() and m['year'] == year:
                    self.log.info("moviedb: removing md5=%s title=%s year=%s",
                                  md5sum, title, year)
                    remove.append(md5sum)
                    remove_paths.append(self.db[md5sum]['filename'])
        for e in remove:
            self.db.pop(e)
        for e in remove_paths:
            self.path_index.pop(e)
                    
        if self.write_immediate:
            self.save()
        return

    def search(self, string):
        results = []
        for md5sum, details in self.db.iteritems():
            if string.lower() in details['title'].lower():
                results.append(details)
        final_results = []
        for r in results:
            if not os.path.isfile(r['filename']):
                # Deleted movie file
                self.remove(md5sum=r['md5sum'])
                continue
            if not self.check_hash(r['filename']):
                self.log.warning("%s has a bad checksum!", r['filename'])
            final_results.append(r)
        return final_results
  
    def scan(self, startdir,
             extensions=['mkv', 'avi', 'mp4', 'mpeg', 'mpg', 'ts', 'flv', 'iso', 'm4v'],
             ext_skip=['md5','idx','sub','srt','smi','nfo','sfv','txt','json','jpeg','jpg','bak'],
             check=False):
        """ Scan startdir for files that end in extensions,
            if check is set, check the md5 file against the actual md5
            checksum, and report
        """
        abspath = os.path.abspath(startdir)
        for basepath, dirs, files in os.walk(abspath):
            for filename in files:
                fullpath = "%s/%s" % (basepath, filename)
                extension = filename.split('.')[-1].lower()
                basename = '.'.join(filename.split('.')[0:-1])
                filesize = os.path.getsize(fullpath)

                if extension in ext_skip:
                    continue

                if extension not in extensions:
                    self.log.warning("filename=%s is not in extensions list=%s, skipping",
                                     fullpath, extensions)
                    continue

                video_subdir = basepath
                video_year = 'n/a'
                video_name = filename
                video_genre = 'n/a'
                try:
                    video_subdir = basepath.split('/')[-1]
                    video_year = video_subdir.split('.')[-1]
                    video_name = ".".join(video_subdir.split('.')[0:-1])
                    video_genre = basepath.split('/')[-2]
                except Exception as e:
                    self.log.error("Error parsing video path=%s: %s", fullpath, e)
                self.log.debug('Found (%s): BasePath=%s Filenam=%s Basename=%s Extension=%s',
                               fullpath, basepath, filename, basename, extension)

                md5value = self.md5file(fullpath)
                if md5value:
                    self.log.debug('Found Hashfile: filename=%s MD5Hash=%s',
                                   filename, md5value)
                    if check:
                        checkvalue = self.md5Checksum(video).lower()
                        if md5value != checkvalue:
                            self.log.error("BAD: Hash mismatch for file=%s "
                                           "stored_hash=%s computed_hash=%s!",
                                           filename, md5value, checkvalue)
                        else:
                            self.log.info('GOOD: %s [ %s / %s ]', filename,
                                          md5value, checkvalue)
                else:
                    md5value = self.generate_checksum(fullpath)
                
                if md5value in self.db:
                    self.db[md5value]['valid'] = True
                    continue

                mediainfo = None
                mediainfo = self.mediainfo(fullpath)

                self.add(title=video_name, year=video_year,
                         genre=video_genre,
                         filename=fullpath, md5sum=md5value,
                         filetype=extension,
                         filesize=self.bytes_to_human(filesize),
                         mkvinfo=mediainfo)

        # remove files that have been deleted
        self.clean_invalid()
        return

    def mediainfo(self, path):
        info = { 'title': None, 'duration': None, 'chapters': None, 'video': [], 'audio': [] }
        video = { 'height': None, 'width': None, 'resolution': None, 'resname': None, 'codec': None, 'duration': None, 'bit_rate': None, 'bit_depth': None, 'aspect_ratio': None }
        audio = { 'freq': None, 'channels': None, 'language': None, 'bit_depth': None, 'codec': None }
        try:
            mi = MediaInfo.parse(path)
        except Exception as e:
            self.log.error("MediaInfo threw error reading path=%s: %s", path, e)
            return self.mkvinfo(path)

        for t in mi.tracks:
            if t.track_type == 'General':
                info['duration'] = self.ms_to_human(t.duration or 0)
                continue
            if t.track_type == "Video":
                vt = dict(video)
                try:
                    # note, display_aspect_ratio = 1.791 , eg 16:9
                    vt['aspect_ratio'] = t.other_display_aspect_ratio[0]
                except:
                    vt['aspect_ratio'] = 'n/a'
                vt['height'] = t.height
                vt['width'] = t.width
                vt['resolution'] = "%dx%d" % (t.width, t.height)
                if 'lace' in ( t.scan_type or "" ):
                    scantype = 'i'
                else:
                    scantype = 'p'
                if 1601 > t.height > 1080:
                    resname = "2160"
                elif 1081 > t.height > 720:
                    resname = "1080"
                elif 721 > t.height > 480:
                    resname = "720"
                elif 481 > t.height > 320:
                    resname = "320"
                else:
                    resname = "%s" % t.height
                vt['resname'] = "%s%s" % (resname, scantype)
                vt['frame_rate'] = t.frame_rate
                vt['codec'] = t.codec
                vt['bit_depth'] = t.bit_depth
                if t.bit_rate:
                    br = t.bit_rate
                elif t.nominal_bit_rate:
                    br = t.nominal_bit_rate
                else:
                    br = None
                try:
                    vt['bit_rate'] = self.speed_to_human(br)
                except:
                    vt['bit_rate'] = "n/a"

                info['video'].append( vt )
            if t.track_type == "Audio":
                at = dict(audio)
                at['codec'] = t.codec_family
                at['format'] = t.format
                at['bit_depth'] = t.bit_depth
                at['language'] = t.language
                at['channels'] = t.channel_s
                at['freq'] = t.sampling_rate
                info['audio'].append( at )

        return info

    def mkvinfo(self, path):
        info = { 'title': None, 'duration': None, 'chapters': None, 'video': [], 'audio': [] }
        video = { 'height': None, 'width': None, 'resolution': None, 'resname': None, 'codec': None, 'duration': None }
        audio = { 'freq': None, 'channels': None, 'language': None, 'bit_depth': None, 'codec': None }
        try:
            with open(path,'rb') as fh:
                mkv = enzyme.MKV(fh)
                self.log.debug("enzyme decoded into: %s", mkv)
        except Exception as e:
            self.log.error("Could not open (%s) with enzyme for getting video info! %s",
                           path, e)
            return info

        try:
            info['title'] = mkv.info.title
            info['duration'] = str(mkv.info.duration)
            info['chapters'] = [c.start for c in mkv.chapters]

            for v in mkv.video_tracks:
                vt = dict(video)
                vt['height'] = v.height
                vt['width'] = v.width
                vt['resolution'] = "%dx%d" % (v.width,v.height)
                if v.interlaced:
                    scantype = 'i'
                else:
                    scantype = 'p'
                if 1081 > v.height > 720:
                    vt['resname'] = '1080%s' % scantype
                elif 721 > v.height > 480:
                    vt['resname'] = '720%s' % scantype
                elif 481 > v.height > 320:
                    vt['resname'] = '320%s' % scantype
                else:
                    vt['resname'] = '%d%s' % (v.height,scantype)
                vt['codec'] = v.codec_id
                info['video'].append( vt )

            for a in mkv.audio_tracks:
                at = dict(audio)
                at['codec'] = a.codec_id
                at['bit_depth'] = a.bit_depth
                at['language'] = a.language
                at['channels'] = a.channels
                at['freq'] = a.sampling_frequency
                info['audio'].append( at )
        except Exception as e:
            self.log.error("Unable to parse mkv! %s",e)
        return info


def printmovies(results=[], showkey=False):
    # sort
    rs = {}
    for m in results:
        newkey = "%s;%s" % (m['title'], m['md5sum'])
        rs[newkey] = m

    if showkey:
        sys.stdout.write("{0:<32s}  ".format("md5sum"))
    sys.stdout.write("{0:<12s}  {1:<50s}  {2:<5s}  {3:<10s}  {4:<3s}  {5:<18s}  {6:<10s}  {7:<6s}  {8:<15s}  {9:<15s}\n".format("Genre","Title","Year","Duration","Ext","Resolution","Bitrate","AudioC","Formats","Size"))
    for key in sorted(rs.keys()):
        m = rs[key]
        if showkey:
            sys.stdout.write("{0:<32s}  ".format(m['md5sum']))
        try:
            sys.stdout.write( "{0:<12s}  {1:<50s}  {2:<5s}".format(m['genre'], m['title'].replace(".", " "), m['year']) )
        except Exception as e:
            logging.warning("Unable to print for title=%s err=%s", m['title'], e)

        extension = m['filename'][-3:]
        if m['mkvinfo']:
            resolution = "n/a"
            resname = "n/a"
            bitrate = "n/a"
            channels = -1
            mkvinfo = m['mkvinfo']
            video = mkvinfo.get('video', [])
            audio = mkvinfo.get('audio', [])
            if len(video) > 0:
                resolution = video[0].get('resolution', '--')
                resname = video[0].get('resname', '--')
                bitrate = video[0].get('bit_rate', '--')
            audio_tracks = len(audio)
            if audio_tracks > 0:
                channels = audio[0].get('channels', '--') or "--"
                channels = str(channels).replace("Object Based / ", "")
            formats = [x.get('format') for x in audio if x.get('format')]
            aformat = "/".join(formats)
            duration = str(mkvinfo.get('duration','--')).split('.')[0]

            res = "%s (%s)" % (resolution, resname)
            sys.stdout.write("  {0:<10s}  {1:<3s}  {2:<18s}  {3:<10s}  {4:<6s}  {5:<15s}  {6:<15s}".format(duration, extension.upper(), res, bitrate, channels, aformat, m.get('filesize', -1)))

        sys.stdout.write("\n")
    return


def main(options):
    db = MovieDB(filename=options.dbfile)
    db.log = options.log
    logging.info("Loaded %d movies from database=%s",
                 len(db.db), options.dbfile)

    if options.delete:
        db.remove(md5sum=options.delete)
        

    if options.scan:
        db.scan(options.startdir)

    if options.search:
        results = db.search(options.search.lower())
        if len(results) > 0:
            printmovies(results, options.showkey)
        
    db.save()
    return

if __name__ == '__main__':
    usage = "Usage: %prog [options] arg"
    parser = optparse.OptionParser(usage, version="%prog 1.0")
    parser.add_option("-s","--search", dest="search", type="string",help="Search string [%default]", default=None)
    parser.add_option("--resolution", dest="s_res", type="string", help="Search for files with [%default] resolution", default=None)
    parser.add_option("-d","--delete", dest="delete", type="string",help="Delete hash key from database [%default]", default=None)
    parser.add_option("--db", dest="dbfile", type="string", help="Database file [%default]", default="/d1/movies/db.json")
    parser.add_option("--start-dir",dest="startdir", type="string",metavar="STARTDIR",help="Start Directory to start processing movies [%default]",default="/d1/movies/")
    parser.add_option("-l", "--log-level", dest="log_level", type="string",metavar="LEVEL",help="change log level [%default]",default="info")
    parser.add_option("-c", "--check-videos", dest="checkvideos", action="store_true",help="Check video MD5s to find bad ones [%default]", default=False)
    parser.add_option("--scan", dest="scan", action="store_true", help="Scan files in addition to search db [%default]", default=False)
    parser.add_option("--key", dest="showkey", action="store_true", help="Show Key value [%default]", default=False)
    (options, args) = parser.parse_args()

    logger = logging.getLogger('')
    level = options.log_level.upper()
    logger.setLevel(getattr(logging, level))
    stderr_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)
    options.log = logger

    enzyme_logger = logging.getLogger("enzyme")
    enzyme_logger.setLevel(logging.ERROR)

    main(options)
    exit(0)
