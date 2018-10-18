from typing import List


class Event:
    whitelistKeys: List[str]
    blacklistKeys: List[str]
    giveKeys: List[str]
    takeKeys: List[str]
    eventType: str
    makeVisible: []
    makeInvisible: []

    def __init__(self, whitelist, blacklist, key, unkey, event_text, event_type):
        self.whitelistKeys = whitelist
        self.blacklistKeys = blacklist
        self.giveKeys = key
        self.takeKeys = unkey
        self.eventText = event_text
        self.eventType = event_type
        self.makeVisible = []
        self.makeInvisible = []

    def activate(self, agent):
        location = agent.get_location()
        for ref in self.makeVisible:
            name = ref[0]
            class_type = ref[1]
            if class_type == "actor":
                location.get_actor(name).show()
            if class_type == "item":
                location.get_item(name).show()
        for ref in self.makeInvisible:
            name = ref[0]
            class_type = ref[1]
            if class_type == "actor":
                location.get_actor(name).hide()
            if class_type == "item":
                location.get_item(name).hide()

        for key in self.giveKeys:
            agent.add_key(key)
        for key in self.takeKeys:
            agent.remove_key(key)

        return self.eventText

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
        return self.eventType

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

# todo: dialogue extends event?
