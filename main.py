from __future__ import annotations

import copy
import json
import math

from base import *
from entity import *
from event import *
from typing import List, Dict


# https://stackoverflow.com/questions/287871/print-in-terminal-with-colors
class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Parser:
    words = {
        "article": ["a", "an", "the"],
        "preposition": ["of", "in", "to", "for", "with", "on", "at", "from", "by", "about", "as",
                        "into", "like", "through", "after", "over", "between", "out", "against",
                        "during", "without", "before", "under", "around", "among"],
        "intensifier": ["fucking"]
    }
    verbs = {
        "pickup": ["pickup", "grab", "get", "take", "pick"],
        "drop": ["drop", "place", "put"],
        "move": ["go", "move", "walk", "run"],
        "direction": ["north", "south", "east", "west", "up", "down", "left", "right",
                      "n", "s", "e", "w", "u", "d", "l", "r"],
        "look": ["look", "examine", "search"],
        "use": ["use", "touch"],
        "talk": ["talk", "speak", "t"],
        "inventory": ["inv", "inventory"],
        "key": ["key", "k"],
        "map": ["map"]
    }
    player: Player

    commandList: List[str]

    def __init__(self, player):
        self.player = player
        self.commandList = []

    def split_commands(self, command_str):
        self.commandList = command_str.split(" ") + ["", "", "", ""]
        if (self.commandList[0] == "pick" and self.commandList[1] == "up") \
                or (self.commandList[0] == "drop" and self.commandList[1] == "down") \
                or (self.commandList[0] == "put" and self.commandList[1] == "down"):
            self.commandList[0:2] = [''.join(self.commandList[0:2])]

    def parse_commands(self, command_str):
        self.split_commands(command_str)
        self.strip_commands()
        verb = self.identify_verb().lower()
        direct_object = self.identify_object(verb).lower()
        self.commandList[0] = verb
        self.commandList[1] = direct_object
        return self.commandList

    def identify_verb(self):
        # look at first word, see if it matches any of the known verbs
        verb = self.commandList[0]
        best_verb = ""
        for key, testVerbs in self.verbs.items():
            if verb in testVerbs:
                best_verb = key
                if best_verb == "direction":
                    best_verb = "move"
                    self.commandList.insert(0, "")
                break
        return best_verb

    def identify_object(self, verb):
        direct_object = self.commandList[1]
        # based on verb do different things
        if verb == "move":
            if direct_object == "n":
                direct_object = "north"
            if direct_object == "s":
                direct_object = "south"
            if direct_object == "e":
                direct_object = "east"
            if direct_object == "w":
                direct_object = "west"
            if direct_object == "u":
                direct_object = "up"
            if direct_object == "d":
                direct_object = "down"

        # if player misspelled actor name
        if verb == "talk" and direct_object:
            actor = self.player.get_location().get_actor_visible(direct_object)
            topic = " ".join(filter(lambda x: len(x) > 0, self.commandList[2:]))
            if actor is None:
                direct_object = self.sp_entity_name(direct_object, self.player.get_location().get_actors_list(), 0.7)
                actor = self.player.get_location().get_actor_visible(direct_object)
            if actor and not actor.check_topic(topic, self.player.get_keys()):
                topic = self.sp_event_name(topic, actor.get_topics_list(self.player.get_keys()), .4)
            self.commandList[2] = topic
        if verb == "move":
            direct_object = self.sp_link_name(direct_object, self.player.get_location().get_links(), 0.7)
        if verb in ["pickup"]:
            direct_object = self.sp_entity_name(direct_object, self.player.get_location().get_item_list(), 0.7)
        if verb in ["look"]:
            direct_object = self.sp_entity_name(direct_object, self.player.get_location().get_item_list() +
                                                self.player.get_location().get_actors_list(), 0.7)
        if verb in ["use"]:
            direct_object = self.sp_entity_name(
                direct_object,
                self.player.get_location().get_item_list() + self.player.get_inventory(),
                0.7)
        if verb in ["drop"]:
            direct_object = self.sp_entity_name(direct_object, self.player.get_inventory(), 0.7)
        return direct_object

    def collect_entity_list(self):
        # get entities in location
        location = self.player.get_location()
        entity_list = location.get_item_list()
        entity_list += location.get_actors_list()

        # get items in player inventory
        entity_list += self.player.get_inventory()

        pass

    def collect_entities_from_entity(self, entity):
        return_list = [entity]
        inventory_list = entity.get_inventory()
        for inventoryItem in inventory_list:
            return_list += self.collect_entities_from_entity(inventoryItem)
        return return_list

    @staticmethod
    def sp_entity_name(word, entity_list: List[Entity], threshold):
        # find closest actor name
        if not word:
            return ""
        correct_list = {}
        for entity in entity_list:
            if not entity.get_visible():
                continue;
            entity_name = entity.get_name()
            character_length = min(len(entity_name), len(word))
            counter = 0
            for i in range(character_length):
                counter += 1 if entity_name.lower()[i] == word.lower()[i] else 0
                correct_list[entity_name] = counter / character_length
        if not correct_list:
            return word
        key = max(correct_list, key=lambda x: correct_list[x])
        if correct_list[key] > threshold:
            word = key
        return word

    @staticmethod
    def sp_link_name(word, link_list: List[Link], threshold):
        # find closest actor name
        if not word:
            return ""
        correct_list = {}
        for link in link_list:
            link_name = link.get_direction()
            character_length = min(len(link_name), len(word))
            counter = 0
            for i in range(character_length):
                counter += 1 if link_name.lower()[i] == word.lower()[i] else 0
                correct_list[link_name] = counter / character_length
        if not correct_list:
            return word
        key = max(correct_list, key=lambda x: correct_list[x])
        if correct_list[key] > threshold:
            word = key
        return word

    # these are for dialogues but events might be extended to include something else so keeping the name event for now
    @staticmethod
    def sp_event_name(word, event_list, threshold):
        # find closest actor name
        if not word:
            return ""
        correct_list = {}

        for event_name in event_list:
            character_length = min(len(event_name), len(word))
            counter = 0
            for i in range(character_length):
                counter += 1 if event_name.lower()[i] == word.lower()[i] else 0
                correct_list[event_name] = counter / character_length
        if not correct_list:
            return word
        key = max(correct_list, key=lambda x: correct_list[x])
        if correct_list[key] > threshold:
            word = key
        return word

    # strip commandList of unnecessary words?
    def strip_commands(self):
        counter = 0
        while counter < len(self.commandList):
            word = self.commandList[counter]
            if word in self.words["article"]:
                self.commandList.remove(word)
                continue
            elif word in self.words["preposition"]:
                self.commandList.remove(word)
                continue
            elif word in self.words["intensifier"]:
                self.commandList.remove(word)
                continue
            counter += 1


