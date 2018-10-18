from __future__ import annotations
import json

from entity import *
from event import *
from typing import List, Dict


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class room:
    links = []
    items: List[item]
    actors: List[actor]
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

    def addItem(self, itemRef):
        self.items.append(itemRef)

    def removeItem(self, index: int):
        return self.items.pop(index)

    def getItemsIndex(self, itemName: str) -> int:
        for i in range(len(self.items)):
            if self.items[i].name == itemName:
                return i

    def getItemRef(self, index):
        return self.items[index]

    def getItemList(self):
        return self.items

    def getActorsList(self):
        return self.actors

    def getDesc(self):
        return self.description

    def getLinksDesc(self):
        if len(self.links) == 0:
            return "you are stuck here\n"
        retString: str = bcolors.OKGREEN + "There are exits: \n" + bcolors.ENDC
        for place in self.links:
            retString += "\tto the "
            retString += place.getDirection() + ", "
            retString += place.getLocation().getName()
            retString += "\n"
        return retString

    def getItemDesc(self):
        itemCount = 0
        retString = bcolors.OKGREEN + "Around you you see: \n" + bcolors.ENDC
        for itemRef in self.items:
            if not itemRef.getVisible():
                continue
            retString += "\t"
            retString += itemRef.getDesc()
            retString += "\n"
            itemCount += 1
        if itemCount == 0:
            return bcolors.OKGREEN + "There is nothing of interest around you\n" + bcolors.ENDC
        return retString

    def getActorDesc(self):
        actorCount = 0
        retString = ""
        for actorRef in self.actors:
            if not actorRef.getVisible():
                continue
            retString += "\t"
            retString += actorRef.getName() + ": "
            retString += actorRef.getDesc()
            retString += "\n"
            actorCount += 1

        if actorCount == 0:
            return bcolors.OKGREEN + "You are alone\n" + bcolors.ENDC
        if actorCount == 1:
            retString = bcolors.OKGREEN + "There is someone here: \n" + bcolors.ENDC + retString
        else:
            retString = bcolors.OKGREEN + "There are people here: \n" + bcolors.ENDC + retString
        return retString

    def addLink(self, location, direction):
        self.links.append(link(location, direction))

    def addActor(self, person):
        self.actors.append(person)

    def getActor(self, actorName):
        for actorRef in self.actors:
            if actorRef.getName() == actorName and actorRef.getVisible():
                return actorRef
        return None

    def getItem(self, itemName):
        for itemRef in self.items:
            if itemRef.getName() == itemName:
                return itemRef
        return None

    def addEvent(self, eventRef):
        self.events.append(eventRef)

    def getEvents(self):
        return self.events

    def getLinks(self):
        return self.links

    def getItems(self):
        return self.items

    def getName(self):
        return self.name


