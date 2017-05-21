#
# F I L E   T E X T   A N A L Y S I S
#
#
# Samples:
#
# Numbers
#
# --root="Numbers" --target="Numbers_List_All.csv" -g
# --configuration="Numbers_Configuration.xml" --source="Numbers_List_All.csv" --target="Numbers_List_Filtered.csv" -f
# --configuration="Numbers_Configuration.xml" --key="OneThroughFour" --source="Numbers_List_Filtered.csv" --target="Numbers_List_Words.csv" -w
# --source="Numbers_List_Filtered.csv" --target="Numbers_List_Extracted.csv" -x
# --tests
# --help
#
# Documents
#
# --root="/home/rod/Documents" --target="Documents_All.csv" -g
# --configuration="Documents_Configuration.xml" --source="Documents_List_All.csv" --target="Documents_List_Filtered.csv" -f
# --source="Documents_List_Filtered.csv" --target="Documents_List_Extracted.csv" -x
# --source="Numbers_List_Extracted.csv" --info=RowCount

import os
import sys
import getopt
import time
import csv

from Configuration import Configuration
from WordFinder import WordFinder
from WordIndex import WordIndex
from gt import gt

def displayHelp():
    print 'Usage:'
    print
    print '  fta.py [Parameters] [Actions]'
    print
    print 'Parameters:'
    print '  -r:<Path>            Root folder'
    print '  -s:<FileName>        Full path of the source file'
    print '  -t:<FileName>        Full path of target file (if the file exists it will be overwriten'
    print '  -c:<Path>            Full path of the configuration file (see below)'
    print '  -k:<Path>            Wordgroup name to use in configuration file'
    print
    print 'Actions:'
    print '  -g                   Generate list of files (-r and -t are requiered)'
    print '  -f                   Filter files (-c, -s, and -t are requiered)'
    print '  -w                   Generate list of files (-r and -t are requiered)'
    print '  -h                   Display help'
    print '  -t                   Run all tests'
    print
    print 'Configuration file (xml format):'
    print '  <Configuration>'
    print '    <FileConstraints>'
    print '      <MaxSize>15 GB</MaxSize>'
    print '      <Masks>'
    print '        <Exclude> *.exe; *.bin </Exclude>'
    print '        <Exclude> *.cab </Exclude>'
    print '        <Exclude> *.msi </Exclude>'
    print '        <Exclude> *.msm </Exclude>'
    print '      </Masks>'
    print '    </FileConstraints>'
    print
    print '    <WordGroup name ="wordGroup1">'
    print '      <word> w1 </word>'
    print '      <word> w2 </word>'
    print '      <word> w3 </word>'
    print '      ...'
    print '    </WordGroup>'
    print
    print '    <WordGroup name ="wordGroup2">'
    print '      ...'
    print '    </WordGroup>'
    print '    ...'
    print '  </Configuration>'
    print
    print 'Example:'
    print '  python fta.py -r"C:\ " -t"C_Drive_Files.txt" -g'
    print '  python fta.py -c"Configuration.xml" -s"C_Drive_Files.txt" -t"Filtered_C_Drive_Files.txt"-g'
    print '  python fta.py -c"Configuration.xml" -k"wordGroup1" -s"Filtered_C_Drive_Files.txt" -t"WordCount_C_Drive_Files.txt"-g'
    return


def doRunAllTests(argument):
    from TestSuite import TestSuite

    suite = TestSuite()
    (total, ok, fail) = suite.runAll()
    gt.system.printEventAndResult("OK", ok)
    gt.system.printEventAndResult("Fail", fail)
    sys.exit(0)


