# -*- coding: utf-8 -*-

import sys
import math
import time
import csv
import os
import datetime
import fnmatch
import codecs
import zipfile
import tempfile
import shutil

from functools import wraps
#import mem_profile

TIME_STAMP_FORMAT = '%Y/%m/%d %H:%M:%S'

class FileData:

    def __init__(self, fullname, size = 0, c_time = 0, a_time = 0, m_time = 0):
        self.fullname = fullname
        self.size = size
        self.error = ""
        self.c_time = c_time
        self.a_time = a_time
        self.m_time = m_time
        self._words = {}
        self._remarks = []
        self._nameOnly, self._extension = gt.files.nameAndExt(self.fullname)
        return

    def __repr__(self):
        if self.error:
            return "name %s %s" % (self.fullname, self.error)

        return "name %s size: %d created: %d accessed: %d modified: %d [%s]" % \
               (
                   self.fullname,
                   self.size,
                   self.c_time,
                   self.a_time,
                   self.m_time,
                   list(self._words.items()))

    def addWord(self, name, value):
        if self._words.has_key(name):
            assert (False) # si esto sucede ¿deberíamos sumar?

        self._words[name] = value

    def addWords(self, keyValueTuples):
        for (key, value) in keyValueTuples:
            self.addWord(key, value)

    def addRemarks(self, comment):
        self._remarks.append(comment)

    @property
    def path(self):
        return os.path.dirname(self.fullname)

    @property
    def nameOnly(self):
        return self._nameOnly

    @property
    def extension(self):
        return self._extension

    @property
    def nameAndExtension(self):
        return self._nameOnly + self._extension

    # @property
    # def wordValue(self, name):
    #     return self._words.get(name, 0)
    #
    @property
    def words(self):
        return self._words.items()

    @property
    def remarks(self):
        return ' | '.join(self._remarks)

def LoggerDecorator(orig_func):

    @wraps(orig_func)
    def wrapper(*args, **kwargs):
        print 'Ran with args: {}, and kwargs: {}'.format(args, kwargs)
        return orig_func(*args, **kwargs)

    return wrapper

def TimerDecorator(orig_func):
    import time

    @wraps(orig_func)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = orig_func(*args, **kwargs)
        t2 = time.time() - t1
        print('{} ran in: {} sec'.format(orig_func.__name__, t2))
        return result

    return wrapper

class OpenFileSafe():

    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode

    def __enter__(self):
        while True:
            try:
                # EMULATE THE ERROR FOR TESTING:  raise IOError("error!!!!")

                self.open_file = open(self.filename, self.mode)

                return self.open_file

            except:
                answer = raw_input('Error opening file "%s" in mode "%s". Retry?' % (self.filename, self.mode))
                if not {'y': 0, 'yes': 0}.has_key(answer.lower()):
                    sys.exit(0)

    def __exit__(self, *args):
        self.open_file.close()