class player:
    location: room
    inventory: List[item]
    conditions: List[str]
    keyList: List[str]

    def __init__(self, startLocation, startingKeys):
        self.location = startLocation
        self.inventory: List[item] = []
        self.conditions: List[str] = []
        self.keyList = startingKeys

    def getLocation(self):
        return self.location

    # get the index of an item in the players inventory, or None if it doesnt exist
    def getInventoryIndex(self, itemName: str) -> int:
        for i in range(len(self.inventory)):
            if self.inventory[i].name == itemName:
                return i

    def getInventory(self):
        return self.inventory

    # returns 1 if success, None if failure
    def pickup(self, itemName):
        # find item in room
        itemIndex = self.location.getItemsIndex(itemName)

        # if item is in current location, remove from room, add to inventory
        if itemIndex is not None:

            itemRef = self.location.getItemRef(itemIndex)
            if not itemRef.getPickupable():
                return None

            self.location.removeItem(itemIndex)
            self.addToInventory(itemRef)
            self.addKey(itemRef.getPickupKey())

        # return item
        return itemIndex

    # return index of item removed, None if item not there
    def drop(self, itemName):
        itemIndex = self.getInventoryIndex(itemName)
        if itemIndex is not None:
            itemRef = self.removeFromInventory(itemIndex)
            self.location.addItem(itemRef)
        return itemIndex

    def addToInventory(self, thing):
        # append item to inventory list
        self.inventory.append(thing)
        pass

    def removeFromInventory(self, index):
        return self.inventory.pop(index)

    def addKey(self, key):
        if key not in self.keyList:
            self.keyList.append(key)
            return len(self.keyList)
        return None

    def removeKey(self, key):
        if key in self.keyList:
            self.keyList.remove(key)
            return len(self.keyList)
        return None

    def getKeys(self):
        return self.keyList

    def displayInventory(self):
        retString = bcolors.OKGREEN + "You have on you: \n" + bcolors.ENDC
        if len(self.inventory) == 0:
            return "you feel sad, for there is nothing in your pockets. "
        for thing in self.inventory:
            retString += thing.getInvDesc()
            retString += "\n"
        return retString

    def move(self, direction):
        links = self.location.getLinks()
        for place in links:
            if place.getDirection() == direction:
                self.location = place.getLocation()
                return self.lookAround()
        return None

    def getActor(self, actorName):
        return self.location.getActor(actorName)

    def talk(self, actorRef, topic):
        if not actorRef.checkTopic(topic, self.getKeys()):
            return actorRef.getName() + " does not know about this."
        retString = actorRef.getName() + ": " + actorRef.speakTopic(topic)
        giveKeys, takeKeys = actorRef.giveDialogueKeys(topic)
        for key in giveKeys:
            self.addKey(key)
        for key in takeKeys:
            self.removeKey(key)

        return retString

    def lookAround(self):
        retString = ""
        retString += self.getLocation().getDesc() + "\n\n"
        retString += self.getLocation().getLinksDesc() + "\n"
        retString += self.getLocation().getActorDesc() + "\n"
        retString += self.getLocation().getItemDesc()

        return retString


class link:
    # room
    direction: str
    location: room

    def __init__(self, location, direction):
        self.location = location
        self.direction = direction

    def getRoomName(self):
        return self.location.getName()

    def getLocation(self):
        return self.location

    def getDirection(self):
        return self.direction


class parser:
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
    player: player

    commandList: List[str]

    def __init__(self, playerRef):
        self.player = playerRef
        self.commandList = []

    def splitCommands(self, commandStr):
        self.commandList = commandStr.split(" ") + ["", "", "", ""]

    def parseCommands(self, commandStr):
        self.splitCommands(commandStr)
        self.stripCommands()
        verb = self.identifyVerb()
        dObject = self.identifyObject(verb)
        self.commandList[0] = verb
        self.commandList[1] = dObject
        return self.commandList

    def identifyVerb(self):
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

    def identifyObject(self, verb):
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

    def collectEntityList(self):
        # get entities in location
        curLocation = self.player.getLocation()
        entityList = curLocation.getItemList()
        entityList += curLocation.getActorsList()

        # get items in player inventory
        entityList += self.player.getInventory()

        pass

    def collectEntitiesFromEntity(self, entityRef):
        returnList = [entityRef]
        inventoryList = entityRef.getInventory()
        for inventoryItem in inventoryList:
            returnList += self.collectEntitiesFromEntity(inventoryItem)
        return returnList

    # strip commandList of unnecessary words?
    def stripCommands(self):
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


class scenarioBuilder:
    scenarioList: List[scenario]
    playerModel: List[float]

    def __init__(self):
        self.scenarioList = []
        # self.playerModel = [0.51087279, 0.22050487, 0.4063116, 0.713533420, 0.08517401]
        self.playerModel = [0]
        self.buildScenarios(["cat.json", "example.json"])
        pass

    def buildScenarios(self, fileList):
        for file in fileList:
            self.scenarioList.append(scenario(file))

    def chooseScenario(self):
        if len(self.scenarioList) == 0:
            return None
        scene = min(self.scenarioList, key=lambda x: abs(sum(x.getWeights()) - sum(self.playerModel)))
        self.scenarioList.remove(scene)
        return scene


