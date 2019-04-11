from __future__ import annotations

import copy
import json
import math
import random
from pprint import pprint
import scipy.stats
import numpy as np
import matplotlib

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
        "map": ["map"],
        "give": ["give"]
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
            actor = self.player.get_current_room().get_actor_when_visible(direct_object)
            topic = " ".join(filter(lambda x: len(x) > 0, self.commandList[2:]))
            if actor is None:
                direct_object = self.sp_entity_name(direct_object, self.player.get_current_room().get_actors_visible(), 0.7)
                actor = self.player.get_current_room().get_actor_when_visible(direct_object)
            if actor and not actor.check_topic(topic, self.player.get_keys()):
                topic = self.sp_event_name(topic, actor.get_topics_list(self.player.get_keys()), .4)
            self.commandList[2] = topic
        if verb == "move":
            direct_object = self.sp_link_name(direct_object, self.player.get_current_room().get_links(), 0.7)
        if verb in ["pickup"]:
            direct_object = self.sp_entity_name(direct_object, self.player.get_current_room().get_items_visible(), 0.7)
        if verb in ["look"]:
            direct_object = self.sp_entity_name(direct_object, self.player.get_current_room().get_items_visible() +
                                                self.player.get_current_room().get_actors_visible(), 0.7)
        if verb in ["use"]:
            direct_object = self.sp_entity_name(
                direct_object,
                self.player.get_current_room().get_items_visible() + self.player.get_inventory(),
                0.7)
        if verb in ["drop"]:
            direct_object = self.sp_entity_name(direct_object, self.player.get_inventory(), 0.7)
        if verb in ["give"]:
            actor = self.player.get_current_room().get_actor_when_visible(direct_object)
            give_object = self.sp_entity_name(self.commandList[2], self.player.get_inventory(), 0.7)
            self.commandList[1] = actor
            self.commandList[2] = give_object
        return direct_object

    def collect_entity_list(self):
        # get entities in location
        location = self.player.get_current_room()
        entity_list = location.get_items_visible()
        entity_list += location.get_actors_visible()

        # get items in player inventory
        entity_list += self.player.get_inventory()
        return entity_list

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
                continue
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
    player_model: Dict[str, float]
    currentScene: Scenario
    state: str
    action_history: List[str]
    action_choices = ["pickup", "look", "talk", "use"]

    def __init__(self, history_length=10):
        self.scenarioList = []
        self.player_model = {}
        self.current_model = {}
        self.action_history = []
        self.history_length = history_length
        self.build_scenarios(["boring.json", "cat.json"])
        self.state = "wait"

        self.reset_model()
        self.initialize_actions()
        for action in self.action_choices:
            self.current_model[action] = 0
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
        # scene = min(self.scenarioList, key=lambda x: abs(sum(x.get_weights()) - sum(self.player_model.values())))
        scene = self.scenarioList[0]
        # todo: re-enable when we have more scenes
        # self.scenarioList.remove(scene)
        return scene

    def initialize_actions(self):
        for i in range(self.history_length):
            action = np.random.choice(list(self.player_model.keys()), p=list(self.player_model.values()))
            self.action_history.append(action)
        pass

    def add_action(self, action):
        if action in self.action_choices:
            self.action_history.append(action)
        self.action_choices = self.action_choices[:self.history_length]
        pass

    def update_model(self, command_array):
        large_threshold = .5
        small_threshold = .2

        # update action history
        self.add_action(command_array[0])

        # recalculate model
        self.calculate_model()

        # check against expected
        difference = self.model_difference()
        entropy = self.calculate_entropy()

        # debug: difference
        print("difference:", difference)
        print("entropy:", entropy)

        if difference is None or difference is np.nan:
            print("this should never happen, you messed up chi-squared.")
            return

        # if difference is big, update model and trigger path change attempt
        # todo: get rid of this warning.
        if difference > large_threshold:
            self.change_model()
            self.path_change()
            return

        # if difference is small, deploy distraction
        if difference > small_threshold:
            # add intervention/distraction task
            self.deploy_distraction()

        # else continue on like normal.

        pass

    def calculate_model(self):
        # based on the player action history, create a model, currently the relative frequency of all relevant actions
        action_frequency = {}
        # properly initalize
        for action in self.action_choices:
            action_frequency[action] = 0

        for action in self.action_history:
            if action not in action_frequency:
                action_frequency[action] = 0
            action_frequency[action] += 1

        for action in action_frequency:
            if action_frequency[action] == 0:
                action_frequency[action] += .0001

        # get average
        for action in action_frequency:
            action_frequency[action] = action_frequency[action] / self.history_length
        self.current_model = action_frequency

    def calculate_entropy(self):
        def sort_dict(dictionary): return [v for k, v in sorted(dictionary.items())]

        current = sort_dict(self.current_model)
        expected = sort_dict(self.player_model)

        return scipy.stats.entropy(current, expected)

    def model_difference(self):
        # expected cant have 0's
        def sort_dict(dictionary): return [v for k, v in sorted(dictionary.items())]

        current = sort_dict(self.current_model)
        expected = sort_dict(self.player_model)

        # print(current, self.current_model)
        # print(expected, self.player_model)

        difference, _ = scipy.stats.chisquare(current, expected)
        return difference

    # currently this just changes the player model to the action history calculated model,
    # todo: in the future it should shift to an accepted quest path model.
    def change_model(self):
        self.player_model = copy.deepcopy(self.current_model)

    # this should modify the player object to flag it for a path change.
    def path_change(self):
        print("path change initiated!")
        pass

    # this should modify the player object to flag it with what the player should be attempted to be distracted with.
    def deploy_distraction(self):
        print("distraction deployed!")
        pass

    # the rest of this shouldnt do anything useful0 for the player.
    def reset_model(self):
        for action in self.action_choices:
            self.player_model[action] = random.random()
        self.quest_dist()

    def print_model(self):
        print(self.player_model)

    # todo: rewrite, it currently does jack shit
    def trace_quests(self):
        def ei(event_list):
            return_string = ""
            if event_list is None:
                return ""
            for event in event_list:
                return_string += ",".join(event.whitelistKeys)
                return_string += " | "
                return_string += event.source_type
                return_string += "->"
                return_string += event.type
                return_string += "->"
                return_string += event.source_ID if event.source_ID is not None else ""
                return_string += " | "
                return_string += ",".join(event.giveKeys)
                return_string += "\n\t"
                return_string += event.text
                return_string += "\n"

            return return_string

        def find_item_show(item: Item):
            event_list = []
            for event in self.currentScene.eventList:
                for visible in event.makeVisible:
                    if item.name in visible[0] and event.room == item.start_room:
                        event_list.append(event)
            return event_list

        def find_keys(key):
            # return key, unkey
            return_list = []
            for event in self.currentScene.eventList:
                if key in event.giveKeys:
                    return_list.append(event)
            return return_list

        def pre_step(req_list):
            return_list = []
            for prereq in req_list:
                if prereq.type == "onPickup":
                    new_list = find_item_show(prereq.source)
                    print(ei(new_list))
                    return_list += new_list
                else:
                    for key in prereq.whitelistKeys:
                        new_list = find_keys(key)
                        print(ei(new_list))
                        return_list += new_list
            return return_list

        print("step================================================================")
        prereq_list: List[Event] = find_keys("win")
        print(ei(prereq_list))
        print("step================================================================")
        prereq_list = pre_step(prereq_list)
        print("step================================================================")
        prereq_list = pre_step(prereq_list)
        print("step================================================================")
        prereq_list = pre_step(prereq_list)

        pass

    # todo: rework this to actually tell if player is bored.
    def quest_dist(self):
        v = {'look': 0.3333333333333333,
             'pickup': 0.3333333333333333,
             'talk': 0.2666666666666666,
             'use': 0.06666666666666667}
        t = {'look': 0.000000000001,
             'pickup': 0.23529411764705882,
             'talk': 0.7058823529411765,
             'use': 0.058823529411764705}
        l = {'look': 0.3124, 'pickup': 0.3125, 'talk': 0.0001, 'use': 0.375}
        r = {'look': random.random(),
             'pickup': random.random(),
             'talk': random.random(),
             'use': random.random()}
        self.player_model = r
        list_sum = sum(self.player_model.values())
        for key, value in self.player_model.items():
            self.player_model[key] = value/list_sum


