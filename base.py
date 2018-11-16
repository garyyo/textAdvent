from __future__ import annotations
# from typing import List, Dict

from entity import *


class Room:
    links = []
    items: List[Item]
    actors: List[Actor]
    events: List[Event]
    name: str
    init_desc: str
    description: str

    def __init__(self, name: str, description: str, init_desc: str):
        self.name = name
        self.description = description
        self.init_desc = init_desc
        self.links = []
        self.items = []
        self.actors = []
        self.events = []
        self.added_keys = []
        self.removed_keys = []
        self.keyring = []

    def add_item(self, item):
        if item:
            self.items.append(item)

    def remove_item(self, index: int):
        return self.items.pop(index)

    def get_items_index(self, item_name: str) -> int:
        for i in range(len(self.items)):
            if self.items[i].get_name().lower() == item_name.lower():
                return i

    def get_item_ref(self, index):
        return self.items[index]

    def get_item_list(self):
        return list(filter(lambda x: x.get_visible(), self.items))

    def get_actors_list(self):
        return list(filter(lambda x: x.get_visible(), self.actors))

    def get_desc(self):
        return self.description

    def add_link(self, location, direction, hidden):
        self.links.append(Link(location, direction, hidden))

    def add_actor(self, actor):
        if actor:
            self.actors.append(actor)

    def get_actor(self, actor_name):
        for actor in self.actors:
            if actor.get_name().lower() == actor_name.lower():
                return actor
        return None

    def get_actor_visible(self, actor_name):
        for actor in self.actors:
            if actor.get_name().lower() == actor_name.lower() and actor.get_visible():
                return actor
        return None

    def get_item(self, item_name):
        for item in self.items:
            if item.get_name().lower() == item_name.lower():
                return item
        return None

    def add_event(self, event):
        if event:
            self.events.append(event)

    def get_events(self):
        return self.events

    def update_keyring(self):
        for key in self.added_keys:
            self.keyring.append(key)
        self.added_keys = []
        for key in self.removed_keys:
            self.keyring.remove(key)
        self.removed_keys = []

    def add_key(self, key):
        if key not in self.keyring:
            self.added_keys.append(key)
            return len(self.keyring)
        return None

    def remove_key(self, key):
        if key in self.keyring:
            self.removed_keys.append(key)
            return len(self.keyring)
        return None

    def get_links(self):
        return list(filter(lambda x: x.get_visible(), self.links))

    def get_all_links(self):
        return self.links

    def get_items(self):
        return self.items

    def get_name(self):
        return self.name


class Player:
    location: Room
    inventory: List[Item]
    conditions: List[str]
    keyring: List[str]
    added_keys: List[str]
    removed_keys: List[str]
    gold: int

    def __init__(self, start_location: Room, starting_keys):
        self.location = start_location
        self.inventory = []
        self.conditions = []
        self.keyring = starting_keys
        self.added_keys = []
        self.removed_keys = []
        self.gold = 0

    def get_location(self):
        return self.location

    # get the index of an item in the players inventory, or None if it doesnt exist
    def get_inventory_index(self, item_name: str) -> int:
        for i in range(len(self.inventory)):
            if self.inventory[i].name == item_name:
                return i

    def get_inventory(self):
        return self.inventory

    # returns 1 if success, None if failure
    def pickup(self, item_name):
        # find item in room
        item_index = self.location.get_items_index(item_name)

        # if item is in current location, remove from room, add to inventory
        if item_index is not None:

            item = self.location.get_item_ref(item_index)
            if not item.get_pickupable():
                return None

            self.location.remove_item(item_index)
            self.add_to_inventory(item)
            self.add_key(item.get_pickup_key())

        # return item
        return item_index

    # return index of item removed, None if item not there
    def drop(self, item_name):
        item_index = self.get_inventory_index(item_name)
        if item_index is not None:
            item = self.remove_from_inventory(item_index)
            self.location.add_item(item)
        return item_index

    def add_to_inventory(self, thing):
        # append item to inventory list
        self.inventory.append(thing)
        pass

    def add_gold(self, gold):
        self.gold += gold

    def remove_gold(self, gold):
        self.gold -= gold

    def get_gold(self):
        return self.gold

    def remove_from_inventory(self, index):
        return self.inventory.pop(index)

    def update_keyring(self):
        for key in self.added_keys:
            self.keyring.append(key)
        self.added_keys = []
        for key in self.removed_keys:
            self.keyring.remove(key)
        self.removed_keys = []

    def add_key(self, key):
        if key not in self.keyring:
            self.added_keys.append(key)
            return len(self.keyring)
        return None

    def remove_key(self, key):
        if key in self.keyring:
            self.removed_keys.append(key)
            return len(self.keyring)
        return None

    def get_keys(self):
        return self.keyring

    def move(self, direction):
        links = self.location.get_links()
        for place in links:
            if place.get_direction() == direction:
                self.location = place.get_location()
                return True
        return None

    def talk(self, actor, topic):
        if not actor.check_topic(topic, self.get_keys()):
            return
        give_keys, take_keys = actor.give_dialogue_keys(topic)
        for key in give_keys:
            self.add_key(key)
        for key in take_keys:
            self.remove_key(key)


class Link:
    # room
    direction: str
    location: Room
    visible: bool

    def __init__(self, location, direction, visible):
        self.location = location
        self.direction = direction
        self.visible = not visible

    def get_visible(self):
        return self.visible

    def set_visible(self, visibility):
        self.visible = visibility

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def get_room_name(self):
        return self.location.get_name()

    def get_location(self):
        return self.location

    def get_direction(self):
        return self.direction
