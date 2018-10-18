from __future__ import annotations
import json

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
    events: List[event]
    name: str
    initDesc: str
    description: str

    def __init__(self, name: str, description: str, initDesc: str):
        self.name = name
        self.description = description
        self.initDesc = initDesc
        self.links = []
        self.items = []
        self.actors = []
        self.events = []

    def add_item(self, itemRef):
        self.items.append(itemRef)

    def remove_item(self, index: int):
        return self.items.pop(index)

    def get_items_index(self, itemName: str) -> int:
        for i in range(len(self.items)):
            if self.items[i].name == itemName:
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
        retString: str = BColors.OKGREEN + "There are exits: \n" + BColors.ENDC
        for place in self.links:
            retString += "\tto the "
            retString += place.get_direction() + ", "
            retString += place.get_location().get_name()
            retString += "\n"
        return retString

    def get_item_desc(self):
        itemCount = 0
        retString = BColors.OKGREEN + "Around you you see: \n" + BColors.ENDC
        for itemRef in self.items:
            if not itemRef.getVisible():
                continue
            retString += "\t"
            retString += itemRef.getDesc()
            retString += "\n"
            itemCount += 1
        if itemCount == 0:
            return BColors.OKGREEN + "There is nothing of interest around you\n" + BColors.ENDC
        return retString

    def get_actor_desc(self):
        actorCount = 0
        retString = ""
        for actor in self.actors:
            if not actor.getVisible():
                continue
            retString += "\t"
            retString += actor.getName() + ": "
            retString += actor.getDesc()
            retString += "\n"
            actorCount += 1

        if actorCount == 0:
            return BColors.OKGREEN + "You are alone\n" + BColors.ENDC
        if actorCount == 1:
            retString = BColors.OKGREEN + "There is someone here: \n" + BColors.ENDC + retString
        else:
            retString = BColors.OKGREEN + "There are people here: \n" + BColors.ENDC + retString
        return retString

    def add_link(self, location, direction):
        self.links.append(link(location, direction))

    def add_actor(self, person):
        self.actors.append(person)

    def get_actor(self, actorName):
        for actor in self.actors:
            if actor.getName() == actorName and actor.getVisible():
                return actor
        return None

    def get_item(self, itemName):
        for itemRef in self.items:
            if itemRef.getName() == itemName:
                return itemRef
        return None

    def add_event(self, eventRef):
        self.events.append(eventRef)

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

    def __init__(self, startLocation, startingKeys):
        self.location = startLocation
        self.inventory: List[Item] = []
        self.conditions: List[str] = []
        self.keyList = startingKeys

    def get_location(self):
        return self.location

    # get the index of an item in the players inventory, or None if it doesnt exist
    def get_inventory_index(self, itemName: str) -> int:
        for i in range(len(self.inventory)):
            if self.inventory[i].name == itemName:
                return i

    def get_inventory(self):
        return self.inventory

    # returns 1 if success, None if failure
    def pickup(self, itemName):
        # find item in room
        itemIndex = self.location.get_items_index(itemName)

        # if item is in current location, remove from room, add to inventory
        if itemIndex is not None:

            itemRef = self.location.get_item_ref(itemIndex)
            if not itemRef.getPickupable():
                return None

            self.location.remove_item(itemIndex)
            self.add_to_inventory(itemRef)
            self.add_key(itemRef.getPickupKey())

        # return item
        return itemIndex

    # return index of item removed, None if item not there
    def drop(self, itemName):
        itemIndex = self.get_inventory_index(itemName)
        if itemIndex is not None:
            itemRef = self.remove_from_inventory(itemIndex)
            self.location.add_item(itemRef)
        return itemIndex

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
        retString = BColors.OKGREEN + "You have on you: \n" + BColors.ENDC
        if len(self.inventory) == 0:
            return "you feel sad, for there is nothing in your pockets. "
        for thing in self.inventory:
            retString += thing.getInvDesc()
            retString += "\n"
        return retString

    def move(self, direction):
        links = self.location.get_links()
        for place in links:
            if place.get_direction() == direction:
                self.location = place.get_location()
                return self.look_around()
        return None

    def get_actor(self, actorName):
        return self.location.get_actor(actorName)

    def talk(self, actor, topic):
        if not actor.checkTopic(topic, self.get_keys()):
            return actor.get_name() + " does not know about this."
        retString = actor.get_name() + ": " + actor.speakTopic(topic)
        giveKeys, takeKeys = actor.giveDialogueKeys(topic)
        for key in giveKeys:
            self.add_key(key)
        for key in takeKeys:
            self.remove_key(key)

        return retString

    def look_around(self):
        retString = ""
        retString += self.get_location().get_desc() + "\n\n"
        retString += self.get_location().get_links_desc() + "\n"
        retString += self.get_location().get_actor_desc() + "\n"
        retString += self.get_location().get_item_desc()

        return retString