class ScenarioBuilder:
    scenarioList: List[Scenario]
    playerModel: List[float]
    currentScene: Scenario

    def __init__(self):
        self.scenarioList = []
        # self.playerModel = [0.51087279, 0.22050487, 0.4063116, 0.713533420, 0.08517401]
        self.playerModel = [0, 0, 0, 0, 0]
        self.build_scenarios(["boring.json"])
        pass

    def build_scenarios(self, file_list):
        for file in file_list:
            self.scenarioList.append(Scenario(file))

    def get_scenario(self):
        self.currentScene = self.choose_scenario()
        return self.currentScene

    def choose_scenario(self):
        if len(self.scenarioList) == 0:
            return None
        scene = min(self.scenarioList, key=lambda x: abs(sum(x.get_weights()) - sum(self.playerModel)))
        # todo: re-enable when we have more scenes
        # self.scenarioList.remove(scene)
        return scene

    def keys_from_model(self):
        if self.player_status():
            return ["bored"], []
        return [], ["bored"]

    def player_status(self):
        # when the player model gets too far away from the current, offer a new quest
        best_scene = self.choose_scenario()
        if best_scene == self.currentScene:
            # print("~~~everything is fine~~~")
            return False
        else:
            return True

    def update_model(self, command_array):
        action = command_array[0]
        if action == "look" or action == "use":
            self.playerModel[0] = (self.playerModel[0] * 2 + 1) / 3
            self.playerModel[1] = (self.playerModel[1] * 2 + 1) / 3
            self.playerModel[2] = (self.playerModel[2] * 2 + 1) / 3
            self.playerModel[3] = (self.playerModel[3] * 2 + 1) / 3
            self.playerModel[4] = (self.playerModel[4] * 2 + 1) / 3

    def reset_model(self):
        self.playerModel = [0, 0, 0, 0, 0]

    def print_model(self):
        print(self.playerModel)


