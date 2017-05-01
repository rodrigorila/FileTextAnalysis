# -*- coding: utf-8 -*-

import string

class WordIndex:
    english_spanish_alphabet = list(string.lowercase[:]) + list(u'áéíóúñ')

    # max_l = 15

    @staticmethod
    def addToWordIndex(ID, wordIndex, chars):
        class Match:
            def __init__(self):
                self.ID = ID
                self.count = 1
                self.next = None

            def __len__(self):
                r = self
                c = 0
                while not r is None:
                    c += 1
                    r = r.next
                return c

            def __contains__(self, value):
                r = self

                while not r is None:
                    if r.ID == value:
                        return True

                return False

            def __str__(self):
                return "%s %d" % (self.ID, self.count)

            def __repr__(self):
                return "%s %d" % (self.ID, self.count)

            # returns the count for ID
            def __getitem__(self, ID):
                r = self
                while not r is None:
                    if ID == self.ID:
                        return r.count
                    r = r.next

                raise IndexError("Match out of index %s" % ID)

            def checkMatch(self, ID):
                if ID == self.ID:
                    self.count += 1
                    return True

                return False

            def items(self):
                r = self
                while (r):
                    yield r
                    r = r.next

            def itemsIDAndCount(self):
                r = self
                while (r):
                    yield r.ID
                    yield r.count
                    r = r.next

        WORD_MINIMUM_LENGTH = 3
        WORD_MAXIMUM_LENGTH = 15 #len("pneumonoultramicroscopicsilicovolcanoconiosis")
        WORD_MAX_REPEATED_LETTERS = 3 # words should not have more than 3 consecutive letters that are equal

        def __addWord__(word):
            # try:
            #     last = None
            #     for m in wordIndex[word].items():
            #         if m.checkMatch(ID):
            #             return
            #         last = m
            #
            #     assert (not last is None)
            #
            #     if not last is None:
            #         last.next = Match()
            #
            # except KeyError:
            #     wordIndex[word] = Match()

            if not wordIndex.has_key(word):
                wordIndex[word] = {ID:1}
                return

            if not wordIndex[word].has_key(ID):
                wordIndex[word][ID] = 1
                return

            wordIndex[word][ID] += 1

        def countEqualBack(w, c):
            count = 0
            for x in reversed(w):
                if x != c:
                    break
                count += 1
            return count

        insideAWord = False
        w =  []
        banned = False


        # start1 = time.time()
        # end2 = 0
        # end3 = 0
        # end4 =
        # end5 = 0
        for i, c in enumerate(chars):

            # start2 = time.time()
            c = c.lower()
            # end2 += time.time() - start2


            # [c for c in ''.join(chr(x) for x in range(255)) if c.isalpha()]
            # if c in WordIndex.english_spanish_alphabet:
            if c.isalpha():
                if banned:
                    continue

                if len(w) > WORD_MAXIMUM_LENGTH:
                    banned = True
                    continue

                # if len(w) >= WordIndex.max_l:
                #     WordIndex.max_l += 1
                #     print "%s = %d" % (''.join(w), len(w))
                #     continue

                insideAWord = True

                if countEqualBack(w, c) == WORD_MAX_REPEATED_LETTERS:
                    banned = True
                    continue

                w.append(c)
            else:
                if insideAWord:
                    if not banned and len(w) >= WORD_MINIMUM_LENGTH:
                        __addWord__(''.join(w))

                    w = []
                    insideAWord = False
                    banned = False

        if not banned and len(w) >= WORD_MINIMUM_LENGTH:
            __addWord__(''.join(w))

        # print "reset: %s" % (end5)
        # print "wordEnd: %s" % (end4)
        # print "moveToNextCharacter: %s" % (end3)
        # print "lower: %s" % (end2)
        # print "Whole: %s" % (time.time() - start1)

