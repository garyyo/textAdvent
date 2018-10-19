from __future__ import annotations
import json
import math

from entity import *
from event import *
from typing import List, Dict


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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


class Parser:
    words = {
        "article": ["a", "an", "the"],
        "preposition": ["of", "in", "to", "for", "with", "on", "at", "from", "by", "about", "as",
                        "into", "like", "through", "after", "over", "between", "out", "against",
                        "during", "without", "before", "under", "around", "among"],
        "intensifier": ["fucking"]
    }
    verbs = {
        "pickup": ["pickup", "grab", "get", "take"],
        "place": ["drop", "place"],
        "move": ["go", "move", "walk", "run"],
        "direction": ["north", "south", "east", "west", "up", "down", "left", "right",
                      "n", "s", "e", "w", "u", "d", "l", "r"],
        "look": ["look", "examine"],
        "talk": ["talk", "speak"],
        "inventory": ["inv", "inventory"],
        "key": ["key", "k"]
    }
    player: Player

    commandList: List[str]

    def __init__(self, player):
        self.player = player
        self.commandList = []

    def split_commands(self, command_str):
        self.commandList = command_str.split(" ") + ["", "", "", ""]

    def parse_commands(self, command_str):
        self.split_commands(command_str)
        self.strip_commands()
        verb = self.identify_verb()
        direct_object = self.identify_object(verb)
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
        # based on verb do different things
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

    def __init__(self):
        self.scenarioList = []
        self.playerModel = [0.51087279, 0.22050487, 0.4063116, 0.713533420, 0.08517401]
        # self.playerModel = [0]
        self.build_scenarios(["cat.json", "example.json"])
        pass

    def build_scenarios(self, file_list):
        for file in file_list:
            self.scenarioList.append(Scenario(file))

    def choose_scenario(self):
        if len(self.scenarioList) == 0:
            return None
        scene = min(self.scenarioList, key=lambda x: abs(sum(x.get_weights()) - sum(self.playerModel)))
        self.scenarioList.remove(scene)
        return scene


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
                room_json["initDesc"] if "initDesc" in room_json else ""
            )

            if "items" in room_json:
                for itemJSON in room_json["items"]:
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
                    linking_room.add_link(self.roomList[linkJSON["roomName"]], linkJSON["direction"])

    def actor_create(self, actor_json):
        new_actor = Actor(
            actor_json["name"] if "name" in actor_json else "",
            actor_json["initDesc"] if "initDesc" in actor_json else "",
            actor_json["desc"] if "desc" in actor_json else ""
        )
        if "hidden" in actor_json:
            new_actor.hide()

        if "dialogues" in actor_json:
            for dialogueJSON in actor_json["dialogues"]:
                new_actor.add_dialogue(
                    Dialogue(dialogueJSON["topic"] if "topic" in dialogueJSON else "",
                             dialogueJSON["text"] if "text" in dialogueJSON else "they stay silent",
                             dialogueJSON["whitelist"] if "whitelist" in dialogueJSON else "",
                             dialogueJSON["blacklist"] if "blacklist" in dialogueJSON else "",
                             dialogueJSON["key"] if "key" in dialogueJSON else "",
                             dialogueJSON["unkey"] if "unkey" in dialogueJSON else ""
                             )
                )

        self.actorList.append(new_actor)
        return new_actor

    def item_create(self, item_json):
        new_item = Item(
            item_json["name"] if "name" in item_json else "",
            item_json["initDesc"] if "initDesc" in item_json else "",
            item_json["invDesc"] if "invDesc" in item_json else "",
            item_json["desc"] if "desc" in item_json else "",
            item_json["weight"] if "weight" in item_json else 0.0,
            item_json["smell"] if "smell" in item_json else "",
            item_json["taste"] if "taste" in item_json else "",
            item_json["size"] if "size" in item_json else "",
            item_json["pickupable"] if "pickupable" in item_json else False,
            item_json["pickupKey"] if "pickupKey" in item_json else ""
        )
        if "hidden" in item_json:
            new_item.hide()

        self.itemList.append(new_item)
        return new_item

    def event_create(self, event_json):
        new_event = Event(
            event_json["whitelist"] if "whitelist" in event_json else "",
            event_json["blacklist"] if "blacklist" in event_json else "",
            event_json["key"] if "key" in event_json else "",
            event_json["unkey"] if "unkey" in event_json else "",
            event_json["text"] if "text" in event_json else "",
            event_json["type"] if "type" in event_json else ""
        )
        if "makeVisible" in event_json:
            for visibleJSON in event_json["makeVisible"]:
                new_event.add_make_visible([
                    visibleJSON["name"] if "name" in visibleJSON else "",
                    visibleJSON["class"] if "class" in visibleJSON else ""
                ])
        if "makeInvisible" in event_json:
            for visibleJSON in event_json["makeInvisible"]:
                new_event.add_make_invisible([
                    visibleJSON["name"] if "name" in visibleJSON else "",
                    visibleJSON["class"] if "class" in visibleJSON else ""
                ])

        self.eventList.append(new_event)
        return new_event

    def get_weights(self):
        return self.jsonData["weights"] if "weights" in self.jsonData else [0, 0, 0, 0, 0]

    def get_player(self):
        starting_keys = self.jsonData["startingKeys"] if "startingKeys" in self.jsonData else []
        return Player(self.roomList[self.start_location], starting_keys)


