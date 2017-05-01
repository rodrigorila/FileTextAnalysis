# -*- coding: utf-8 -*-

import time

from gt import *
from WordFinder import *
from WordIndex import *

class TestSuite:
    _ok = 0
    _fail = 0

    # region Test Utilities
    def _reset(self):
        self._ok = 0
        self._fail = 0

    def _checkTrue(self, condition):
        if (condition):
            self._ok += 1
            return True
        else:
            self._fail += 1
            return False

    def _checkEqual(self, a, b):
        return self._checkTrue(cmp(a, b) is 0)
    # endregion

    def _gt_convert(self):
        self._checkEqual(gt.convert.BytesToString(1024), "1.0 KB")
        self._checkEqual(gt.convert.BytesToString(2048), "2.0 KB")
        self._checkEqual(gt.convert.BytesToString(2048+512), "2.5 KB")

    def _gt_files_filter(self):
        def runTest(ID, files, masksExclude, maxSizeString, expected):
            result = list(x.fullname for x in gt.files.filter(files, masksExclude, gt.convert.StringToBytes('100 MB')))
            if not self._checkEqual(sorted(result), sorted(expected)):
                gt.system.printEventAndResult("Test ID", ID)
                gt.system.printEventAndResult("Masks exclude", sorted(masksExclude))
                gt.system.printEventAndResult("Expected", sorted(expected))
                gt.system.printEventAndResult("Result", sorted(result))

        runTest(
            "Basic",
            [
                FileData(u"yes.dat", gt.convert.StringToBytes('2 MB')),
                FileData(u"yes.docx", gt.convert.StringToBytes('50 MB')),
                FileData(u"yes.txt", gt.convert.StringToBytes('20 MB')),
                FileData(u"yes.exe.txt", gt.convert.StringToBytes('20 MB')),

                FileData(u"no extension.exe", gt.convert.StringToBytes('10 MB')),
                FileData(u"no extension.~dat", gt.convert.StringToBytes('35 MB')),
                FileData(u"no extension.dat~", gt.convert.StringToBytes('102 KB')),
                FileData(u"no extension.~dat~", gt.convert.StringToBytes('5 KB')),
                FileData(u"no extension.~dat~2", gt.convert.StringToBytes('12 KB')),
                FileData(u"no size.docx", gt.convert.StringToBytes('101 MB')),
                FileData(u"no size.dat", gt.convert.StringToBytes('1 GB')),
            ],
            ["*.exe", "*.~*", "*.*~"],
            gt.convert.StringToBytes("100 MB"),
            [u'yes.dat', u'yes.docx', u'yes.txt', u'yes.exe.txt']
        )


    def _findWords(self):

        def runTest(TestID, words, data, expected):
            r = list(WordFinder.findWords(data, words))

            if not self._checkEqual(sorted(list(r)), sorted(list(expected))):
                print "Test ID : %s.%s" % ("_findWordsInFile", TestID)
                print "Data    : %s" % (data)
                print "Words   : %s" % (words)
                print "Expected: %s" % list(expected)
                print "Results : %s" % list(r)
                print

        runTest('Empty no words', [], '', ())
        runTest('Empty', ['CAT', 'DOG'], '', ())
        runTest('Basic', ['cat'], 'cat', [('cat', 1)])

        runTest('non-case-sensitive', ['CAT'], 'CAT.Cat.cat.XCAT.CATX.XCATX', [('cat', 3)])

        runTest('two words', ['CAT', 'DOG'], 'CAT.Cat.cat.catdog.dogcat.dOg', [('cat', 3), ('dog', 1)])
        runTest('second word', ['CAT', 'DOG'], 'xdog.dOg', [('dog', 1)])

        runTest('two words many matches',
                ['CAT', 'DOG'],
                'cat_dog_CAT_DOG_Cat-Dog-CAT CatDog_DogCat C AT DO G Catalog Dodge',
                [('cat', 4), ('dog', 3)])

        runTest('letters', ['a', 'b'], 'nothing a b in (a,b) that is backup alpha respect to b', (('b', 3), ('a', 2)))

        runTest('single new line character',
                ['uno', 'dos', 'tres', 'cuatro'],
                'Uno\nDos\nTres\nCuatro\nCinco\nSeis\nSiete\nOcho\nNueve\nDiez',
                (('uno', 1), ('dos', 1), ('tres', 1), ('cuatro', 1)))

        runTest('only two matches', ['uno', 'cuatro'], 'Uno.Cuatro', [('uno', 1), ('cuatro', 1)])

        runTest('many no-matching words', ['palabra', 'nada', 'ni', 'me', 'tenemos'], 'No tenemos esa palabra', [('palabra', 1), ('tenemos', 1)])

        runTest('Unicode strings',
                [u'cáñamo', u'candado'],
                u'El cáñamo está en la habitación con candado',
                [(u'cáñamo', 1), ('candado', 1)])

    def _findWordsInFiles(self):

        def runTest(TestID, fileName, wordList, expected):
            fd = FileData(fileName)

            fd.words = list(WordFinder.findWords(gt.files.extractChars(fileName), wordList))

            if not self._checkEqual(sorted(fd.words), sorted(expected)):
                print "Test ID : %s.%s" % ("_runFindWordsInFiles", TestID)
                print "File    : %s" % fileName
                print "Words   : %s" % wordList
                print "Expected: %s" % sorted(expected)
                print "Results : %s" % sorted(fd.words)
                print

        file_numbers_1_to_10_lowercase = os.path.join('TestFiles', 'Numbers', "1 to 10 - lowercase.txt")
        file_numbers_Almost_100KB = os.path.join('TestFiles', 'Numbers', 'Almost 100 KB.txt')
        # file_numbers_More_Than_10MB = os.path.join('TestFiles', 'Numbers', 'More than 10 MB.txt')
        # file_numbers_More_Than_30MB = os.path.join('TestFiles', 'Numbers', 'More than 30 MB.txt')
        file_numbers_SpecialCharacters = os.path.join('TestFiles', 'Numbers', u'Special characters in name áéíóúñüçÁÉÍÓÚÑÜç.txt')
        file_numbers_WordDocument = os.path.join('TestFiles', 'Numbers', "1 to 10 plain and with styles.docx")
        file_numbers_ZipFile = os.path.join('TestFiles', 'Numbers', "One to Ten.zip")
        file_numbers_ZipInsiseZip = os.path.join('TestFiles', 'Numbers', "Zip inside Zip.zip")
        file_numbers_ZipThreeLevels = os.path.join('TestFiles', 'Numbers', "One to Ten in 3 levels of zip (total 7 times each number).zip")

        runTest(
            'File with special characters',
            file_numbers_SpecialCharacters,
            ['cinco', u'fríolentas', u'vicuñas'],
            [('cinco', 1), (u'vicuñas', 1)])

        runTest('file with lowercase 1', file_numbers_1_to_10_lowercase, ['uno'], [('uno', 1)])
        runTest('file with lowercase 2', file_numbers_1_to_10_lowercase, ['dos'], [('dos', 1)])
        runTest('file with lowercase 3', file_numbers_1_to_10_lowercase, ['uno', 'dos'], [('dos', 1), ('uno', 1)])
        runTest('file with Almost 100 KB', file_numbers_Almost_100KB, ['uno', 'dos'], [('dos', 1884), ('uno', 1884)])
        # runTest('file with More than 10 MB', file_numbers_More_Than_10MB, ['uno', 'dos'], [('dos', 197888), ('uno', 197888)])
        # runTest('file with More than 30 MB', file_numbers_More_Than_30MB, ['uno', 'dos'], [('dos', 192080*3), ('uno', 192080*3)])
        runTest('Word Document', file_numbers_WordDocument,
                ['uno', 'dos', 'tres', 'cuatro', 'cinco',
                 'seis', 'siete', 'ocho', 'nueve', 'diez'],
                [('uno', 3), ('dos', 3), ('tres', 3), ('cuatro', 3), ('cinco', 3),
                 ('seis', 3), ('siete', 3), ('ocho', 3), ('nueve', 3), ('diez', 3)])
        runTest("Zip file", file_numbers_ZipFile,
                ['one', 'two', 'three', 'four', 'five',
                 'six', 'seven', 'eight', 'nine', 'ten'],
                [('one', 1), ('two', 1), ('three', 1), ('four', 1), ('five', 1),
                 ('six', 1), ('seven', 1), ('eight', 1), ('nine', 1), ('ten', 1)])
        runTest("Zip inside zip", file_numbers_ZipInsiseZip,
                ['one', 'two', 'three', 'four', 'five',
                 'six', 'seven', 'eight', 'nine', 'ten'],
                [('one', 2), ('two', 2), ('three', 2), ('four', 2), ('five', 2),
                 ('six', 2), ('seven', 2), ('eight', 2), ('nine', 2), ('ten', 2)])
        runTest("Zip three levels", file_numbers_ZipThreeLevels,
                ['one', 'two', 'three', 'four', 'five',
                 'six', 'seven', 'eight', 'nine', 'ten'],
                [('one', 7), ('two', 7), ('three', 7), ('four', 7), ('five', 7),
                 ('six', 7), ('seven', 7), ('eight', 7), ('nine', 7), ('ten', 7)])

    def _wordIndex(self):

        def runTest(TestID, text, expected):
            ID = 'TID'

            wordIndex = {}
            WordIndex.addToWordIndex(ID, wordIndex, text)

            result = []
            for word, occurences in wordIndex.items():
                assert(len(occurences) == 1)
                assert (ID in occurences)
                result.append((word, occurences[ID]))
                # assert(len(occurences) == 1)
                # assert (occurences.has_key(ID))
                # result.append((word, occurences[ID]))

            if not self._checkEqual(sorted(result), sorted(list(expected))):
                print "Test ID : %s.%s" % ("_wordIndex", TestID)
                print "Text    : %s" % (text)
                print "Expected: %s" % (expected)
                print "Result  : %s" % (result)
                print

        runTest("Empty", "", [])

        runTest("Separators",
                u"alpha alpha_alpha.alpha\talpha(alpha)[alpha]¿alpha?alpha-alpha_alpha=alpha&alpha|alpha\nalpha\n\ralpha",
                [(u"alpha", 16)])

        runTest("No words found",
                u"38.9_x ls dn [de]", [])

        runTest("Many items (100 KB aprox)",
                u" ".join(["short story"] * 10000),
                [(u"short", 10000), (u"story", 10000)])

        runTest("Historia de las Bellas",
                u"La dramática historia de las bellas frágiles, bellas alegres y bellas ajenas",
                [(u"dramática", 1), (u"historia", 1), (u"las", 1), (u"bellas", 3), (u"frágiles", 1), (u"alegres", 1), (u"ajenas", 1)])

        runTest("Notas musicales",
                u"do re mi fa sol la si do",
                [(u"sol", 1)])

        runTest("Words with more than 3 repetitive letters",
                u"faaaar frrrrom theeeese pllllace innnnside ññññulen amongggg Jíííífix",
                [])

        runTest("Words with more than 3 repetitive letters and some good words",
                u"drrrraging my dog todaaaaay to thhhhe beeeeest Vet",
                [('dog', 1), ('vet', 1)])

    def _wordIndexTime(self):

        def runPath(ID, path):
            start = time.clock()

            files = gt.files.pathFiles(path)

            wordIndex = {}

            for file in files:
                WordIndex.addToWordIndex(file, wordIndex, gt.files.extractChars(file))

            gt.system.printEventAndResult(ID, "{0:.1f} seconds, {1} words".format(time.clock() - start, len(wordIndex)))

        # runPath('128 files of 1 KB', os.path.join('Numbers', '128 files of 1 KB'))
        # runPath('1024 files of 1 KB', os.path.join('Numbers', '1024 files of 1 KB'))
        runPath('512 files of 1 MB', os.path.join('Numbers', '512 files of 1 MB'))
        # runPath('1024 files of 1 MB', os.path.join('Numbers', '1024 files of 1 MB'))

    def runAll(self):
        self._reset()
        self._gt_convert()
        self._gt_files_filter ()
        self._findWords()
        self._findWordsInFiles()
        self._wordIndex ()
        self._wordIndexTime ()
        return (self._ok + self._fail, self._ok, self._fail)