class scenario:
    roomList: Dict[str, room]
    eventList: List
    actorList: List
    itemList: List
    startLocation: str
    jsonData: Dict

    def __init__(self, fileName="example.json"):
        with open(fileName) as f:
            self.jsonData = json.load(f)
        self.roomList = {}
        self.actorList = []
        self.itemList = []
        self.eventList = []
        self.startLocation = "template"

        self.roomCompile()
        self.linkBuilder()

    def roomCompile(self):
        for roomJSON in self.jsonData["rooms"]:
            name = roomJSON["name"]
            if "startLocation" in roomJSON:
                self.startLocation = name
            newRoom = room(name,
                           roomJSON["desc"] if "desc" in roomJSON else "",
                           roomJSON["initDesc"] if "initDesc" in roomJSON else ""
                           )

            if "items" in roomJSON:
                for itemJSON in roomJSON["items"]:
                    newRoom.addItem(self.itemCreate(itemJSON))
            if "actors" in roomJSON:
                for actorJSON in roomJSON["actors"]:
                    newRoom.addActor(self.actorCreate(actorJSON))
            if "events" in roomJSON:
                for eventJSON in roomJSON["events"]:
                    newRoom.addEvent(self.eventCreate(eventJSON))

            self.roomList[name] = newRoom

    def linkBuilder(self):
        for roomJSON in self.jsonData["rooms"]:
            if "links" in roomJSON:
                linkingRoom = self.roomList[roomJSON["name"]]
                for linkJSON in roomJSON["links"]:
                    linkingRoom.addLink(self.roomList[linkJSON["roomName"]], linkJSON["direction"])

    def actorCreate(self, actorJSON):
        newActor = actor(
            actorJSON["name"] if "name" in actorJSON else "",
            actorJSON["initDesc"] if "initDesc" in actorJSON else "",
            actorJSON["desc"] if "desc" in actorJSON else ""
        )
        if "hidden" in actorJSON:
            newActor.hide()

        if "dialogues" in actorJSON:
            for dialogueJSON in actorJSON["dialogues"]:
                newActor.addDialogue(
                    dialogue(dialogueJSON["topic"] if "topic" in dialogueJSON else "",
                             dialogueJSON["text"] if "text" in dialogueJSON else "they stay silent",
                             dialogueJSON["whitelist"] if "whitelist" in dialogueJSON else "",
                             dialogueJSON["blacklist"] if "blacklist" in dialogueJSON else "",
                             dialogueJSON["key"] if "key" in dialogueJSON else "",
                             dialogueJSON["unkey"] if "unkey" in dialogueJSON else ""
                             )
                )

        self.actorList.append(newActor)
        return newActor

    def itemCreate(self, itemJSON):
        newItem = item(
            itemJSON["name"] if "name" in itemJSON else "",
            itemJSON["initDesc"] if "initDesc" in itemJSON else "",
            itemJSON["invDesc"] if "invDesc" in itemJSON else "",
            itemJSON["desc"] if "desc" in itemJSON else "",
            itemJSON["weight"] if "weight" in itemJSON else 0.0,
            itemJSON["smell"] if "smell" in itemJSON else "",
            itemJSON["taste"] if "taste" in itemJSON else "",
            itemJSON["size"] if "size" in itemJSON else "",
            itemJSON["pickupable"] if "pickupable" in itemJSON else False,
            itemJSON["pickupKey"] if "pickupKey" in itemJSON else ""
        )
        if "hidden" in itemJSON:
            newItem.hide()

        self.itemList.append(newItem)
        return newItem

    def eventCreate(self, eventJSON):
        newEvent = event(
            eventJSON["whitelist"] if "whitelist" in eventJSON else "",
            eventJSON["blacklist"] if "blacklist" in eventJSON else "",
            eventJSON["key"] if "key" in eventJSON else "",
            eventJSON["unkey"] if "unkey" in eventJSON else "",
            eventJSON["text"] if "text" in eventJSON else "",
            eventJSON["type"] if "type" in eventJSON else ""
        )
        if "makeVisible" in eventJSON:
            for visibleJSON in eventJSON["makeVisible"]:
                newEvent.addMakeVisible([
                    visibleJSON["name"] if "name" in visibleJSON else "",
                    visibleJSON["class"] if "class" in visibleJSON else ""
                ])
        if "makeInvisible" in eventJSON:
            for visibleJSON in eventJSON["makeInvisible"]:
                newEvent.addMakeInvisible([
                    visibleJSON["name"] if "name" in visibleJSON else "",
                    visibleJSON["class"] if "class" in visibleJSON else ""
                ])

        self.eventList.append(newEvent)
        return newEvent

    def getWeights(self):
        return self.jsonData["weights"] if "weights" in self.jsonData else [0, 0, 0, 0, 0]

    def getPlayer(self):
        startingKeys = self.jsonData["startingKeys"] if "startingKeys" in self.jsonData else []
        return player(self.roomList[self.startLocation], startingKeys)