class Scenario:
    roomList: Dict[str, Room]
    eventList: List
    actorList: List
    itemList: List
    start_location: str
    jsonData: Dict

    def __init__(self, file_name="example.json"):
        with open(file_name) as f:
            self.jsonData = json.load(f)
        self.roomList = {}
        self.actorList = []
        self.itemList = []
        self.eventList = []
        self.start_location = "template"

        self.room_compile()
        self.link_builder()

    def room_compile(self):
        for room_json in self.jsonData["rooms"]:
            name = room_json["name"]
            if "startLocation" in room_json:
                self.start_location = name
            new_room = Room(
                name,
                room_json["desc"] if "desc" in room_json else "",
                room_json["examineDesc"] if "examineDesc" in room_json else ""
            )

            if "items" in room_json:
                for itemJSON in room_json["items"]:
                    new_room.add_item(self.item_create(itemJSON))
            if "backgrounds" in room_json:
                for itemJSON in room_json["backgrounds"]:
                    new_room.add_item(self.item_create(itemJSON))
            if "actors" in room_json:
                for actorJSON in room_json["actors"]:
                    new_room.add_actor(self.actor_create(actorJSON))
            if "events" in room_json:
                for eventJSON in room_json["events"]:
                    new_room.add_event(self.event_create(eventJSON))

            self.roomList[name] = new_room

    def link_builder(self):
        for room_json in self.jsonData["rooms"]:
            if "links" in room_json:
                linking_room = self.roomList[room_json["name"]]
                for linkJSON in room_json["links"]:
                    linking_room.add_link(self.roomList[linkJSON["roomName"]] if "roomName" in linkJSON else "template",
                                          linkJSON["direction"] if "direction" in linkJSON else "up",
                                          linkJSON["hidden"] if "hidden" in linkJSON else False)

    def actor_create(self, actor_json):
        new_actor = Actor(
            actor_json["name"] if "name" in actor_json else "",
            actor_json["examine"] if "examine" in actor_json else "",
            actor_json["desc"] if "desc" in actor_json else ""
        )
        if new_actor.get_name() in ["template", ""]:
            return None

        if "hidden" in actor_json:
            new_actor.hide()

        if "dialogues" in actor_json:
            for dialogueJSON in actor_json["dialogues"]:
                new_dialogue = Dialogue(dialogueJSON["whitelist"] if "whitelist" in dialogueJSON else "",
                                        dialogueJSON["blacklist"] if "blacklist" in dialogueJSON else "",
                                        dialogueJSON["key"] if "key" in dialogueJSON else "",
                                        dialogueJSON["unkey"] if "unkey" in dialogueJSON else "",
                                        dialogueJSON["keyRoom"] if "keyRoom" in dialogueJSON else [""],
                                        dialogueJSON["unkeyRoom"] if "unkeyRoom" in dialogueJSON else [""],
                                        dialogueJSON["text"] if "text" in dialogueJSON else "they stay silent",
                                        dialogueJSON["topic"] if "topic" in dialogueJSON else "")

                # get rid of empty entries.
                for i in range(len(new_dialogue.whitelistKeys)):
                    if new_dialogue.whitelistKeys[i] == "":
                        new_dialogue.whitelistKeys.pop(i)
                for i in range(len(new_dialogue.blacklistKeys)):
                    if new_dialogue.blacklistKeys[i] == "":
                        new_dialogue.blacklistKeys.pop(i)

                new_actor.add_dialogue(new_dialogue)

        self.actorList.append(new_actor)
        return new_actor

    def item_create(self, item_json):
        new_item = Item(
            item_json["name"] if "name" in item_json else "",
            item_json["examine"] if "examine" in item_json else "",
            item_json["invDesc"] if "invDesc" in item_json else "",
            item_json["desc"] if "desc" in item_json else "",
            item_json["weight"] if "weight" in item_json else 0.0,
            item_json["smell"] if "smell" in item_json else "",
            item_json["taste"] if "taste" in item_json else "",
            item_json["size"] if "size" in item_json else "",
            item_json["pickupable"] if "pickupable" in item_json else False,
            item_json["pickupKey"] if "pickupKey" in item_json else ""
        )

        # get rid of templates
        if new_item.get_name() in ["template", ""]:
            return None

        if "events" in item_json:
            for eventJSON in item_json["events"]:
                new_item.add_event(self.event_create(eventJSON))

        if "hidden" in item_json:
            new_item.hide()

        self.itemList.append(new_item)
        return new_item

    def background_create(self, item_json):
        new_item = Background(
            item_json["name"] if "name" in item_json else "",
            item_json["examine"] if "examine" in item_json else "",
            item_json["invDesc"] if "invDesc" in item_json else "",
            item_json["desc"] if "desc" in item_json else "",
            item_json["weight"] if "weight" in item_json else 0.0,
            item_json["smell"] if "smell" in item_json else "",
            item_json["taste"] if "taste" in item_json else "",
            item_json["size"] if "size" in item_json else "",
        )

        # get rid of templates
        if new_item.get_name() in ["template", ""]:
            return None

        if "hidden" in item_json:
            new_item.hide()

        self.itemList.append(new_item)
        return new_item

    def event_create(self, event_json):
        new_event = Event(
            event_json["whitelist"] if "whitelist" in event_json else "",
            event_json["blacklist"] if "blacklist" in event_json else "",
            event_json["key"] if "key" in event_json else [""],
            event_json["unkey"] if "unkey" in event_json else [""],
            event_json["keyRoom"] if "keyRoom" in event_json else [""],
            event_json["unkeyRoom"] if "unkeyRoom" in event_json else [""],
            event_json["text"] if "text" in event_json else "",
            event_json["type"] if "type" in event_json else ""
        )

        # todo: instead of finding things by name later, find them now and store reference instead of name.
        if "show" in event_json:
            for visibleJSON in event_json["show"]:

                new_event.add_show([
                    visibleJSON["name"] if "name" in visibleJSON else "",
                    visibleJSON["class"] if "class" in visibleJSON else ""
                ])
        if "hide" in event_json:
            for visibleJSON in event_json["hide"]:
                new_event.add_hide([
                    visibleJSON["name"] if "name" in visibleJSON else "",
                    visibleJSON["class"] if "class" in visibleJSON else ""
                ])

        # remove blank keys
        for i in range(len(new_event.whitelistKeys)):
            if new_event.whitelistKeys[i] == "":
                new_event.whitelistKeys.pop(i)
        for i in range(len(new_event.blacklistKeys)):
            if new_event.blacklistKeys[i] == "":
                new_event.blacklistKeys.pop(i)

        self.eventList.append(new_event)
        return new_event

    def get_weights(self):
        return self.jsonData["weights"] if "weights" in self.jsonData else [0, 0, 0, 0, 0]

    def get_player(self):
        starting_keys = self.jsonData["startingKeys"] if "startingKeys" in self.jsonData else []
        player = Player(self.roomList[self.start_location], starting_keys)
        player.add_gold(self.jsonData["initialGold"] if "initialGold" in self.jsonData else 0)
        return player


