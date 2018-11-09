from __future__ import annotations
# noinspection PyUnresolvedReferences
from typing import List
from base import *


class Event:
    whitelistKeys: List[str]
    blacklistKeys: List[str]
    giveKeys: List[str]
    takeKeys: List[str]
    type: str
    makeVisible: []
    makeInvisible: []

    def __init__(self, whitelist, blacklist, key, unkey, event_text, event_type):
        self.whitelistKeys = whitelist
        self.blacklistKeys = blacklist
        self.giveKeys = key
        self.takeKeys = unkey
        self.text = event_text
        self.type = event_type
        self.makeVisible = []
        self.makeInvisible = []

    def activate(self, player):
        location: Room = player.get_location()
        for ref in self.makeVisible:
            name = ref[0]
            class_type = ref[1]
            if class_type == "actor":
                if location.get_actor(name):
                    location.get_actor(name).show()
            if class_type == "item":
                if location.get_item(name):
                    location.get_item(name).show()
            if class_type == "link":
                for link in location.get_all_links():
                    if link.get_room_name() == name:
                        link.show()
        for ref in self.makeInvisible:
            name = ref[0]
            class_type = ref[1]
            if class_type == "actor":
                if location.get_actor_visible(name):
                    location.get_actor_visible(name).hide()
            if class_type == "item":
                if location.get_item(name):
                    location.get_item(name).hide()
            if class_type == "link":
                link = next(filter(lambda x: x.get_room_name() == name, location.get_links()))
                if link:
                    link.hide()

        for key in self.giveKeys:
            player.add_key(key)
        for key in self.takeKeys:
            player.remove_key(key)

        return self.text

    def check_allowed(self, keys):
        if len(self.whitelistKeys) != 0:
            for key in self.whitelistKeys:
                if key not in keys:
                    return False
        if len(self.blacklistKeys) != 0:
            for key in keys:
                if key in self.blacklistKeys:
                    return False
        return True

    def get_type(self):
        return self.type

    def get_keys(self):
        return self.giveKeys, self.takeKeys

    def add_show(self, visibility_list):
        self.makeVisible.append(visibility_list)

    def add_hide(self, visibility_list):
        self.makeInvisible.append(visibility_list)

    def get_make_visible(self):
        return self.makeVisible

    def get_make_invisible(self):
        return self.makeInvisible


class Dialogue(Event):
    def __init__(self, whitelist, blacklist, key, unkey, text, topic):
        Event.__init__(self, whitelist, blacklist, key, unkey, text, topic)

    def get_topic(self):
        return self.type

    def activate(self, player):
        for key in self.giveKeys:
            player.add_key(key)
        for key in self.takeKeys:
            player.remove_key(key)
        return self.text