class display:
    location: room
    agent: player

    # pass in arbitrary objects and get proper formatting for their description.
    def __init__(self):
        pass

    def display(self):
        # confirm command
        self.display_command()
        # display any relevant events
        self.display_event()
        # print place description
        self.display_
        # exits

        # people

        # items

        pass
    # this is to act as a template, or interface between actually printing things out and using curses.
    pass

def act(command, agent):
    # do verb on object
    verb = command[0]
    target = command[1]

    if verb == "pickup":
        attempt = agent.pickup(target)
        if attempt is not None:
            print("you have picked up", target)
        else:
            print("you cannot pick that up")
    elif verb == "drop":
        attempt = agent.drop(target)
        if attempt is not None:
            print("you have dropped", target)
        else:
            print("you do not have that item in your pockets")
    elif verb == "move":
        attempt = agent.move(target)
        if attempt is None:
            print("there is nothing in that direction")
        else:
            eventListener("onEnter", agent)
    elif verb == "talk":
        topic = command[2]
        actorRef = agent.getActor(target)
        if topic == "":
            if actorRef is not None:
                print(actorRef.getTopics(agent.getKeys()))
            else:
                print("you talk into the aether to someone who isn't there")
        else:
            if actorRef is not None:
                print(agent.talk(actorRef, topic))
                print("")
            else:
                print("you talk into the aether to someone who isn't there")
    elif verb == "inventory":
        print(agent.displayInventory())
    elif verb == "look":
        print(agent.lookAround())

    elif verb == "use":
        # the target is activated and key might be given (which then would activate event?)
        pass
    elif verb == "examine":
        pass
    elif verb == "key":
        print(agent.getKeys())
    else:
        print("I do not understand that command")

    # basic interaction types


def eventListener(eventType, agent):
    events = agent.getLocation().getEvents()
    for eventRef in events:
        if eventRef.getType() == eventType:
            # print(agent.getKeys())
            # print(eventRef.whitelistKeys, eventRef.blacklistKeys)

            if eventRef.checkAllowed(agent.getKeys()):
                # print("event activated!")
                print(eventRef.activate(agent))
            # else:
            #     print("no event activated :(")


def winCondition(agent):
    # what is the win condition
    # when the player gets a win key!
    if "win" in agent.getKeys():
        print("you won!")
        print("next scenario!")
        agent.removeKey("win")
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

    dungeonMaster = scenarioBuilder()

    while True:
        scene = dungeonMaster.chooseScenario()
        if scene is None:
            print("you won the game! congrats.")
            exit(1)
        agent = scene.getPlayer()
        inParser = parser(agent)

        # have the player enter the room officially.
        eventListener("onEnter", agent)

        while not winCondition(agent):
            # TODO: implement pre/in/post act functions

            # current state of pre act function
            print(agent.lookAround())

            # input
            command = input("> ")
            commandArray = inParser.parseCommands(command)

            # interpret input
            # commandArray = parseInput(command, agent)
            # act on input and display
            act(commandArray, agent)
            eventListener("active", agent)

            # postAct(commandArray, agent)

        # give the player some blank space to look at
        print("\n\n\n\n\n\n\n\n")


main()
