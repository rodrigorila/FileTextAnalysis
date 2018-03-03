import pypff

from WordFinder import WordFinder
from gt import gt, OpenFileSafe

import csv

class PFFParser:
    @staticmethod
    def __show__(folders):

        def printSubFolders(sub_folders, level):
            if sub_folders is None:
                return

            for sf in sub_folders:
                print "{0}{1}({2})".format(" " * level, sf.name, sf.number_of_sub_items)

                for si in sf.sub_items:
                    if type(si) is pypff.message:
                        print "{0}-SENDER-{1}".format(" " * level, si.sender_name)
                        print "{0}-SUBJECT-{1}".format(" " * level, si.subject)
                        print "{0}-HEADERS-{1}".format(" " * level, si.transport_headers)
                        # print "{0}-BODY-{1}".format(" " * level, si.plain_text_body)
                        print ""

                printSubFolders(sf.sub_folders, level + 1)

        printSubFolders (folders, 0)

    @staticmethod
    def __email_writer__(results_file, source_file, wordsList):
        titles = [u"File", u"Sender", u"Subject", u"Created", u"Delivered"]
        counter = gt.__createWordCounter__(wordsList)

        def get_headers(wordsList):
            return titles if wordsList is None else titles + wordsList

        def writer (sender, subject, created, delivered, words):
            with OpenFileSafe(results_file, 'ab') as file:

                writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)

                if file.tell() == 0:
                    writer.writerow(get_headers(wordsList))

                values =[
                    source_file,
                    sender,
                    subject,
                    created,
                    delivered
                ] + counter(words)

                writer.writerow(values)

        return writer

    @staticmethod
    def __search__(folders, writer, wordsList):

        def write_message(msg):

            email_parts = [
                msg.transport_headers,
                msg.subject,
                msg.sender_name,
                msg.plain_text_body
            ]

            words = []

            for part in email_parts:
                for w, c in WordFinder.findWords(part, wordsList):
                    words.append((w, c))

            if len(words) > 0:
                try:
                    # msg.transport_headers  has more information for future implementations (Date, IPs, etc)


                    writer(msg.sender_name, msg.subject, "", "", words)
                except Exception as e:
                    print e
        def traverseThree(sub_folders, level):
            if sub_folders is None:
                return

            for sf in sub_folders:
                for si in sf.sub_items:
                    if type(si) is pypff.message:
                        write_message(si)

                traverseThree(sf.sub_folders, level + 1)

        traverseThree(folders, 0)


    @staticmethod
    def findWords(file, results_file, wordsList):
        # print "pypff version: " + pypff.get_version()

        pst = pypff.file()
        try:
            pst.open(file)

            # PFFParser.__show__(pst.root_folder.sub_folders)

            writer = PFFParser.__email_writer__(results_file, file, wordsList)
            PFFParser.__search__(pst.root_folder.sub_folders, writer, wordsList)
        finally:
            pst.close()

        return
