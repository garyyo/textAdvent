from __future__ import annotations
from typing import List, Dict


class dialogue:
    topic: str
    text: str
    whitelistKeys: List[str]
    blacklistKeys: List[str]
    giveKeys: List[str]
    takeKeys: List[str]

    def __init__(self, topic, text, whitelist, blacklist, key, unkey):
        self.topic = topic
        self.text = text
        self.whitelistKeys = whitelist
        self.blacklistKeys = blacklist
        self.giveKeys = key
        self.takeKeys = unkey

    def checkAllowed(self, keys):
        for key in self.whitelistKeys:
            if key not in keys:
                return False
        for key in keys:
            if key in self.blacklistKeys:
                return False
        return True

    def getTopic(self):
        return self.topic

    def getText(self):
        return self.text

    def getKeys(self):
        return self.giveKeys, self.takeKeys


class entity:
    name: str
    description: str
    initDescription: str
    firstLook: bool
    visible: bool
    inventory: List[item]

    def __init__(self, name, initDesc, desc):
        self.name = name
        self.description = desc
        self.initDescription = initDesc
        self.firstLook = True
        self.visible = True

    def getDesc(self):
        if not self.visible:
            return ""
        if self.firstLook:
            return self.initDescription
        return self.description

    def getName(self):
        return self.name

    def getVisible(self):
        return self.visible

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def addToInventory(self, thing):
        # append item to inventory list
        self.inventory.append(thing)
        pass

    def removeFromInventory(self, index):
        return self.inventory.pop(index)

    # get the index of an item in the players inventory, or None if it doesnt exist
    def getInventoryIndex(self, itemName: str) -> int:
        for i in range(len(self.inventory)):
            if self.inventory[i].name == itemName:
                return i

    def getInventory(self):
        return self.inventory


class item(entity):
    inventoryDesc: str
    weight: float
    smell: str
    taste: str
    size: str
    pickupable: bool
    pickupKey: str

    def __init__(self, name, initDesc, invDesc, desc, weight, smell, taste, size, pickupable, pickupKey):
        entity.__init__(self, name, initDesc, desc)
        self.inventoryDesc = invDesc
        self.weight = weight
        self.smell = smell
        self.taste = taste
        self.size = size
        self.pickupable = pickupable
        self.pickupKey = pickupKey

    def getInvDesc(self):
        return self.inventoryDesc

    def getWeight(self):
        return self.weight

    def getSmell(self):
        return self.smell

    def getTaste(self):
        return self.taste

    def getSize(self):
        return self.size

    def getPickupable(self):
        return self.pickupable

    def getPickupKey(self):
        return self.pickupKey


class background(item):
    def __init__(self, name, initDesc, invDesc, desc, weight, smell, taste, size):
        item.__init__(self, name, initDesc, invDesc, desc, weight, smell, taste, size, False, "")


class container(background):

    def __init__(self, name, initDesc, invDesc, desc, weight, smell, taste, size):
        background.__init__(self, name, initDesc, invDesc, desc, weight, smell, taste, size)


class actor(entity):
    dialogueList: Dict[str, dialogue]

    def __init__(self, name, initDesc, desc, ):
        entity.__init__(self, name, initDesc, desc)
        self.dialogueList = {}

    def addDialogue(self, chat: dialogue):
        self.dialogueList[chat.getTopic()] = chat
        pass

    def getTopics(self, keys):
        retString = ""
        for chatKey, chatEntry in self.dialogueList.items():
            if chatEntry.checkAllowed(keys):
                retString += chatEntry.getTopic() + "\n"
        if retString == "":
            return "They dont want to talk"
        retString = "Topics:\n" + retString
        return retString

    def checkTopic(self, topic, keys):
        if topic in self.dialogueList:
            return self.dialogueList[topic].checkAllowed(keys)
        return False

    def speakTopic(self, topic):
        if topic in self.dialogueList:
            return self.dialogueList[topic].getText()
        return ""

    def giveDialogueKeys(self, topic):
        if topic in self.dialogueList:
            return self.dialogueList[topic].getKeys()