class Display:
    player: Player
    display_width = 150
    print_list: List[List[str]]

    # pass in arbitrary objects and get proper formatting for their description.
    def __init__(self, player):
        self.player = player
        self.print_list = []

    def add_print_list(self, print_list):
        self.print_list.append(print_list)

    def print(self):
        for print_list in self.print_list:
            for line in print_list:
                while len(line) > 0:
                    print_line, line = self.break_text(line)
                    print(print_line)
                # print(line)
            # print()
        self.print_list = []

    def display_room(self):
        self.current_area()
        self.link_list()
        self.actor_list()
        self.item_list()

    # todo replace with different functions for each functionality
    # im already doing this pretty much, but when i want to reject a message i use this? put rejections in the others
    def confirm_command(self, text: str, status: bool = True, command: str = None, args: List[str] = None):
        # todo: figure out what to do here. do i even need this?
        print()
        # if status is false
        #   print in red because an action failed
        if not status:
            print(self.color_text(text, "red"))
            print()
            return

        # types interpreted from command???: multiline, confirmation,
        # command and args are only to be used in very specific cases, like topic listing.
        # i still want everything to be routed through this function.

        pass

    # todo use reject instead of else statements because i said so
    def reject(self, text):
        self.add_print_list([self.color_text(text, "red")])

    def look(self, entity: Entity):
        if entity is not None:
            self.add_print_list(
                [
                    self.color_text("you examine the " + entity.get_name() + " closely", "bold"),
                    "\t" + entity.get_examine()
                ]
            )
        else:
            self.reject("You look, you look but you cannot find that.")

    def talk(self, actor, topic, accept=True):
        if accept:
            if not actor.check_topic(topic, self.player.get_keys()):
                self.add_print_list([actor.get_name() + " does not know about this topic."])
                return
            self.add_print_list([self.color_text(actor.get_name(), "blue") + " starts to respond:"])
            self.add_print_list(["\t" + actor.speak_topic(topic, self.player)])
        else:
            self.add_print_list([self.color_text("you talk into the aether to someone who isn't there", "red")])

    def inventory(self):
        margin_width = 8
        print_list = []

        gold_text = " gold: " + str(self.player.get_gold())
        gold_text_length = len(gold_text)

        if self.player.get_inventory():
            max_item = max(self.player.get_inventory(), key=lambda x: len(x.get_inv_desc())+len(x.get_name()))
            inventory_width = margin_width + len(max_item.get_inv_desc()) + len(max(max_item.get_name()))
            inventory_width = min(inventory_width,self.display_width + margin_width)
        else:
            inventory_width = gold_text_length+1

        gold_text_spaced = gold_text + (math.floor((inventory_width - gold_text_length)) * " ")

        print_list.append("=" + ("-" * int(inventory_width)) + "=")
        print_list.append("|" + gold_text_spaced + "|")
        print_list.append("|" + (" " * int(inventory_width)) + "|")

        item_num = 0
        for item in self.player.get_inventory():
            line = item.get_inv_desc()
            item_num += 1
            first_time = True
            while len(line) > 0:
                # 8 is a magic number of just counting up all the characters in front and behind print_line
                print_line, line = self.break_text(line, inventory_width)
                if not first_time:
                    d = "    " + print_line
                else:
                    d = " " + item.get_name() + ": " + print_line
                    first_time = False
                d_length = len(d)
                d_spaced = d + (math.floor((inventory_width - d_length)) * " ")
                print_list.append("|" + d_spaced + "|")

        print_list.append("|" + (" " * inventory_width) + "|")
        print_list.append("=" + ("-" * inventory_width) + "=")

        self.add_print_list(print_list)

    @staticmethod
    def map():
        print("+ - - G - - + \n"
              "| t g F b . | \n"
              "| . a m . . | \n"
              "+ - - G - - + \n"
              " \n"
              "G: gate \n"
              "g: guild \n"
              "F: starting fountain \n"
              "b: babushka's house \n"
              "t: tavern \n"
              "m: market \n")

    def keys(self):
        print(self.player.get_keys())

    def event(self, text):
        if text == "":
            return
        self.add_print_list([self.color_text(text,"bold")])

    def topics_list(self, actor):
        topics_list = actor.get_topics_list(self.player.get_keys())
        print_list = []

        for chatKey, chatEntry in topics_list.items():
            print_list.append("\t" + self.color_text(chatEntry.get_topic(), "yellow"))
        if print_list == []:
            print_list.append(self.color_text("They don't want to talk.", "red"))
        else:
            print_list.insert(0, self.color_text(actor.get_name(), "blue") + " can talk about: ")
        self.add_print_list(print_list)

    def current_area(self):
        name = self.color_text(self.player.get_location().get_name(), "blue")
        desc = self.player.get_location().get_desc()
        self.add_print_list([self.color_text("You are at the ", "green") + name + ":",
                             "\t" + desc])

    def actor_list(self):
        print_list = []
        actor_list = self.player.get_location().get_actors_list()
        if len(actor_list) > 0:
            print_list.append(self.color_text("There is someone here:", "green"))
            for actor in actor_list:
                print_list.append("\t" + self.color_text(actor.get_name(), "yellow") + ": " + actor.get_desc())
        else:
            print_list.append(self.color_text("You are alone", "green"))

        self.add_print_list(print_list)

    def item_list(self):
        print_list = []
        item_list = self.player.get_location().get_item_list()
        if len(item_list) > 0:
            print_list.append(self.color_text("There is something here:", "green"))
            for item in item_list:
                if item.get_visible():
                    print_list.append("\t" + self.color_text(item.get_name(), "yellow") + ": " + item.get_desc())
        else:
            print_list.append(self.color_text("There is nothing of interest here", "green"))

        self.add_print_list(print_list)

    def link_list(self):
        print_list = []
        link_list = self.player.get_location().get_links()
        if len(link_list) > 0:
            print_list.append(self.color_text("There are places to go:", "green"))
            for link in link_list:
                print_list.append("\t" + self.color_text(link.get_direction(), "yellow") + ": " + link.get_room_name())
        else:
            print_list.append(self.color_text("There is nowhere to go", "green"))

        self.add_print_list(print_list)

    @staticmethod
    def color_text(text, color):
        if color == "green":
            return BColors.OKGREEN + text + BColors.ENDC
        if color == "red":
            return BColors.FAIL + text + BColors.ENDC
        if color == "yellow":
            return BColors.WARNING + text + BColors.ENDC
        if color == "blue":
            return BColors.OKBLUE + text + BColors.ENDC
        if color == "bold":
            return BColors.BOLD + text + BColors.ENDC
        return text

    # todo: this is like asking to be a recursive function. i cant see any downsides
    def break_text(self, text, line_width=None):
        # the inventory function requires a custom line length, but the normal print does not.
        if line_width is None:
            line_width = self.display_width

        # since a tab is for spaces but only counts as one character, adjust line width accordingly
        for _ in range(text.count("\t")):
            line_width -= 3

        # if newline then that's where we split
        if "\n" in text[:line_width]:
            index = text[:line_width + 1].rfind("\n")
            print_text = text[:index].rstrip()

        else:
            # if the text is less than the line width, you just return.
            if len(text) < line_width:
                return text, ""

            index = text[:line_width + 1].rfind(" ")
            print_text = text[:index].rstrip()

        line = text[index + 1:]
        # if the line started with a tab the subsequent ones should too
        if text[0] == "\t":
            line = "\t" + line

        return print_text, line


