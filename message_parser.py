#!/usr/bin/python3

from collections import namedtuple

class MessageParser(object):

    def getElements(self, message):
        allElements = message.split("-")
        Elements = namedtuple("Element", ["trelloCards", "description", "githubIssues"])
        elements = Elements(trelloCards=allElements[0],
                            description=allElements[1],
                            githubIssues=allElements[2])
        return elements

    def getListFrom(self, elements, splitString):
        listItems = elements.split(splitString)
        for item in listItems:
            # Strip any whitespaces at end
            item.rstrip()
        # Remove any empty entries
        filteredList = list(filter(None, listItems))
        return filteredList


# For self running
if __name__ == '__main__':
    testMessage = "%g6dHh25s%HA34cde2-Queuing Updates-#3#24"
    mp = MessageParser();
    elements = mp.getElements(testMessage)
    trelloCards = mp.getListFrom(elements.trelloCards, "%")
    issues = mp.getListFrom(elements.githubIssues, "#")
    print("Trello card ids: ", trelloCards)
    print("Github issues: ", issues)

