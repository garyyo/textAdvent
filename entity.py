from __future__ import annotations
from typing import List, Dict


class Dialogue:
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

    def check_allowed(self, keys):
        for key in self.whitelistKeys:
            if key not in keys:
                return False
        for key in keys:
            if key in self.blacklistKeys:
                return False
        return True

    def get_topic(self):
        return self.topic

    def get_text(self):
        return self.text

    def get_keys(self):
        return self.giveKeys, self.takeKeys


class Entity:
    name: str
    description: str
    init_description: str
    firstLook: bool
    visible: bool
    inventory: List[Item]

    def __init__(self, name, init_desc, desc):
        self.name = name
        self.description = desc
        self.init_description = init_desc
        self.firstLook = True
        self.visible = True

    def get_desc(self):
        if not self.visible:
            return ""
        if self.firstLook:
            return self.init_description
        return self.description

    def get_name(self):
        return self.name

    def get_visible(self):
        return self.visible

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def add_to_inventory(self, thing):
        # append item to inventory list
        self.inventory.append(thing)
        pass

    def remove_from_inventory(self, index):
        return self.inventory.pop(index)

    # get the index of an item in the players inventory, or None if it doesnt exist
    def get_inventory_index(self, item_name: str) -> int:
        for i in range(len(self.inventory)):
            if self.inventory[i].name == item_name:
                return i

    def get_inventory(self):
        return self.inventory


class Item(Entity):
    inventory_desc: str
    weight: float
    smell: str
    taste: str
    size: str
    pickupable: bool
    pickupKey: str

    def __init__(self, name, init_desc, inv_desc, desc, weight, smell, taste, size, pickupable, pickup_key):
        Entity.__init__(self, name, init_desc, desc)
        self.inventory_desc = inv_desc
        self.weight = weight
        self.smell = smell
        self.taste = taste
        self.size = size
        self.pickupable = pickupable
        self.pickupKey = pickup_key

    def get_inv_desc(self):
        return self.inventory_desc

    def get_weight(self):
        return self.weight

    def get_smell(self):
        return self.smell

    def get_taste(self):
        return self.taste

    def get_size(self):
        return self.size

    def get_pickupable(self):
        return self.pickupable

    def get_pickup_key(self):
        return self.pickupKey


class Background(Item):
    def __init__(self, name, init_desc, inv_desc, desc, weight, smell, taste, size):
        Item.__init__(self, name, init_desc, inv_desc, desc, weight, smell, taste, size, False, "")


class Container(Background):

    def __init__(self, name, init_desc, inv_desc, desc, weight, smell, taste, size):
        Background.__init__(self, name, init_desc, inv_desc, desc, weight, smell, taste, size)


class Actor(Entity):
    dialogueList: Dict[str, Dialogue]

    def __init__(self, name, init_desc, desc, ):
        Entity.__init__(self, name, init_desc, desc)
        self.dialogueList = {}

    def add_dialogue(self, chat: Dialogue):
        self.dialogueList[chat.get_topic()] = chat
        pass

    def get_topics(self, keys):
        return_string = ""
        for chatKey, chatEntry in self.dialogueList.items():
            if chatEntry.check_allowed(keys):
                return_string += chatEntry.get_topic() + "\n"
        if return_string == "":
            return "They don't want to talk"
        return_string = "Topics:\n" + return_string
        return return_string

    def check_topic(self, topic, keys):
        if topic in self.dialogueList:
            return self.dialogueList[topic].check_allowed(keys)
        return False

    def speak_topic(self, topic):
        if topic in self.dialogueList:
            return self.dialogueList[topic].get_text()
        return ""

    def give_dialogue_keys(self, topic):
        if topic in self.dialogueList:
            return self.dialogueList[topic].get_keys()