class Display:
    player: Player

    # pass in arbitrary objects and get proper formatting for their description.
    def __init__(self, player):
        self.player = player
        pass

    def display(self):
        # confirm command
        # self.display_command()
        # display any relevant events
        # self.display_event()
        # print place description
        # self.display_
        # exits

        # people

        # items

        pass

    def confirm_command(self):
        # if inventory command, display inventory in a nicely formatted manner.

        pass

    def inventory(self):
        if not self.player.get_inventory():
            return
        print_list = []
        inventory_width = 5 + len(max(self.player.get_inventory(), key=lambda x: len(x.get_inv_desc())).get_inv_desc())
        print_list.append("=" + ("-"*int(inventory_width)) + "=")
        print_list.append("|" + (" "*int(inventory_width)) + "|")
        item_num = 0
        for item in self.player.get_inventory():
            item_num += 1
            d = " " + str(item_num) + ": " + item.get_inv_desc()
            d_length = len(d)
            d_spaced =  d + (math.floor((inventory_width - d_length)) * " ")
            print_list.append("|" + d_spaced + "|")

        print_list.append("|" + (" "*inventory_width) + "|")
        print_list.append("=" + ("-"*inventory_width) + "=")

        print("\n".join(print_list))

    def actor_list(self):
        print_list = []
        actor_list = self.player.get_location().get_actors_list()
        if len(actor_list) > 0:
            print_list.append("There is someone here:")
            for actor in actor_list:
                print_list.append("\t" + actor.get_name() + ": " + actor.get_desc())
        else:
            print_list.append("You are alone")
        print("\n".join(print_list))

    def item_list(self):
        print_list = []
        actor_list = self.player.get_location().get_actors_list()
        if len(actor_list) > 0:
            print_list.append("There is someone here:")
            for actor in actor_list:
                print_list.append("\t" + actor.get_name() + ": " + actor.get_desc())
        else:
            print_list.append("You are alone")
        print("\n".join(print_list))

    def link_list(self):
        print_list = []
        link_list = self.player.get_location().get_links()
        if len(link_list) > 0:
            print_list.append("There are places to go:")
            for link in link_list:
                print_list.append("\t" + link.get_direction() + ": " + link.get_room_name())
        else:
            print_list.append("There is nowhere to go")
        print("\n".join(print_list))


def act(command, player):
    # do verb on object
    verb = command[0]
    target = command[1]

    if verb == "pickup":
        attempt = player.pickup(target)
        if attempt is not None:
            print("you have picked up", target)
        else:
            print("you cannot pick that up")
    elif verb == "drop":
        attempt = player.drop(target)
        if attempt is not None:
            print("you have dropped", target)
        else:
            print("you do not have that item in your pockets")
    elif verb == "move":
        attempt = player.move(target)
        if attempt is None:
            print("there is nothing in that direction")
        else:
            event_listener("onEnter", player)
    elif verb == "talk":
        topic = command[2]
        actor = player.get_actor(target)
        if topic == "":
            if actor is not None:
                print(actor.get_topics(player.get_keys()))
            else:
                print("you talk into the aether to someone who isn't there")
        else:
            if actor is not None:
                print(player.talk(actor, topic))
                print("")
            else:
                print("you talk into the aether to someone who isn't there")
    elif verb == "inventory":
        print(player.display_inventory())
    elif verb == "look":
        print(player.look_around())

    elif verb == "use":
        # the target is activated and key might be given (which then would activate event?)
        pass
    elif verb == "examine":
        pass
    elif verb == "key":
        print(player.get_keys())
    else:
        print("I do not understand that command")

    # basic interaction types


def event_listener(event_type, player):
    events = player.get_location().get_events()
    for event in events:
        if event.get_type() == event_type:
            # print(player.getKeys())
            # print(event.whitelistKeys, event.blacklistKeys)

            if event.check_allowed(player.get_keys()):
                # print("event activated!")
                print(event.activate(player))
            # else:
            #     print("no event activated :(")


def win_condition(player):
    # what is the win condition
    # when the player gets a win key!
    if "win" in player.get_keys():
        print("you won!")
        print("next scenario!")
        player.remove_key("win")
        return True
    return False


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

    dungeon_master = ScenarioBuilder()

    while True:
        scene = dungeon_master.choose_scenario()
        if scene is None:
            print("you won the game! congrats.")
            exit(1)
        player = scene.get_player()
        parser = Parser(player)
        display = Display(player)

        # have the player enter the room officially.
        event_listener("onEnter", player)

        while not win_condition(player):
            # TODO: implement pre/in/post act functions

            # current state of pre act function
            print(player.look_around())

            # input
            command = input("> ")
            command_array = parser.parse_commands(command)

            # interpret input
            # command_array = parseInput(command, player)
            # act on input and display
            act(command_array, player)
            event_listener("active", player)
            # postAct(command_array, player)

        # give the player some blank space to look at
        input("Press enter to continue...")
        print("\n\n\n\n\n\n\n\n")


main()