class link:
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

    def __init__(self, playerRef):
        self.player = playerRef
        self.commandList = []

    def split_commands(self, commandStr):
        self.commandList = commandStr.split(" ") + ["", "", "", ""]

    def parse_commands(self, commandStr):
        self.split_commands(commandStr)
        self.strip_commands()
        verb = self.identify_verb()
        dObject = self.identify_object(verb)
        self.commandList[0] = verb
        self.commandList[1] = dObject
        return self.commandList

    def identify_verb(self):
        # look at first word, see if it matches any of the known verbs
        verb = self.commandList[0]
        bestVerb = ""
        for key, testVerbs in self.verbs.items():
            if verb in testVerbs:
                bestVerb = key
                if bestVerb == "direction":
                    bestVerb = "move"
                    self.commandList.insert(0, "")
                break
        return bestVerb

    def identify_object(self, verb):
        dObject = self.commandList[1]
        if verb == "move":
            if dObject == "n":
                dObject = "north"
            if dObject == "s":
                dObject = "south"
            if dObject == "e":
                dObject = "east"
            if dObject == "w":
                dObject = "west"
            if dObject == "u":
                dObject = "up"
            if dObject == "d":
                dObject = "down"
        # based on verb do different things
        return dObject

    def collect_entity_list(self):
        # get entities in location
        curLocation = self.player.get_location()
        entityList = curLocation.get_item_list()
        entityList += curLocation.get_actors_list()

        # get items in player inventory
        entityList += self.player.get_inventory()

        pass

    def collect_entities_from_entity(self, entityRef):
        returnList = [entityRef]
        inventoryList = entityRef.get_inventory()
        for inventoryItem in inventoryList:
            returnList += self.collect_entities_from_entity(inventoryItem)
        return returnList

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
        # self.playerModel = [0.51087279, 0.22050487, 0.4063116, 0.713533420, 0.08517401]
        self.playerModel = [0]
        self.build_scenarios(["cat.json", "example.json"])
        pass

    def build_scenarios(self, fileList):
        for file in fileList:
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
    startLocation: str
    jsonData: Dict

    def __init__(self, file_name="example.json"):
        with open(file_name) as f:
            self.jsonData = json.load(f)
        self.roomList = {}
        self.actorList = []
        self.itemList = []
        self.eventList = []
        self.startLocation = "template"

        self.room_compile()
        self.link_builder()

    def room_compile(self):
        for roomJSON in self.jsonData["rooms"]:
            name = roomJSON["name"]
            if "startLocation" in roomJSON:
                self.startLocation = name
            newRoom = Room(name,
                           roomJSON["desc"] if "desc" in roomJSON else "",
                           roomJSON["initDesc"] if "initDesc" in roomJSON else ""
                           )

            if "items" in roomJSON:
                for itemJSON in roomJSON["items"]:
                    newRoom.add_item(self.item_create(itemJSON))
            if "actors" in roomJSON:
                for actorJSON in roomJSON["actors"]:
                    newRoom.add_actor(self.actor_create(actorJSON))
            if "events" in roomJSON:
                for eventJSON in roomJSON["events"]:
                    newRoom.add_event(self.event_create(eventJSON))

            self.roomList[name] = newRoom

    def link_builder(self):
        for roomJSON in self.jsonData["rooms"]:
            if "links" in roomJSON:
                linkingRoom = self.roomList[roomJSON["name"]]
                for linkJSON in roomJSON["links"]:
                    linkingRoom.add_link(self.roomList[linkJSON["roomName"]], linkJSON["direction"])

    def actor_create(self, actor_json):
        newActor = Actor(
            actor_json["name"] if "name" in actor_json else "",
            actor_json["initDesc"] if "initDesc" in actor_json else "",
            actor_json["desc"] if "desc" in actor_json else ""
        )
        if "hidden" in actor_json:
            newActor.hide()

        if "dialogues" in actor_json:
            for dialogueJSON in actor_json["dialogues"]:
                newActor.addDialogue(
                    Dialogue(dialogueJSON["topic"] if "topic" in dialogueJSON else "",
                             dialogueJSON["text"] if "text" in dialogueJSON else "they stay silent",
                             dialogueJSON["whitelist"] if "whitelist" in dialogueJSON else "",
                             dialogueJSON["blacklist"] if "blacklist" in dialogueJSON else "",
                             dialogueJSON["key"] if "key" in dialogueJSON else "",
                             dialogueJSON["unkey"] if "unkey" in dialogueJSON else ""
                             )
                )

        self.actorList.append(newActor)
        return newActor

    def item_create(self, item_json):
        newItem = Item(
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
            newItem.hide()

        self.itemList.append(newItem)
        return newItem

    def event_create(self, event_json):
        newEvent = event(
            event_json["whitelist"] if "whitelist" in event_json else "",
            event_json["blacklist"] if "blacklist" in event_json else "",
            event_json["key"] if "key" in event_json else "",
            event_json["unkey"] if "unkey" in event_json else "",
            event_json["text"] if "text" in event_json else "",
            event_json["type"] if "type" in event_json else ""
        )
        if "makeVisible" in event_json:
            for visibleJSON in event_json["makeVisible"]:
                newEvent.addMakeVisible([
                    visibleJSON["name"] if "name" in visibleJSON else "",
                    visibleJSON["class"] if "class" in visibleJSON else ""
                ])
        if "makeInvisible" in event_json:
            for visibleJSON in event_json["makeInvisible"]:
                newEvent.addMakeInvisible([
                    visibleJSON["name"] if "name" in visibleJSON else "",
                    visibleJSON["class"] if "class" in visibleJSON else ""
                ])

        self.eventList.append(newEvent)
        return newEvent

    def get_weights(self):
        return self.jsonData["weights"] if "weights" in self.jsonData else [0, 0, 0, 0, 0]

    def get_player(self):
        startingKeys = self.jsonData["startingKeys"] if "startingKeys" in self.jsonData else []
        return Player(self.roomList[self.startLocation], startingKeys)


class Display:
    location: Room
    player: Player

    # pass in arbitrary objects and get proper formatting for their description.
    def __init__(self):
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
    # this is to act as a template, or interface between actually printing things out and using curses.
    pass


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
                print(actor.getTopics(player.get_keys()))
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
    for eventRef in events:
        if eventRef.getType() == event_type:
            # print(player.getKeys())
            # print(eventRef.whitelistKeys, eventRef.blacklistKeys)

            if eventRef.checkAllowed(player.get_keys()):
                # print("event activated!")
                print(eventRef.activate(player))
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
        print("\n\n\n\n\n\n\n\n")


main()