class Scenario:
    roomList: Dict[str, Room]
    eventList: List
    dialogueList: List
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
        self.dialogueList = []

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
                    new_room.add_item(self.item_create(itemJSON, new_room))
            if "backgrounds" in room_json:
                for itemJSON in room_json["backgrounds"]:
                    new_room.add_item(self.item_create(itemJSON, new_room))
            if "actors" in room_json:
                for actorJSON in room_json["actors"]:
                    new_room.add_actor(self.actor_create(actorJSON, new_room))
            if "events" in room_json:
                for eventJSON in room_json["events"]:
                    new_room.add_event(self.event_create(eventJSON, new_room, source_type="room", source=new_room))

            # distractions need to be made for every type of thing that a player can get distracted by
            for distract_type in ["look", "talk", "use", ]:
                new_room.add_item(self.distraction_generation(new_room, distract_type))

            self.roomList[name] = new_room

    def link_builder(self):
        for room_json in self.jsonData["rooms"]:
            if "links" in room_json:
                linking_room = self.roomList[room_json["name"]]
                for linkJSON in room_json["links"]:
                    linking_room.add_link(self.roomList[linkJSON["roomName"]] if "roomName" in linkJSON else "template",
                                          linkJSON["direction"] if "direction" in linkJSON else "up",
                                          linkJSON["hidden"] if "hidden" in linkJSON else False)

    def actor_create(self, actor_json, new_room):
        new_actor = Actor(
            actor_json["name"] if "name" in actor_json else "",
            actor_json["examine"] if "examine" in actor_json else "",
            actor_json["desc"] if "desc" in actor_json else "",
            new_room
        )
        if new_actor.get_name() in ["template", ""]:
            return None

        if "events" in actor_json:
            for eventJSON in actor_json["events"]:
                new_actor.add_event(self.event_create(eventJSON, new_room, source_type="actor", source=new_actor))

        if "hidden" in actor_json:
            new_actor.hide()

        if "dialogues" in actor_json:
            for dialogueJSON in actor_json["dialogues"]:
                new_dialogue = Dialogue(
                    dialogueJSON["whitelist"] if "whitelist" in dialogueJSON else "",
                    dialogueJSON["blacklist"] if "blacklist" in dialogueJSON else "",
                    dialogueJSON["key"] if "key" in dialogueJSON else "",
                    dialogueJSON["unkey"] if "unkey" in dialogueJSON else "",
                    dialogueJSON["keyRoom"] if "keyRoom" in dialogueJSON else [""],
                    dialogueJSON["unkeyRoom"] if "unkeyRoom" in dialogueJSON else [""],
                    dialogueJSON["text"] if "text" in dialogueJSON else "they stay silent",
                    dialogueJSON["topic"] if "topic" in dialogueJSON else "",
                    new_room
                )

                # get rid of empty entries.
                for i in range(len(new_dialogue.whitelistKeys)):
                    if new_dialogue.whitelistKeys[i] == "":
                        new_dialogue.whitelistKeys.pop(i)
                for i in range(len(new_dialogue.blacklistKeys)):
                    if new_dialogue.blacklistKeys[i] == "":
                        new_dialogue.blacklistKeys.pop(i)

                new_actor.add_dialogue(new_dialogue)
                self.eventList.append(new_dialogue)
        self.actorList.append(new_actor)
        return new_actor

    def item_create(self, item_json, start_room):
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
            item_json["pickupKey"] if "pickupKey" in item_json else "",
            start_room
        )

        # get rid of templates
        if new_item.get_name() in ["template", ""]:
            return None

        if "events" in item_json:
            for eventJSON in item_json["events"]:
                new_item.add_event(self.event_create(eventJSON, start_room, source_type="item", source=new_item))

        if "hidden" in item_json:
            new_item.hide()

        self.itemList.append(new_item)
        return new_item

    def background_create(self, item_json, start_room):
        new_item = Background(
            item_json["name"] if "name" in item_json else "",
            item_json["examine"] if "examine" in item_json else "",
            item_json["invDesc"] if "invDesc" in item_json else "",
            item_json["desc"] if "desc" in item_json else "",
            item_json["weight"] if "weight" in item_json else 0.0,
            item_json["smell"] if "smell" in item_json else "",
            item_json["taste"] if "taste" in item_json else "",
            item_json["size"] if "size" in item_json else "",
            start_room
        )

        # get rid of templates
        if new_item.get_name() in ["template", ""]:
            return None

        if "hidden" in item_json:
            new_item.hide()

        self.itemList.append(new_item)
        return new_item

    def event_create(self, event_json, room, source_type=None, source=None):
        new_event = Event(
            event_json["whitelist"] if "whitelist" in event_json else "",
            event_json["blacklist"] if "blacklist" in event_json else "",
            event_json["key"] if "key" in event_json else [""],
            event_json["unkey"] if "unkey" in event_json else [""],
            event_json["keyRoom"] if "keyRoom" in event_json else [""],
            event_json["unkeyRoom"] if "unkeyRoom" in event_json else [""],
            event_json["text"] if "text" in event_json else "",
            event_json["type"] if "type" in event_json else "",
            room,
            source_type=source_type,
            source=source
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

    def distraction_generation(self, room, distraction_type):
        # get a list of distractions
        new_item = Background(
            "distraction: type " + distraction_type,
            "aha you got distracted!",
            "aha you got distracted!",
            "aha you got distracted!",
            0,
            "aha you got distracted!",
            "aha you got distracted!",
            "aha you got distracted!",
            room
        )
        new_item.set_distractor(True, distraction_type)
        new_item.hide()

        self.itemList.append(new_item)
        return new_item
        pass

    def get_weights(self):
        return self.jsonData["weights"] if "weights" in self.jsonData else [0, 0, 0, 0, 0]

    def get_player(self):
        map_chart = self.jsonData["map"] if "map" in self.jsonData else "you have no map"
        starting_keys = self.jsonData["startingKeys"] if "startingKeys" in self.jsonData else []
        player = Player(self.roomList[self.start_location], starting_keys, map_chart)
        player.add_gold(self.jsonData["initialGold"] if "initialGold" in self.jsonData else 0)
        return player


class Display:
    player: Player
    display_width = 150
    print_list: List[List[str]]

    # pass in arbitrary objects and get proper formatting for their description.
    def __init__(self, player, active=True):
        self.player = player
        self.print_list = []
        self.active = active

    def add_print_list(self, print_list):
        self.print_list.append(print_list)

    def print(self):
        if not self.active:
            return
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
    # todo: also, get rid of the print statements in here >:(
    # im already doing this pretty much, but when i want to reject a message i use this? put rejections in the others
    def confirm_command(self, text: str, status: bool = True, command: str = None, args: List[str] = None):
        if not self.active:
            return
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
            self.reject("you talk into the aether to someone who isn't there")

    def inventory(self):
        margin_width = 8
        print_list = []

        gold_text = " gold: " + str(self.player.get_gold())
        gold_text_length = len(gold_text)

        if self.player.get_inventory():
            max_item = max(self.player.get_inventory(), key=lambda x: len(x.get_inv_desc()) + len(x.get_name()))
            inventory_width = margin_width + len(max_item.get_inv_desc()) + len(max(max_item.get_name()))
            inventory_width = min(inventory_width, self.display_width + margin_width)
        else:
            inventory_width = gold_text_length + 1

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

    def map(self):
        print(self.player.map)

    def keys(self):
        print(self.player.get_keys())

    def event(self, text):
        if text == "":
            return
        self.add_print_list([self.color_text(text, "bold")])

    def topics_list(self, actor):
        topics_list = actor.get_topics_list(self.player.get_keys())
        print_list = []

        for chatKey, chatEntry in topics_list.items():
            print_list.append("\t" + self.color_text(chatEntry.get_topic(), "yellow"))
        if not print_list:
            self.reject("They don't want to talk.")
            print_list.append(self.color_text("", "red"))
        else:
            print_list.insert(0, self.color_text(actor.get_name(), "blue") + " can talk about: ")
        self.add_print_list(print_list)

    def current_area(self):
        name = self.color_text(self.player.get_current_room().get_name(), "blue")
        desc = self.player.get_current_room().get_desc()
        self.add_print_list([self.color_text("You are at the ", "green") + name + ":",
                             "\t" + desc])

    def actor_list(self):
        print_list = []
        actor_list = self.player.get_current_room().get_actors_visible()
        if len(actor_list) > 0:
            print_list.append(self.color_text("There is someone here:", "green"))
            for actor in actor_list:
                print_list.append("\t" + self.color_text(actor.get_name(), "yellow") + ": " + actor.get_desc())
        else:
            print_list.append(self.color_text("You are alone", "green"))

        self.add_print_list(print_list)

    def item_list(self):
        print_list = []
        item_list = self.player.get_current_room().get_items_visible()
        if len(item_list) > 0:
            print_list.append(self.color_text("There is something here:", "green"))
            for item in item_list:
                print_list.append("\t" + self.color_text(item.get_name(), "yellow") + ": " + item.get_desc())
        else:
            print_list.append(self.color_text("There is nothing of interest here", "green"))

        self.add_print_list(print_list)

    def link_list(self):
        print_list = []
        link_list = self.player.get_current_room().get_links()
        if len(link_list) > 0:
            print_list.append(self.color_text("There are places to go:", "green"))
            for link in link_list:
                print_list.append(
                    "\t" + self.color_text(link.get_direction(), "yellow") + ": room " + link.get_room_name())
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


# can roll event listener in there so the main loop stays clean
class Act:
    action_functions: Dict
    display: Display

    def __init__(self, display, player):
        self.display = display
        self.player = player
        self.command = []
        self.action_functions = {
            "pickup": self.grab,
            "drop": self.drop,
            "move": self.move,
            "talk": self.talk,
            "inventory": self.inventory,
            "look": self.examine,
            "use": self.use,
            "key": self.key,
            "map": self.map,
            "give": self.give
        }
        pass

    def pre(self):
        self.player.update_keyring()
        self.player.get_current_room().update_keyring()
        self.display.display_room()
        self.display.print()
        pass

    def mid(self, commands):
        verb = commands[0]
        self.command = commands
        if verb in self.action_functions:
            self.action_functions[verb]()
        else:
            event_listener(verb, self.player, self.display)
            self.display.confirm_command("I do not understand that command", False)
        pass

    def post(self, commands):

        self.player.update_keyring()
        self.player.get_current_room().update_keyring()

        if commands is None:
            commands = ["", ""]
        verb = commands[0]
        target = commands[1]
        if verb == "talk":
            actor = self.player.get_current_room().get_actor_when_visible(target)
            if actor is not None:
                self.display.topics_list(actor)
        pass

    # give to npc
    # todo: make this work when you have the proper item, and not work when you dont.
    def give(self):
        # give actor object
        # find object in inventory
        item_name = self.command[2]
        item_ref = self.player.drop(item_name)

        # find actor in world
        actor_name = self.command[1]
        actor_ref: Actor = self.player.get_current_room().get_actor_when_visible(actor_name)
        keys = []
        # check if actor wants this item?!?! check for keys
        if actor_ref is not None and item_ref is not None:
            # print("blah", actor_ref.get_events_type("onGive"))
            #
            #
            #     keys.append(list(event.get_keys()))
            #     print("keys", keys)
            # self.player.has_keys(keys)

            # check if the actor can accept the gift.
            # look for an onGive event
            for event in actor_ref.get_events_type("onGive"):
                # for each event, check to see if player violates the keys
                gift_allowed_flag = event.check_allowed(self.player.get_keys()) or gift_allowed_flag
            if not gift_allowed_flag:
                self.display.reject("They do not want that.")
                return
            else:
                actor_ref.add_to_inventory(item_ref)
                event_listener("onGive", self.player, self.display, entity=actor_ref)
        else:
            self.display.reject("error parsing string, please check spelling")
        pass

    # pick up from room
    # or container if specified
    def grab(self):

        target = " ".join(self.command[1:]).strip()
        attempt = self.player.pickup(target)
        if attempt is not None:
            self.display.event("you have picked up " + target)
            event_listener("onPickup", self.player, self.display, entity=attempt)
        else:
            self.display.confirm_command("you cannot pick that up", False)
        pass

    # place in room
    def drop(self):
        target = " ".join(self.command[1:]).strip()
        attempt = self.player.drop(target)
        if attempt is not None:
            self.player.get_current_room().add_item(attempt)
            self.display.event("you have dropped " + target)
            event_listener("onDrop", self.player, self.display, entity=attempt)
        else:
            self.display.confirm_command("you do not have that item in your pockets", False)
        pass

    # move to another room
    def move(self):
        event_listener("onLeave", self.player, self.display)
        # todo: add check separate from action
        attempt = self.player.move(" ".join(filter(lambda x: len(x) > 0, self.command[1:])))
        if attempt is None:
            self.display.confirm_command("there is nothing in that direction", False)
        else:
            # todo: move leave to here, and add actual move in between on leave and and on enter.
            event_listener("onEnter", self.player, self.display)
        pass

    # talk to npc
    def talk(self):
        target = self.command[1]
        topic = self.command[2]
        actor = self.player.get_current_room().get_actor_when_visible(target)
        if actor is not None:
            if topic != "":
                self.display.talk(actor, topic)
        else:
            self.display.talk(None, None, False)
        pass

    # look
    def examine(self):
        target = " ".join(self.command[1:]).strip()
        entity = self.player.get_current_room().get_item(target)
        if entity is None:
            entity = self.player.get_current_room().get_actor_when_visible(target)
        self.display.look(entity)
        if entity is not None:
            event_listener("onExamine", self.player, self.display, entity)
        pass

    # print the inventory
    def inventory(self):
        self.display.inventory()
        pass

    # activate the use event on object in (inventory or) room
    def use(self):
        target = " ".join(self.command[1:]).strip()
        entity = self.player.get_current_room().get_item(target)
        if entity is not None:
            event_listener("onUse", self.player, self.display, entity)
            pass
        else:
            self.display.reject("You cannot use that.")
        pass

    # print map
    def map(self):
        self.display.map()
        pass

    # print keys, for debugging
    def key(self):
        self.display.keys()
        pass


# todo: show some distractions!
def show_all_distractions(player, show=True):
    items = player.get_current_room().get_items()
    distraction_list = filter(lambda x: x.get_distractor(), items)
    for item in distraction_list:
        if show:
            item.show()
        else:
            item.hide()
        pass


def show_some_distractions(player: Player, distraction_type):
    items = player.get_current_room().get_items()
    actors = player.get_current_room().get_actors()
    entities = items + actors
    distraction_entities = list(filter(lambda x: x.get_distractor(), entities))
    filtered_entities = list(filter(lambda x: x.distraction_type == distraction_type, distraction_entities))
    for entity in distraction_entities:
        entity.hide()
    for entity in filtered_entities:
        entity.show()
    pass


# todo: change print statement to use the display object.
def event_listener(event_type, player, display: Display, entity: Entity = None):
    if entity is not None:
        events = entity.get_events()
    else:
        events = player.get_current_room().get_events()
    current_keys = copy.copy(player.get_keys())
    # print(event_type, events)
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


# def intro_q():
#     answers = []
#     print("answer with y or n")
#     answers.append(True if input("do you like swords") == "y" else False)
#     answers.append(True if input("do you like talking") == "y" else False)
#     answers.append(True if input("do you want mystery") == "y" else False)
#     answers.append(True if input("do you want action") == "y" else False)
#     return answers

class History:
    player: Player
    saved_commands: List
    test_commands = [
        ['n',
         'e',
         'look at book',
         'g b',
         'grab book',
         's',
         'examine holocube',
         'examine pedestal',
         'use pede',
         'pickup holocube',
         'use pedestal',
         's',
         'look at projector',
         'use pro',
         'e',
         'w',
         'examine b',
         'use bookshelf',
         'grab keymold',
         'e',
         'use projector',
         'pickup golden key',
         'grab g',
         'w',
         'n'],
        [
            "w",
            "t b",
            "t b h",
            "t b f",
            "e",
            "n",
            "t w",
            "t w g",
            "e",
            "s",
            "grab tab",
            "s",
            "w",
            "pickup b",
            "n",
            "n",
            "t w",
            "t w t",
            "drop book",
            "drop tablet",
            "talk w",
            "t w d",
            "grab g",
            "s",
            "w",
            "t b",
            "t b favor done",
            "drop gold",
            "t b k",
            "grab g",
            "e",
            "use g"
        ],
        [
            "pickup ball",
            "give anton ball"
        ]
    ]
    test_num = 0
    test_flag = False
    dm_test_flag = True

    def __init__(self, player, auto_turns=10):
        self.counter = 0
        self.auto_turns = auto_turns
        self.player = player
        self.saved_commands = []
        self.dm_test_commands = []
        self.set_model()

        self.true_model = dict(look=random.random(), pickup=random.random(), talk=random.random(), use=random.random())

        list_sum = sum(self.true_model.values())
        for key, value in self.true_model.items():
            self.true_model[key] = value / list_sum

    def record_commands(self):
        pass

    def print_commands(self):
        pprint(self.saved_commands)
        pass

    def auto_command(self, model=None):
        self.counter += 1
        if self.counter > self.auto_turns:
            return None
        if self.test_flag and self.test_commands[self.test_num]:
            return self.test_commands[self.test_num].pop(0)
        if self.dm_test_flag:
            return self.get_action_from_model(model)
        else:
            return None

    def update(self, command):
        # record command
        self.saved_commands.append(command)
        pass

    def get_action_from_model(self, true_model=None):
        if true_model is None:
            true_model = self.true_model

        # generate action
        partial_action = np.random.choice(list(true_model.keys()), p=list(true_model.values()))

        # check to see if there are entities in the current room that are consistent with that action
        # find_all_entities_ir_room()
        # if actors, check if dialogs exist and player has keys for it
        # (with some probability to talk even if keys dont exist?)
        full_action = self.expand_command(partial_action)

        # if a valid action doesnt exist
        if full_action is None:
            # todo: try other commands with some prob?
            # current: move to other room.
            full_action = random.choice(["n","s","e","w"])
            pass

        return full_action

    def expand_command(self, partial_command):
        translation = {
            "pickup": "onPickup",
            "look": "onExamine",
            "talk": "dialogue",
            "use": "onUse"
        }
        if partial_command in translation:
            event_type = translation[partial_command]
        else:
            return None
        # room.get_entities? only the ones that are visible though
        current_room = self.player.get_current_room()
        all_entities = current_room.get_actors_visible() + current_room.get_items_visible()

        for entity in all_entities:
            # special case handling for dialogue
            if event_type == "dialogue":
                if type(entity) == Actor:
                    topics = entity.get_topics_list(self.player.get_keys()).values()
                    if len(topics) :
                        return None
                    dialogue = random.choice(topics)
                    return partial_command + " " + entity.get_name() + dialogue.get_topic()
                continue

            # non-examine events only work on Items
            if event_type != "onExamine":
                if type(entity) != Item:
                    continue

            events = entity.get_events_type(event_type)
            if not events:
                return None
            for event in events:
                if event.check_allowed(self.player.get_keys()):
                    return partial_command + " " + entity.get_name()

        return None

    def set_model(self, true_model=None):
        self.true_model = true_model
        pass


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

    dm = ScenarioBuilder(history_length=30)

    while True:
        scene = dm.get_scenario()
        if scene is None:
            print("you won the game! congrats.")
            exit(1)
        player = scene.get_player()
        parser = Parser(player)
        history = History(player, auto_turns=30)
        display = Display(player, False)
        act = Act(display, player)

        history.set_model(dict(look=.1, pickup=.1, talk=.1, use=.7))

        # todo: finish trace test
        # trace_test(dm)

        # have the player enter the room officially.
        event_listener("onEnter", player, display)
        act.post(None)

        while not win_condition(player):
            act.pre()

            # input
            command = history.auto_command()
            if command is None:
                command = input("> ")
            else:
                print(">", command)
            # todo: move this to the act object
            if command == "record":
                history.print_commands()
                continue

            history.update(command)

            command_array = parser.parse_commands(command)

            dm.update_model(command_array)

            act.mid(command_array)

            player.update_keyring()
            event_listener("active", player, display)

            act.post(command_array)

        # give the player some blank space to look at
        input("Press enter to continue...")
        print("\n\n\n\n\n\n\n\n")


def trace_test(dm):
    dm.trace_quests()
    exit(0)


def print_story():
    # todo: print the current quest in an easy to parse manner. to make editing easier?
    pass


main()
