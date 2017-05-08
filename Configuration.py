import xml.etree.ElementTree

from gt import *


class Configuration:

    def __init__(self):
        self._maxFileSize = 500 * 1024 * 1024;  # 500 MB
        self._masksExlude = []
        self._masksInclude = []
        self._wordGroups = {}
        self._bannedFoldersLowercase = set()
        self.activeWordGroup = None

    def __appendWord__(self, wordGroup, word):
        if self.activeWordGroup is None:
            self.activeWordGroup = wordGroup

        self._wordGroups.setdefault(wordGroup, [])

        self._wordGroups[wordGroup].append(word)

    @property
    def maxFileSize(self):
        return self._maxFileSize

    @property
    def masksExlude(self):
        return self._masksExlude

    @property
    def masksInclude(self):
        return self._masksInclude

    @property
    def bannedFoldersLowercase(self):
        return self._bannedFoldersLowercase

    @property
    def hasBannedFolders(self):
        return len(self._bannedFoldersLowercase) > 0

    @property
    def hasWordGroups(self):
        return len(self._wordGroups) > 0

    @property
    def words(self):
        if self.activeWordGroup is None:
            return None
        elif not self._wordGroups.has_key(self.activeWordGroup):
            raise AssertionError('"%s" is not a WordGroup name in the configuration file. Please review the configuration file' % self.activeWordGroup)
        else:
            return self._wordGroups[self.activeWordGroup]

    def read(self, fileName):

        def DoFileConstraints(node, attributes):

            def listMasks(node, element):
                for masks in node.findall(element):
                    for mask in masks.text.split(';'):
                        if not mask:
                            continue

                        yield mask

            def DoMaxSize(node, attributes, value):
                self._maxFileSize = gt.convert.StringToBytes(value)

            def DoMasks(node, attributes, value):
                for mask in listMasks(node, 'Exclude'):
                    self._masksExlude.append(mask)

                for mask in listMasks(node, 'Include'):
                    self._masksInclude.append(mask)

            def DoBannedFolders(node, attributes, value):
                for folder in node.findall('Folder'):
                    if not folder.text:
                        continue

                    self._bannedFoldersLowercase.add(folder.text.lower())

            subgroups = {
                "MaxSize": DoMaxSize,
                "Masks": DoMasks,
                "BannedFolders": DoBannedFolders,
            }

            for child in node:
                f = subgroups.get(child.tag, lambda n, a, t : "")
                f(child, child.attrib, child.text)

            return


        def DoWordGroup(node, attributes):
            for word in node.findall('Word'):
                self.__appendWord__(attributes['name'], word.text)

        try:
            root = xml.etree.ElementTree.parse(fileName).getroot()
        except xml.etree.ElementTree.ParseError as e:
            raise AssertionError('Unable to read the configuration file "%s". %s' % (fileName, e.message))


        if (root.tag != "Configuration"):
            raise AssertionError("<Configuration> root not found in configuration file. Review the configuration file format (use --help parameter)")
            sys.exit(2)

        subgroups = {
            "FileConstraints": DoFileConstraints,
            "WordGroup": DoWordGroup,
        }

        for child in root:
            f = subgroups.get(child.tag, lambda n, a : "")
            f(child, child.attrib)

        return