def Execute(baseFolder, argv):
    configuration = Configuration()

    parameters = {
        "source": None,
        "target": None,
        "root": None,
        "key": None,
    }  # done with a dictionary beacuse in Python 2.7 you cannot use nonlocal

    def filesProgressIterator(files, progressInformation = None):

        def getExtraInformation():
            if progressInformation is None:
                return ""
            else:
                return progressInformation()


        totalBytes = gt.files.sumSizes(files)

        gt.system.printEventAndResult("Total files size", gt.convert.BytesToString(totalBytes))

        processedBytes = 0

        progress = gt.system.progresReporter(totalBytes)

        if totalBytes == 0:
            print "Nothing to do. No files with contents where found"
            return

        progress(0)  # start progress

        for file in files:
            yield file
            processedBytes += file.size
            text = ' '.join([file.nameAndExtension, getExtraInformation()])
            progress(processedBytes, text)

        assert (processedBytes == totalBytes)
        progress(processedBytes)
        print

    def doHelp(argument):
        displayHelp()
        sys.exit(0)

    def doGetActiveWordGroup(argument):
        parameters["key"] = argument

    def doGetTarget(argument):
        parameters["target"] = argument

    def doGetSource(argument):
        parameters["source"] = argument

    def doGetRoot(argument):
        parameters["root"] = argument

    def doReportConfiguraion():
        gt.system.printEventAndResult("Max. file size", gt.convert.BytesToString(configuration.maxFileSize))
        if not configuration.masksInclude is None:
            gt.system.printEventAndResult("Masks include", " ".join(configuration.masksInclude))
        if not configuration.masksExlude is None:
            gt.system.printEventAndResult("Masks exclude", " ".join(configuration.masksExlude))
        if configuration.hasWordGroups:
            gt.system.printEventAndResult("Word group", configuration.activeWordGroup)
            gt.system.printEventAndResult("Words", " ".join(configuration.words))
        if configuration.hasBannedFolders:
            gt.system.printEventAndResult("Banned folders", " ".join(configuration.bannedFoldersLowercase))

    def doReadConfiguration(argument):
        if not (os.path.exists(argument)):
            raise ValueError('File "%s" does not exist' % (argument))

        configuration.read(argument)

    def doGenerateFilesList(argument):
        t = parameters["target"]
        r = parameters["root"]

        gt.files.removeIfExists(t)

        gt.files.saveFileList(gt.files.find(r), t)

        gt.system.printEventAndResult('List of files', t)

        sys.exit(0)

    def doFilter(argument):
        s = parameters["source"]
        t = parameters["target"]

        if not (os.path.exists(s)):
            raise ValueError('File "%s" does not exist' % (s))

        doReportConfiguraion()

        gt.files.removeIfExists(t)

        gt.files.saveFileList(
            gt.files.filter(
                gt.files.loadFileList(s),
                configuration.masksInclude,
                configuration.masksExlude,
                configuration.maxFileSize,
                configuration.bannedFoldersLowercase
            ),
            t
        )

        gt.system.printEventAndResult('Filtered', t)

        sys.exit(0)

    def doFindFilesWithWords(argument):

        s = parameters["source"]
        t = parameters["target"]
        k = parameters["key"]

        if not k is None:
            configuration.activeWordGroup = k

        doReportConfiguraion()

        if not (os.path.exists(s)):
            raise ValueError('File "%s" does not exist' % (s))

        gt.files.removeIfExists(t)

        files = list(gt.files.loadFileList(s))

        for file in filesProgressIterator(files):
            try:
                for value, matchCount in WordFinder.findWords(gt.files.extractChars(file.fullname),
                                                              configuration.words):
                    file.addWord(value, matchCount)
            except Exception as e:
                file.addRemarks("Failed: %s" % str(e))

        gt.files.saveFileList(files, t, configuration.words)

        gt.system.printEventAndResult('Word Count', t)

        sys.exit(0)

    def doExtractWords(argument):

        def fileCounterTuplesToList(list):
            for i in list:
                for t in i:
                    yield t

        s = parameters["source"]
        t = parameters["target"]

        def getWordCount():
            return '(%d words)' % len(wordIndex)

        if not (os.path.exists(s)):
            raise ValueError('File "%s" does not exist' % (s))

        gt.files.removeIfExists(t)

        files = list(gt.files.loadFileList(s))

        wordIndex = {}

        for index, file in enumerate(filesProgressIterator(files, getWordCount)):
            try:
                WordIndex.addToWordIndex(index, wordIndex, gt.files.extractChars(file.fullname))
            except Exception as e:
                gt.system.printEventAndResult("Failed", "%s (%s)" % (file.fullname, str(e)))
                print

        gt.files.saveWordIndex(t, wordIndex)

        gt.system.printEventAndResult('Extracted', len(wordIndex))

        sys.exit(0)

    def doGetInformation(argument):

        s = parameters["source"]

        infoSet = {
            "RowCount": lambda fn: gt.system.printEventAndResult("Row Count", gt.files.lineCount(fn)),
        }

        f = infoSet.get(argument, lambda n, a: None)

        if f is None:
            raise AssertionError('"%s" is not recognized as valid --info option')

        f(s)

        return

    try:
        opts, args = getopt.getopt(argv, "r: s: t: c: k: i:"
                                         "g f w t h x",
                                   ["root=", "source=", "target=", "configuration=", "key=", "info=",
                                    "generate", "filter", "words", "tests", "help", "extract"])
    except getopt.GetoptError, e:
        print "Error in arguments: %s (use -h for help)" % e
        print
        sys.exit(2)

    methods = {
        '-h': doHelp,
        '-s': doGetSource,
        '-t': doGetTarget,
        '-r': doGetRoot,
        '-c': doReadConfiguration,
        '-k': doGetActiveWordGroup,
        '-g': doGenerateFilesList,
        '-f': doFilter,
        '-w': doFindFilesWithWords,
        '-q': doRunAllTests,
        '-x': doExtractWords,
        '-i': doGetInformation,

        '--help': doHelp,
        '--source': doGetSource,
        '--target': doGetTarget,
        '--root': doGetRoot,
        '--configuration': doReadConfiguration,
        '--generate': doGenerateFilesList,
        '--filter': doFilter,
        '--words': doFindFilesWithWords,
        '--tests': doRunAllTests,
        '--key': doGetActiveWordGroup,
        '--extract': doExtractWords,
        '--info': doGetInformation,
    }

    for opt, arg in opts:
        method = methods.get(opt, lambda argument: 0)
        method(arg)

    return


# --------------
# -- M A I N  --
# --------------
#
# NOTES.-
# 0.4.4 -> word count when displaying the progress in WordIndex
# 0.4.3 -> add try-except when loading files for inspection (find words and extract)
#          add BannedFolders option in configuration for filtering
# 0.4.2 -> zip recursion
# 0.4.1 -> word extraction with singly-linked lists
#
def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')

    gt.system.printEventAndResult("Version", "0.4.4")
    gt.system.printEventAndResult("Arguments", " ".join(sys.argv[1:]))

    start_time = time.time()
    try:
        Execute(os.path.abspath(os.path.dirname(sys.argv[0])), sys.argv[1:])
    finally:
        gt.system.printEventAndResult("Time", "%.1f sec" % (time.time() - start_time))
        print

main()
# import profile
# profile.run('main()')
