from __future__ import annotations
from typing import List, Dict

from entity import *
from event import *


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

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, index: int):
        return self.items.pop(index)

    def get_items_index(self, item_name: str) -> int:
        for i in range(len(self.items)):
            if self.items[i].name == item_name:
                return i

    def get_item_ref(self, index):
        return self.items[index]

    def get_item_list(self):
        return self.items

    def get_actors_list(self):
        return self.actors

    def get_desc(self):
        return self.description

    def get_links_desc(self):
        if len(self.links) == 0:
            return "you are stuck here\n"
        return_string: str = BColors.OKGREEN + "There are exits: \n" + BColors.ENDC
        for place in self.links:
            return_string += "\tto the "
            return_string += place.get_direction() + ", "
            return_string += place.get_location().get_name()
            return_string += "\n"
        return return_string

    def get_item_desc(self):
        item_count = 0
        return_string = BColors.OKGREEN + "Around you you see: \n" + BColors.ENDC
        for item in self.items:
            if not item.get_visible():
                continue
            return_string += "\t"
            return_string += item.get_desc()
            return_string += "\n"
            item_count += 1
        if item_count == 0:
            return BColors.OKGREEN + "There is nothing of interest around you\n" + BColors.ENDC
        return return_string

    def get_actor_desc(self):
        actor_count = 0
        return_string = ""
        for actor in self.actors:
            if not actor.get_visible():
                continue
            return_string += "\t"
            return_string += actor.get_name() + ": "
            return_string += actor.get_desc()
            return_string += "\n"
            actor_count += 1

        if actor_count == 0:
            return BColors.OKGREEN + "You are alone\n" + BColors.ENDC
        if actor_count == 1:
            return_string = BColors.OKGREEN + "There is someone here: \n" + BColors.ENDC + return_string
        else:
            return_string = BColors.OKGREEN + "There are people here: \n" + BColors.ENDC + return_string
        return return_string

    def add_link(self, location, direction):
        self.links.append(Link(location, direction))

    def add_actor(self, person):
        self.actors.append(person)

    def get_actor(self, actor_name):
        for actor in self.actors:
            if actor.get_name() == actor_name and actor.get_visible():
                return actor
        return None

    def get_item(self, item_name):
        for item in self.items:
            if item.get_name() == item_name:
                return item
        return None

    def add_event(self, event):
        self.events.append(event)

    def get_events(self):
        return self.events

    def get_links(self):
        return self.links

    def get_items(self):
        return self.items

    def get_name(self):
        return self.name


class Player:
    location: Room
    inventory: List[Item]
    conditions: List[str]
    keyList: List[str]

    def __init__(self, start_location, starting_keys):
        self.location = start_location
        self.inventory: List[Item] = []
        self.conditions: List[str] = []
        self.keyList = starting_keys

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

    def remove_from_inventory(self, index):
        return self.inventory.pop(index)

    def add_key(self, key):
        if key not in self.keyList:
            self.keyList.append(key)
            return len(self.keyList)
        return None

    def remove_key(self, key):
        if key in self.keyList:
            self.keyList.remove(key)
            return len(self.keyList)
        return None

    def get_keys(self):
        return self.keyList

    def display_inventory(self):
        return_string = BColors.OKGREEN + "You have on you: \n" + BColors.ENDC
        if len(self.inventory) == 0:
            return "you feel sad, for there is nothing in your pockets. "
        for thing in self.inventory:
            return_string += thing.get_inv_desc()
            return_string += "\n"
        return return_string

    def move(self, direction):
        links = self.location.get_links()
        for place in links:
            if place.get_direction() == direction:
                self.location = place.get_location()
                return self.look_around()
        return None

    def get_actor(self, actor_name):
        return self.location.get_actor(actor_name)

    def talk(self, actor, topic):
        if not actor.check_topic(topic, self.get_keys()):
            return actor.get_name() + " does not know about this."
        return_string = actor.get_name() + ": " + actor.speak_topic(topic)
        give_keys, take_keys = actor.give_dialogue_keys(topic)
        for key in give_keys:
            self.add_key(key)
        for key in take_keys:
            self.remove_key(key)

        return return_string

    def look_around(self):
        return_string = ""
        return_string += self.get_location().get_desc() + "\n\n"
        return_string += self.get_location().get_links_desc() + "\n"
        return_string += self.get_location().get_actor_desc() + "\n"
        return_string += self.get_location().get_item_desc()

        return return_string


class Link:
    # room
    direction: str
    location: Room

    def __init__(self, location, direction):
        self.location = location
        self.direction = direction

    def get_room_name(self):
        return self.location.get_name()

    def get_location(self):
        return self.location

    def get_direction(self):
        return self.direction