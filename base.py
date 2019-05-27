from __future__ import annotations
# from typing import List, Dict

from entity import *


class Room:
    links = List['Link']
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
    #     todo: does room need its own keyring?

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

    def get_items_visible(self):
        return list(filter(lambda x: x.get_visible(), self.items))

    def get_actors_visible(self):
        return list(filter(lambda x: x.get_visible(), self.actors))

    def get_actors(self):
        return self.actors

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

    def get_actor_when_visible(self, actor_name):
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
            if key in self.keyring:
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

    def get_links(self) -> List[Link]:
        return list(filter(lambda x: x.get_visible(), self.links))

    def get_all_links(self):
        return self.links

    def get_items(self):
        return self.items

    def get_name(self):
        return self.name


class Player:
    current_room: Room
    inventory: List[Item]
    conditions: List[str]
    keyring: List[str]
    added_keys: List[str]
    removed_keys: List[str]
    gold: int
    map: str

    def __init__(self, start_location: Room, starting_keys, map_chart="you have no map"):
        self.current_room = start_location
        self.inventory = []
        self.conditions = []
        self.keyring = starting_keys
        self.added_keys = []
        self.removed_keys = []
        self.gold = 0
        self.map = map_chart

    def get_current_room(self) -> Room:
        return self.current_room

    # get the index of an item in the players inventory, or None if it doesnt exist
    # todo: all index tracking should be handled inside
    def get_inventory_index(self, item_name: str) -> int:
        for i in range(len(self.inventory)):
            if self.inventory[i].name.lower() == item_name.lower():
                return i

    def get_inventory_item_ref(self, item_name):
        index = get_inventory_index(item_name)
        return

        pass

    def get_inventory(self):
        return self.inventory

    # use for DM mostly
    def get_available_actions(self):
        available_actions = []
        # can the player move
        # if len(self.current_room.get_links()) > 0:
        #     available_actions.append("move")

        for actor in self.current_room.get_actors_visible():
            # can the player speak to someone
            if len(actor.get_topics_list(self.keyring)):
                if "talk" not in available_actions:
                    available_actions.append("talk")
            if len(actor.get_events_type("onExamine")):
                if "look" not in available_actions:
                    available_actions.append("look")

        # can the player pick something up, (or have something in their inventory??)?
        for item in self.current_room.get_items_visible():
            if len(item.get_events_type("onPickup")) > 0:
                available_actions.append("pickup")
            if len(item.get_events_type("onExamine")):
                if "look" not in available_actions:
                    available_actions.append("look")
            if len(item.get_events_type("onUse")):
                if "use" not in available_actions:
                    available_actions.append("use")
        # can the player examine a thing?
        # can the player interact with stuff?

        # if there is a distraction, then add the type of that distraction to the available actions list
        for item in self.current_room.get_items_visible():
            if item.get_distractor():
                if item.distraction_type not in available_actions:
                    available_actions.append(item.distraction_type)

        return available_actions

    # remove from room, add to inventory
    # todo: move outside of player. this is an action
    def pickup(self, item_name):
        # find item in room
        item_index = self.current_room.get_items_index(item_name)

        item = None

        # if item is in current location, remove from room, add to inventory
        if item_index is not None:
            item = self.current_room.get_item_ref(item_index)
            if not item.get_pickupable():
                return None

            self.current_room.remove_item(item_index)
            self.add_to_inventory(item)
            # todo: deprecate
            self.add_key(item.get_pickup_key())

        # return item
        return item

    # return index of item removed, None if item not there
    def drop(self, item_name):
        item_index = self.get_inventory_index(item_name)
        item = None
        if item_index is not None:
            item = self.remove_from_inventory(item_index)
            # self.location.add_item(item)
            # todo: is this line needed?
            # self.add_key(item.get_pickup_key())
            self.remove_key(item.get_pickup_key())
        return item

    def add_to_inventory(self, item_ref):
        # append item to inventory list
        self.inventory.append(item_ref)
        pass

    def remove_from_inventory(self, index):
        return self.inventory.pop(index)

    def add_gold(self, gold):
        self.gold += gold

    def remove_gold(self, gold):
        self.gold -= gold

    def get_gold(self):
        return self.gold

    def update_keyring(self):
        for key in self.added_keys:
            self.keyring.append(key)
        self.added_keys = []
        for key in self.removed_keys:
            if key in self.keyring:
                self.keyring.remove(key)
        self.removed_keys = []

    def get_keys(self):
        return self.keyring

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

    def has_keys(self, keys):
        print(self.keyring, type(self.keyring), keys, type(keys))
        return set(self.keyring).issubset(keys)

    # update location
    # todo: should this be moved outside because it represents an action, or stay because its updating internal stuff?
    def move(self, direction):
        links = self.current_room.get_links()
        for place in links:
            if place.get_direction() == direction:
                self.current_room = place.get_room()
                return True
        return None

    # gives player keys from actor talk event
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

    def get_room(self):
        return self.location

    def get_direction(self):
        return self.direction
