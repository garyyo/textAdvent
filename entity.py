from __future__ import annotations
from typing import Dict
from event import *


class Entity:
    name: str
    description: str
    examine_desc: str
    visible: bool
    events: List[Event]
    inventory: List[Item]

    def __init__(self, name, examine_desc, desc):
        self.name = name
        self.description = desc
        self.examine_desc = examine_desc
        self.visible = True
        self.events = []

    def get_desc(self):
        if not self.visible:
            return ""
        return self.description

    def get_examine(self):
        return self.examine_desc

    def get_name(self):
        return self.name

    def get_visible(self):
        return self.visible

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def add_event(self, event):
        if event:
            self.events.append(event)

    def get_events(self):
        return self.events

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

    def __init__(self, name, examine_desc, inv_desc, desc, weight, smell, taste, size, pickupable, pickup_key):
        Entity.__init__(self, name, examine_desc, desc)
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
    def __init__(self, name, examine_desc, inv_desc, desc, weight, smell, taste, size):
        Item.__init__(self, name, examine_desc, inv_desc, desc, weight, smell, taste, size, False, "")


class Container(Background):

    def __init__(self, name, examine_desc, inv_desc, desc, weight, smell, taste, size):
        Background.__init__(self, name, examine_desc, inv_desc, desc, weight, smell, taste, size)


class Actor(Entity):
    dialogueList: Dict[str, Dialogue]

    def __init__(self, name, examine_desc, desc, ):
        Entity.__init__(self, name, examine_desc, desc)
        self.dialogueList = {}

    def add_dialogue(self, chat: Dialogue):
        self.dialogueList[chat.get_topic()] = chat
        pass

    # todo: move to Display class instead of in entity class
    def get_topics(self, keys):
        return_string = ""
        for chatKey, chatEntry in self.dialogueList.items():
            if chatEntry.check_allowed(keys):
                return_string += chatEntry.get_topic() + "\n"
        if return_string == "":
            return "They don't want to talk"
        return_string = "Topics:\n" + return_string
        return return_string

    def get_topics_list(self, keys):
        return {k: v for k, v in self.dialogueList.items() if v.check_allowed(keys)}

    def check_topic(self, topic, keys):
        if topic in self.dialogueList:
            return self.dialogueList[topic].check_allowed(keys)
        return False

    def speak_topic(self, topic, player):
        if topic in self.dialogueList:
            return self.dialogueList[topic].activate(player)
        return ""

    def give_dialogue_keys(self, topic):
        if topic in self.dialogueList:
            return self.dialogueList[topic].get_keys()
