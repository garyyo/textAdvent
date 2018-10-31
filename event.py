from __future__ import annotations
from typing import List


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

    def activate(self, agent):
        location = agent.get_location()
        for ref in self.makeVisible:
            name = ref[0]
            class_type = ref[1]
            if class_type == "actor":
                if location.get_actor(name):
                    location.get_actor(name).show()
            if class_type == "item":
                if location.get_item(name):
                    location.get_item(name).show()
        for ref in self.makeInvisible:
            name = ref[0]
            class_type = ref[1]
            if class_type == "actor":
                if location.get_actor(name):
                    location.get_actor(name).hide()
            if class_type == "item":
                if location.get_item(name):
                    location.get_item(name).hide()
            if class_type == "link":
                link = filter(lambda x: x.get_room_name() == name,location.get_links())[0]
                if link:
                    link.hide()

        for key in self.giveKeys:
            agent.add_key(key)
        for key in self.takeKeys:
            agent.remove_key(key)

        return self.text

    def check_allowed(self, keys):
        if self.whitelistKeys:
            for key in self.whitelistKeys:
                if key not in keys:
                    return False
        if self.blacklistKeys:
            for key in keys:
                if key in self.blacklistKeys:
                    return False
        return True

    def get_type(self):
        return self.type

    def get_keys(self):
        return self.giveKeys, self.takeKeys

    def add_make_visible(self, visibility_list):
        self.makeVisible.append(visibility_list)

    def add_make_invisible(self, visibility_list):
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

    def activate(self, player=None):
        return self.text