# todo: objectify act. turn each command into an object with functions for pre during and post.
# then we can just call:
# act.pre(commandList)
# act.active(commandList)
# act.post(commandList)
# can roll event listener in there so the main loop stays clean
# pre would probably just throw away the commandList but might use previous command. if we even need pre...
def act(command, player: Player, display: Display):
    # do verb on object
    verb = command[0]
    target = command[1]

    if verb == "pickup":
        target = " ".join(command[1:]).strip()
        attempt = player.pickup(target)
        if attempt is not None:
            display.event("you have picked up " + target)
            event_listener("onPickup", player, display, entity=attempt)
        else:
            display.confirm_command("you cannot pick that up", False)
    elif verb == "drop":
        target = " ".join(command[1:]).strip()
        attempt = player.drop(target)
        if attempt is not None:
            display.event("you have dropped " + target)
            event_listener("onDrop", player, display, entity=attempt)
        else:
            display.confirm_command("you do not have that item in your pockets", False)
    elif verb == "move":
        event_listener("onLeave", player, display)
        # todo: add check separate from action
        attempt = player.move(" ".join(filter(lambda x: len(x) > 0, command[1:])))
        if attempt is None:
            display.confirm_command("there is nothing in that direction", False)
        else:
            # todo: move leave to here, and add actual move in between on leave and and on enter.
            event_listener("onEnter", player, display)
    elif verb == "talk":
        topic = command[2]
        actor = player.get_location().get_actor_visible(target)
        if actor is not None:
            if topic != "":
                display.talk(actor, topic)
        else:
            display.talk(None, None, False)
    elif verb == "inventory":
        display.inventory()
        pass
    elif verb == "look":
        target = " ".join(command[1:]).strip()
        entity = player.get_location().get_item(target)
        if entity is None:
            entity = player.get_location().get_actor_visible(target)
        display.look(entity)
        if entity is not None:
            event_listener("onExamine", player, display, entity)

    elif verb == "use":
        target = " ".join(command[1:]).strip()
        entity = player.get_location().get_item(target)
        if entity is not None:
            event_listener("onUse", player, display, entity)
            pass
        else:
            display.reject("You cannot use that.")
    elif verb == "examine":
        pass
    elif verb == "key":
        display.keys()
    elif verb == "map":
        # display.map()
        pass
    else:
        event_listener(verb, player, display)
        display.confirm_command("I do not understand that command", False)

    # basic interaction types