class gt:
    @staticmethod
    def __getFileListHeaders__():
        return [u"Full path", u"Name", u"Type", u"Size", u"Created", u"Accessed", u"Modified", u"Status"]

    @staticmethod
    def __getWordIndexHeaders__(fileCountPairs = 1):
        return [u"Word"] + [u"File", u"Count"] * fileCountPairs

    class strf:
        @staticmethod
        def rangeChar(c1, c2):
            """Generates the characters from `c1` to `c2`, inclusive."""
            for c in xrange(ord(c1), ord(c2) + 1):
                yield chr(c)

    class convert:
        @staticmethod
        def StringToFileTimeStamp(timeStampString):
            return time.mktime(datetime.datetime.strptime(timeStampString, TIME_STAMP_FORMAT).timetuple())

        @staticmethod
        def FileTimeStampToString(timeStamp):
            #return time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(timeStamp))
            return time.strftime(TIME_STAMP_FORMAT, time.localtime(timeStamp))

        @staticmethod
        def BytesToString(size_bytes):
           if (size_bytes == 0):
               return '0B'

           size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

           i = int(math.floor(math.log(size_bytes, 1024)))
           p = math.pow(1024, i)
           s = round(size_bytes/p, 2)

           return '%s %s' % (s, size_name[i])

        @staticmethod
        def StringToBytes(size_in_text):
            text = size_in_text.split(" ")

            if (len(text) != 2):
                raise ValueError('%s should be in the format "Value Units"' % (size_in_text))

            value = float(text [0])
            units = text [1]

            unitsDictionary = {
                "YB": 8,
                "ZB": 7,
                "EB": 6,
                "PB": 5,
                "TB": 4,
                "GB": 3,
                "MB": 2,
                "KB": 1,
                "B": 0,
            }

            if not unitsDictionary.has_key(units):
                raise AssertionError('Unknown units "%s"' % (units))

            return math.pow(1024, unitsDictionary.get(units, 0)) * value

    class files:
        @staticmethod
        def nameAndExt(filename):
            base = os.path.basename(filename)
            return  os.path.splitext(base)

        @staticmethod
        def sumSizes(fileDatas):
            total = 0
            for fd in fileDatas:
                total += fd.size
            return total

        @staticmethod
        def matchesMasks(fileName, masksExcludeList, emptyListDefaultResult):
            if masksExcludeList is None:
                return emptyListDefaultResult

            if len(masksExcludeList) == 0:
                return emptyListDefaultResult

            for mask in masksExcludeList:
                if (fnmatch.fnmatch(fileName.lower(), mask.lower())):
                    return True

            return False

        # @staticmethod
        # def validName(fileName):
        #     valid_chars = "-_.() %s%s%s" % (string.ascii_letters, string.digits, "áéíóúñüçÁÉÍÓÚÑÜç")
        #     result = ''.join(c for c in fileName if c in valid_chars)
        #     result = result.replace(' ', '_')  # I don't like spaces in filenames.
        #     return result

        @staticmethod
        def readCSVFile(fileName, readTitlesFunction, readLineFunction):
            must_read_title = True

            with OpenFileSafe(fileName, 'rb') as file:
            #with open(fileName, 'rb') as file:
                reader = csv.reader(file, delimiter=',')

                for index, values in enumerate(reader):
                    if (must_read_title):
                        readTitlesFunction(index, values)
                        must_read_title = False
                        continue

                    fd = readLineFunction(index, values)

                    yield fd

        @staticmethod
        def loadFileList(fileName):
            wordsList = []

            def readTitles(index, values):
                for t in values[8:]:
                    wordsList.append(t)

            def readLine(index, values):
                fullname = values[0]
                # values[1] "Name" column, ignored
                # values[2] "Extension" column, ignored
                size = int(values[3])
                ct = gt.convert.StringToFileTimeStamp(values[4])
                at = gt.convert.StringToFileTimeStamp(values[5])
                mt = gt.convert.StringToFileTimeStamp(values[6])
                # values[7] "Remarks" column, ignored
                wordMatches = values[8:]

                fd = FileData(fullname, size, ct, at, mt)

                if len(wordMatches) > len(wordsList):
                    raise AssertionError("Too many values at line %d (Max. %d)" % (index, len(wordsList)))

                for word, count in zip(wordsList, wordMatches):
                    fd.addWord(word, count)

                return fd

            return  gt.files.readCSVFile(fileName, readTitles, readLine)

        # Appends the dictionary of "<file name> <file data>" pairs to a CSV file
        @staticmethod
        def saveFileList(files, fileName, wordsList=None):
            wordTitlesIndex = {}

            def collectWordList():
                if wordsList is None:
                    return

                for index, word in enumerate(wordsList):
                    wordTitlesIndex[word] = index

            def getWordCounts(words):
                if wordsList is None:
                    return []

                list = map(lambda x : "", range(0, len(wordTitlesIndex)))

                for word, count in words:
                    # if not wordTitlesIndex.has_key(word):
                    #     pass
                    #
                    # if wordTitlesIndex[word] >= len(list):
                    #     pass
                    list[wordTitlesIndex[word]] = count

                return list

            collectWordList()

            with OpenFileSafe(fileName, 'ab') as file:

                writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)

                if file.tell() == 0 and wordsList is not None:
                    writer.writerow(gt.__getFileListHeaders__() + wordsList)

                for index, data in enumerate(files):
                    ct = gt.convert.FileTimeStampToString(data.c_time)
                    at = gt.convert.FileTimeStampToString(data.a_time)
                    mt = gt.convert.FileTimeStampToString(data.m_time)
                    name = data.nameOnly
                    extension = data.extension
                    remarks = data.remarks

                    values = [
                                 data.fullname, #0
                                 name, #1
                                 extension, #2
                                 data.size, #3
                                 ct, #4
                                 at, #5
                                 mt, #6
                                 remarks #7
                             ] + getWordCounts(data.words)

                    writer.writerow(values)

                    if index % 1000 == 0:
                        file.flush()

        @staticmethod
        def saveWordIndex(fileName, wordIndex):
            def fileCounterTuplesToForumlas(list):
                for i in list:
                    assert (len(i) == 2)
                    yield i[0] + 1
                    yield i[1]
                    # yield "=+Numbers_List_Filtered.A%d" % (i[1] + 2)

            with open(fileName, 'ab') as file:
                writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)

                maxLen = 0
                for word in wordIndex:
                    maxLen = max(maxLen, len(wordIndex[word]))

                writer.writerow(gt.__getWordIndexHeaders__(maxLen))

                for word in wordIndex:
                    # line = [word] + list(wordIndex[word].itemsIDAndCount())
                    line = [word] + list(fileCounterTuplesToForumlas(wordIndex[word].items()))
                    writer.writerow(line)

        @staticmethod
        def removeIfExists(fileName):
            if (os.path.exists(fileName)):
                os.remove(fileName)

        @staticmethod
        def pathFiles(path):
            for dirPath, dirs, files in os.walk(path):
                for filename in files:
                    fn = os.path.join(dirPath, filename)
                    yield fn

        # Displays the file list on screen
        @staticmethod
        def show(fileList):
            for data in fileList:
                print "%s (size:%d created:%d accessed:%d modified:%d)" % (
                    data.name, data.size, data.c_time, data.a_time, data.m_time)
            return

        # Iterator of FileData for all the files found at path
        @staticmethod
        def find(path):

            for dirPath, dirs, files in os.walk(path):
                for filename in files:
                    fn = os.path.join(dirPath, filename)
                    try:
                        stat = os.stat(fn)

                        sz = stat.st_size
                        ct = stat.st_ctime
                        at = stat.st_atime
                        mt = stat.st_mtime
                    except Exception as e:
                        print ('Unable to open file "%s". %s' % (fn, e.message))

                    yield FileData(fn, sz, ct, at, mt)

        # Iterator of FileData list for all the files that match the masks and size criteria
        @staticmethod
        def filter(filesList, masksIncludeList, masksExcludeList, maxFileSize, bannedFolders = {}):
            for file in filesList:
                if file.size == 0:
                    continue

                if file.size > maxFileSize:
                    continue

                if file.path.lower() in bannedFolders:
                    continue

                if not gt.files.matchesMasks(file.fullname, masksIncludeList, True):
                    continue

                if gt.files.matchesMasks(file.fullname, masksExcludeList, False):
                    continue

                yield file

        @staticmethod
        def extractChars(filename):

            def basicASCII(s):
                r = ""
                for c in s:
                    if c.isalnum():
                        r += c
                    else:
                        r += '_'
                return r

            def extractText(filename):
                def openFile():
                    try:
                        full = os.path.abspath(filename)

                        #check if the file exists to prevent an exception to be thrown by opening the file
                        if not os.path.exists(full):
                            raise AssertionError('File "%s" does not exist' % full)

                        # return OpenFileSafe(filename, 'rb')
                        file = codecs.open(filename, mode="r", encoding='UTF-8')
                        try:
                            file.read()  # TEST IF FILE IS UNICODE BY READING SOME CHARACTERS (THIS GENERATES AN EXCEPTION FORMAT IS NOT UNICODE)
                            file.seek(0, 0)
                        except:
                            file.close()
                            raise

                        return file
                    except:
                        # return codecs.open(filename, mode="rb", encoding='other-single-byte-encoding')
                        # return OpenFileSafe(filename, 'rb') its best that the exception is trapped outside
                        return open(full, "rb")

                with openFile() as f:
                    while True:
                        chunk = f.read(512 * 1024 * 1024)
                        if chunk:
                            for c in chunk:
                                yield c
                        else:
                            break
                return

            def extractZipped(filename):
                name, extension = gt.files.nameAndExt(filename)

                tempFolder = tempfile.mkdtemp(prefix=basicASCII(name+extension), suffix='_tmp')
                try:
                    with zipfile.ZipFile(filename, 'r') as zip:
                        zip.extractall(tempFolder)

                    for file in gt.files.pathFiles(tempFolder):
                        if zipfile.is_zipfile(file):
                            for c in  extractZipped(file):  # recursive call
                                yield c
                            continue
                            # raise AssertionError("Zip files that reside a zip file cannot been processed")

                        for c in extractText(file):
                            yield c
                finally:
                    shutil.rmtree(path=tempFolder)

            if zipfile.is_zipfile(filename):
                return extractZipped(filename)
            else:
                return extractText(filename)

        @staticmethod
        def lineCount(filename):
            with open(filename) as f:
                for i, l in enumerate(f):
                    pass
            return i + 1



    class system:
        # @staticmethod
        # def memUsed(self):
        #     return mem_profile.mem_profile.memory_usage_resource()
        #
        # @staticmethod
        # def memUsedString(self):
        #     return "Memory after {}Mb ".format(self.memUsed())

        @staticmethod
        def printEventAndResult(event, result, newLine = True):
            line = '{:>16} : {:<15}'.format(event, result)

            if newLine:
                print line
            else:
                sys.stdout.write(line)

        @staticmethod
        def progresReporter(goal):
            processGoal = float(goal)

            def reportProgress(processed, text=None):
                p = processed / processGoal * 100.0

                if not text is None:
                    gt.system.printEventAndResult("Progress", "{:5.1f}% @ {}".format(p, text[0:50].ljust(50)), False)
                    #sys.stdout.write("Progress        : {:5.1f}% @ {}".format(p, text[0:50].ljust(50)))
                else:
                    gt.system.printEventAndResult("Progress", "{:5.1f}%".format(p), False)
                    #ys.stdout.write("Progress        : {:5.1f}%".format(p))

                sys.stdout.write('\r')
                sys.stdout.flush()

            return reportProgress

        @staticmethod
        def timeClock(self):
            return time.clock()


