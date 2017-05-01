
class WordFinder:
    WORD_END_CHARACTER = 'X'  # This makes it case-incentive

    class Word:
        def __init__(self, value):
            self._value = value.lower() + WordFinder.WORD_END_CHARACTER  # This makes it case-incentive
            self._lenght = len(value)
            self._position = 0
            self._matchCount = 0

        @property
        def matchCount(self):
            return self._matchCount

        @property
        def value(self):
            return self._value[:self._lenght]

        # @property
        # def position(self):
        #     return self._position
        #

        @property
        def current(self):
            return self._value[self._position]

        def printData(self):
            print "%s (%s at %d)" % (self._value, self.current, self._position)
            return

        # def checkCharacter(self, c):
        #     if self.position == len(self._value):
        #         self._overflow = True
        #
        #     if self._overflow:
        #         return
        #
        #     if self._value[self._position] == c:
        #         self._position += 1
        #
        # def checkMatch(self):
        #     if (not self._overflow) and (self._position == len(self._value) - 1):
        #         self._matchCount += 1

        def moveToNextCharacter(self, c):

            if self._position == -1:
                return

            if self._position == self._lenght:
                self._position = -1
                return

            if self._value[self._position] == c:
                self._position += 1
            else:
                self._position = -1

        def wordEnd(self):
            if self._position == -1:
                self._position = 0
                return

            if self._value[self._position] == WordFinder.WORD_END_CHARACTER:
                self._matchCount += 1

            self._position = 0

        def __repr__(self):
            # return "%s (%d matches)" % (self.value, self._matchCount)
            if self._position < 0 or self._position >= self._lenght:
                return "%s (%d matches)" % (self.value, self._matchCount)
            else:
                return "%s (%s at %d, %d matches)" % (self.value, self.current, self._position, self._matchCount)

    @staticmethod
    def __createWordsList__(words):
        list = []
        for w in words:
            list.append(WordFinder.Word(w))
        return list

    # def __createUsedCharactersList(self, words):
    #     list = []
    #
    #     for c in range(0, 255):
    #         list.append(False)
    #
    #     for w in words:
    #         for c in w.value:
    #             list[ord(c)] = True
    #
    #     return list
    #
    # def __getMaxWordSize(words):
    #     m = 0
    #     for w in words:
    #         m = max(m, len(w))
    #     return m

    @staticmethod
    def __printCharacterMap__(charMap, words):
        print "---- Char Map ---------------------------------------"
        for c in charMap:
            c.printData()

        print "---- Words ------------------------------------------"
        for w in words:
            w.printData()

        # print "-----------------------------------------------------"
        print

        return

    # def __checkCharacterInWords(self, byte):
    #
    #     c = chr(byte)
    #     used = self._usedChars[byte];
    #
    #     if not used:
    #         self.__resetWords()
    #
    #     if used:
    #         for w in self._words:
    #             w.check(c)
    #
    #     return list
    #
    # def __resetWords(self, _words):
    #     for w in _words:
    #         w.checkMatch()
    #         w.reset
    #     return
    #
    # def resetWords(self, _words, _charMap):
    #     for c in range(0, 255, 1):
    #         _charMap[c].clear()
    #
    #     for w in _words:
    #         _charMap[ord(w.current)].add(w)
    #
    #     return

    # def asBytes(self, s):
    #     for c in s:
    #         yield ord(c)
    #

    @staticmethod
    def findWords(chars, wordsList):
        words = WordFinder.__createWordsList__(wordsList)
        insideAWord = False

        def moveToNextCharacter(character):
            for word in words:
                word.moveToNextCharacter(character)

        def wordEnd():
            for word in words:
                word.wordEnd()

        # start1 = time.time()
        # end2 = 0
        # end3 = 0
        # end4 = 0
        # end5 = 0
        for c in chars:

            # start2 = time.time()
            c = c.lower()
            # end2 += time.time() - start2

            if c.isalpha():
                insideAWord = True

                # start3 = time.time()
                moveToNextCharacter(c)
                # end3 += time.time() - start3
            else:
                if insideAWord:
                    # start4 = time.time()
                    wordEnd()
                    # end4 += time.time() - start4

                    insideAWord = False

        wordEnd()
        # print "reset: %s" % (end5)
        # print "wordEnd: %s" % (end4)
        # print "moveToNextCharacter: %s" % (end3)
        # print "lower: %s" % (end2)
        # print "Whole: %s" % (time.time() - start1)

        for w in words:
            if w.matchCount > 0:
                yield w.value, w.matchCount