# todo: change print statement to use the display object.
def event_listener(event_type, player, display: Display, entity: Entity = None):
    if entity is not None:
        events = entity.get_events()
    else:
        events = player.get_location().get_events()
    current_keys = copy.copy(player.get_keys())
    for event in events:
        if event.get_type() == event_type:
            # print("keys", current_keys)
            # print("whitelist", event.whitelistKeys)
            # print("blacklist", event.blacklistKeys)

            if event.check_allowed(current_keys):
                # print("event activated!")
                display.event(event.activate(player))
            else:
                # print("no event activated :(")
                pass

def win_condition(player):
    # what is the win condition
    # when the player gets a win key!
    if "win" in player.get_keys():
        print("you won!")
        print("next scenario!")
        player.remove_key("win")
        return True
    return False


def pre_act(player):
    pass
    return player


# todo fix babushka not giving correct options the first time she answers a topic.
# talk b c
# prints
# Babushka can talk about:
# 	cat
# instead of
# Babushka can talk about:
# 	cat
#   description
def post_act(command, player: Player, display: Display):
    player.update_keyring()
    player.get_location().update_keyring()

    if command is None:
        command = ["", ""]
    verb = command[0]
    target = command[1]
    if verb == "talk":
        actor = player.get_location().get_actor_visible(target)
        if actor is not None:
            display.topics_list(actor)
    display.display_room()
    display.print()
    pass


