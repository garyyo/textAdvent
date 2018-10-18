from typing import List, Dict


class event:
    whitelistKeys: List[str]
    blacklistKeys: List[str]
    giveKeys: List[str]
    takeKeys: List[str]
    eventType: str
    makeVisible: []
    makeInvisible: []

    def __init__(self, whitelist, blacklist, key, unkey, eventText, eventType):
        self.whitelistKeys = whitelist
        self.blacklistKeys = blacklist
        self.giveKeys = key
        self.takeKeys = unkey
        self.eventType = eventType
        self.eventText = eventText
        self.makeVisible = []
        self.makeInvisible = []

    def activate(self, agent):
        location = agent.get_location()
        for ref in self.makeVisible:
            name = ref[0]
            classType = ref[1]
            if classType == "actor":
                location.get_actor(name).show()
            if classType == "item":
                location.get_item(name).show()
        for ref in self.makeInvisible:
            name = ref[0]
            classType = ref[1]
            if classType == "actor":
                location.get_actor(name).hide()
            if classType == "item":
                location.get_item(name).hide()

        for key in self.giveKeys:
            agent.add_key(key)
        for key in self.takeKeys:
            agent.remove_key(key)

        return self.eventText

    def checkAllowed(self, keys):
        if self.whitelistKeys:
            for key in self.whitelistKeys:
                if key not in keys:
                    return False
        if self.blacklistKeys:
            for key in keys:
                if key in self.blacklistKeys:
                    return False
        return True

    def getType(self):
        return self.eventType

    def getKeys(self):
        return self.giveKeys, self.takeKeys

    def addMakeVisible(self, visibilityList):
        self.makeVisible.append(visibilityList)

    def addMakeInvisible(self, visibilityList):
        self.makeInvisible.append(visibilityList)

    def getMakeVisible(self):
        return self.makeVisible

    def getMakeInvisible(self):
        return self.makeInvisible

# todo: dialogue extends event?
