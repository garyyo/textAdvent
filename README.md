# textAdvent
a text adventure that hopefully can leverage ai stuff to make it cool

# how it works (or will work...)
in a persistent town the player is given tasks. these tasks can be something as simple as slaying a dragon or as Zcomplicated as rescuing a lost cat. Each of these quests have different ways to complete them, wiht the goal not always staying in the same place. The cat could be in a tree, or in a bush, or may need to be summoned by a rain dance that makes it rain cats (though not dogs). But how do you know which of these will be the way that the quest is completed? The player will play, and as they play the computer will profile them and build an internal model. This player model will then be used by a system that will try to give the player the path that they will most enjoy. 

# The player model
currently the player model is the player's affinity towards certain actions. this method is incomplete atm.


# The drama manager?!?!?! (I might be wrong on this)
the drama manager(DM) has two parts. profiling the player to build a model of them, and predicting which path and quest the player will prefer based on said model. profiling the player is done by collecting data on their actions. this data comes from side objectives that the player may be able to interact with and main objectives that the player tries to follow. Side objectives can take the form of small objects that the player can interact with, without being explicetly told (e.g. turning off a fountain by interacting with it), or pursuing things that might be mentioned but arent going to benefit the completion of the quest (subsequently turning the on the fountain because it tells you to do so "before anyone notices"). (is the idea of this to try to figure out when the player is stuck and not making progress? or to find actions similar to the ones done, aka maybe the player hates talking to people but loves looking at things). The main objectives denote the players preference to one sort of story line. If a player starts to follow one quest path the DM will try to give options for the player to take to see if they want to go towards another path. if they take these options the DM is now more certain that the player prefers to take an actions similar to what they just did, and that they might prefer that sort of path going forward. 

the choices that the drama manager makes are to give the player some keys that will help describe their state. The story needs to be written in a way to leverage this system. if say a player is said to be "stuck" perhaps another path will open to allow them to explore more in another that area. This requires these paths to be intertwined, but not reliant on each other. 

```
p1    q1
p2 -> q2
p3<-  q3
p4  \-q4
p5    q5
```

# The code simply explained.
there are a few concepts that are used in the text adventure: player, room, entity, and events. 

Starting with players, this is how the player is represented. players can move from room to room, pick up certain entities, and they have an hidden keyring of keys (list of strings) that tracks their progress through the game. This keyring is important for later. Players also have gold, the local currency, that they can use to buy things (WIP).

Rooms are places that things can exist in. The player will always be in a room, entities are always assigned a room, events always take place in rooms, you cannot be not in a room. but rooms dont have to be litteral rooms. a street corner can be considered a room, so can the top of a tree, or even a bathroom. these are all "rooms" in the code sense. maybe location is a better term for it.

Rooms have links between them. to get from one room to the next you have to move by referencing the link, e.g. "go north". Links can be hidden so that they arent available to the player if the quest needs to keep the player trapped, or to allow the player to explore a new place they just didnt notice before.

Entities are the most complicated of them all. There are several types of entities: items, backgrounds, and actors. items have the possiblity to be picked up, placed down, and interacted with. backgrounds can only be itneracted with. actors can be interacted with and spoken too. actors can have dialogues which are a type of event. they use these dialogues to interact with players. interactions with things are also handled with events. 

Events are the core of the system. Events are how things happen, they can print out text, give or take keys from the player the, and hide and show entites and links. Events also have a whitelist and a blacklist. If the player has a key that is on the blacklist, the event IS NOT activated. if they are missing a key that is on the whitelist, the event is again NOT activate. only if the player has none of the keys on the blacklist and all the keys on the whitelist is the event actiavted. whitelists and blacklists can be blank. event can be assigned to the room, an entity, or as dialogue on actors. Events also have several different types. onEnter will trigger on entering a room, active will trigger every time the player takes an action, onUse for when the player uses the use command on an entity, onLook for the look command, and so on. 

white and black lists lead to a couple interesting capabilities. if an event has a key that it gives on its blacklist, the event will only trigger once, until that key is taken away by something else. or if the player gets new info from someone it could lock out dialogue for false info. Dialogues can take a sort of tree structure where one dialogue leads to several others (by whitelisting the key the last one  gives, and blacklilsting the key it itself gives).

Dialogues themselves work by way of topics. the player will type `talk <actor>` and the system will display the available topics you can talk about. then the player can type `talk <actor> <topic>` and the event for that topic will be activated. 