def intro_q():
    answers = []
    print("answer with y or n")
    answers.append(True if input("do you like swords") == "y" else False)
    answers.append(True if input("do you like talking") == "y" else False)
    answers.append(True if input("do you want mystery") == "y" else False)
    answers.append(True if input("do you want action") == "y" else False)
    return answers


def main():
    # print("Welcome to the game\n"
    #       "you can do a couple things:\n"
    #       "grab item, drop item\n"
    #       "look\n"
    #       "talk to people\n"
    #       "talk to people about topic\n"
    #       "move direction\n"
    #       "inv\n")
    # time.sleep(5)

    dm = ScenarioBuilder()

    test_cases = [
        [
            "e",
            "t b c",
            "w",
            "n",
            "t g o",
            "s",
            "w",
            "w",
            "go t",
            "k",
            "t b"
        ],
        [
            "e",
            "t b c",
            "w",
            "touch f",
            "touch f",
            "w",
            "s",
            "grab cat"
        ],
        [

            "e",
            "t b c",
            "w",
            "n",
            "t g o",
            "n",
            "look at the bush",
            "pickup b",
            "inv"
        ],
        [
            "e",
            "t b c",
            "w",
            "w",
            "t b c",
            "e",
            "s",
            "examine c",
            "t c c"
        ],
        [
            "n",
            "n",
            "grab s",
            "inv"
        ]
    ]
    test_case_num = 4
    testing = False
    while True:
        scene = dm.get_scenario()
        if scene is None:
            print("you won the game! congrats.")
            exit(1)
        player = scene.get_player()
        parser = Parser(player)
        display = Display(player)

        # have the player enter the room officially.
        event_listener("onEnter", player, display)
        post_act(None, player, display)

        while not win_condition(player):
            # TODO: implement pre/in/post act functions

            # current state of pre act function

            # input
            if len(test_cases[test_case_num]) > 0 and testing:
                command = test_cases[test_case_num].pop(0)
                print(">", command)
            else:
                command = input("> ")
            command_array = parser.parse_commands(command)

            dm.update_model(command_array)
            if dm.player_status():
                add, remove = dm.keys_from_model()
                for key in add:
                    player.add_key(key)
                for key in remove:
                    player.remove_key(key)
            # dm.print_model()

            # interpret input

            act(command_array, player, display)

            player.update_keyring()
            event_listener("active", player, display)

            post_act(command_array, player, display)

        # give the player some blank space to look at
        input("Press enter to continue...")
        print("\n\n\n\n\n\n\n\n")


main()
