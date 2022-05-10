from typing import Any, Text, Dict, List
from unicodedata import name

from numpy import disp

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from pymongo import MongoClient
from pymongo import ReturnDocument

import random
import re
import requests

connection_string = "mongodb+srv://admin:admin@cluster0.j7xf8.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client.chatbot
print("Connection Established\n")
print(db.list_collection_names())
userdata = db.userdata

url = "https://pokeapi.co/api/v2/"
def get_request(end_point,item=None, params=None):
  resp = requests.get(url+end_point+"/"+(str(item) if item else ""), params)
  return resp.json() if resp else None

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []

class ActionFindPokemon(Action):
    def name(self) -> Text:
        return "action_find_pokemon"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get pokemon name from the bot
        pokemon = next(tracker.get_latest_entity_values("pokemon"),None)
        if pokemon=="pokemon" or not pokemon:
            dispatcher.utter_message(text="Uh oh, couldn't find any pokemon with that name!")
            return []
        result = get_request("pokemon",pokemon.lower() if pokemon!="pokemon" else "")
        if not result or pokemon=="":
            dispatcher.utter_message(text="Uh oh, couldn't find any pokemon with that name!")
            return []
        
        # send the pokemon info to the bot
        returningText = "Pokemon requested: " +result['name']+"\n"
        
        print(pokemon)
        print(returningText)
        # CHANGES MADE HERE. REVERT TO FRONT DEFAULT IF SOMETHING BREAKS
        dispatcher.utter_message(text = returningText, image = result["sprites"]["other"]["official-artwork"]['front_default'])

        return []

class ActionFindPokemonType(Action):
    def name(self) -> Text:
        return "action_find_pokemon_type"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get type name from the bot
        pokemon_type = next(tracker.get_latest_entity_values("pokemonType"),None)
        if not pokemon_type:
            dispatcher.utter_message(text="Uh oh, couldn't find any pokemon type in your message!")
            return []
        pokemon_type = pokemon_type.split(" ")[0]
         
        # Get type info
        result = get_request("type",pokemon_type.lower() if pokemon_type!="pokemon" else "fire")
        if not result:
            dispatcher.utter_message(text="Uh oh, couldn't find any pokemon type with that name!")
            return []
        

        # Finding a random pokemon of this type 
        randPokemon =  result['pokemon'][random.randrange(0,len(result['pokemon'])-1)]['pokemon']['url']
        pokemonNumber = re.findall(r'\d+', randPokemon)
        pokemon = get_request("pokemon",pokemonNumber[1].lower())
        # SlotSet(key = "pokemon_slot",value = pokemon['name'])

        # Creating the return string
        returningText = "Type requested: " + result['name'] + " type\nType relations for this type:"

        damage_relations = result["damage_relations"].keys()
        temp = "\n"
        for relation in damage_relations:
            list_of_pokemon = result['damage_relations'][relation]
            if len(list_of_pokemon)>0:
                temp += relation + ": \n"
                for i,x in enumerate(list_of_pokemon):
                    temp += str(i+1)+". "+x['name']+"\n"

        temp+="\nPokemon in the picture: "+pokemon['name']
        # send the pokemon info to the bot
        dispatcher.utter_message(text = returningText+temp, image = pokemon["sprites"]["front_default"])
        # dispatcher.utter_message(text = pokemon_type)

        return [SlotSet(key = "pokemon_slot",value = pokemon['name'])]
    
class ActionFromContext(Action):
    def name(self) -> Text:
        return "action_from_context"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        pokemon = tracker.get_slot("pokemon_slot")
        print(pokemon)
        # Get pokemon
        if pokemon=="pokemon":
            dispatcher.utter_message(text="Uh oh, couldn't find any pokemon with that name!")
            return []

        result = get_request("pokemon",pokemon.lower() if pokemon!="pokemon" else "")
        if not result or pokemon=="":
            dispatcher.utter_message(text="Uh oh, couldn't find any pokemon with that name!")
            return []
        

        # send the pokemon info to the bot
        returningText = "Pokemon requested: " + result['name'] + "\nPokemon height: "
        returningText += str(result["height"]) + "\nPokemon weight: " + str(result["weight"])

        returningText += "\nPokemon Stats: \n"
        for i,stats in enumerate(result['stats']):
            returningText += stats['stat']["name"] + ": " + str(stats['base_stat']) + '\n'

        returningText += "\nPokemon Type: \n"
        for i,poketype in enumerate(result['types']):
            returningText+=str(i+1)+". "+poketype["type"]["name"] + "\n"

        returningText+="\nPokemon Abilities:\n"
        for i,ability in enumerate(result["abilities"]):
            returningText+=str(i+1)+". "+ability["ability"]["name"] + "\n"

        returningText+='This is what the "Shiny" variant of '+pokemon.title()+' looks like!'
        print(returningText)
        dispatcher.utter_message(text = returningText, image = result["sprites"]["front_shiny"])
        return []

class ActionPokemonMoves(Action):
    def name(self) -> Text:
        return "action_pokemon_moves"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # pokemon = next(tracker.get_latest_entity_values("pokemon"),None)
        pokemon = tracker.get_slot("pokemon_slot")
        print(pokemon)
        # Get pokemon
        if pokemon=="pokemon" or pokemon=="" or not pokemon:
            dispatcher.utter_message(text="Uh oh, couldn't find any pokemon with that name!")
            return []

        result = get_request("pokemon",pokemon.lower() if pokemon!="pokemon" else "")
        if not result or pokemon=="":
            dispatcher.utter_message(text="Uh oh, couldn't find any pokemon with that name!")
            return []

        returningText = pokemon.title()+" can learn 4 out of "+str(len(result['moves']))+" moves at a time.\nHere are a few examples!\n"
        for i in range(0,4):
            randpokemon = random.randint(0,len(result["moves"])-1)
            returningText+= str(i+1) + ". " + result["moves"][randpokemon]["move"]["name"]+"\n"

        dispatcher.utter_message(text=returningText)
        return []

class AddToFav(Action):
    def name(self) -> Text:
        return "action_add_fav"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user = tracker.sender_id
        query = {'userID':user}
        result = userdata.find_one(query)

        pokemon = tracker.get_slot("pokemon_slot")
        if pokemon == "": # no pokemon in the slot
            message = "No pokemon queried yet."
            dispatcher.utter_message(text = message)
            return []

        if not result:
            # create new entry
            userdata.insert_one({"userID":user,"favs":[pokemon]})
            temp = userdata.find_one(query)
            message = "Pokemon added!\nCurrent favorites:\n"
            for i,poke in enumerate(temp["favs"]):
                message+=str(i+1) + ". " + poke.title() + "\n"
            dispatcher.utter_message(text = message)
            return []
        else:
            if "favs" not in result:
                userdata.find_one_and_update(query, {"$set":{"favs":[pokemon]}})
                # pokemon added display it now
                temp = userdata.find_one(query)
                message = "Pokemon added!\nCurrent favorites:\n"
                for i,poke in enumerate(temp["favs"]):
                    message+=str(i+1) + ". " + poke.title() + "\n"
                dispatcher.utter_message(text = message)
                return []
            # update
            if pokemon not in result["favs"]:
                temp = userdata.find_one_and_update(query, {'$push': {"favs":pokemon}}, upsert=True, return_document = ReturnDocument.AFTER)
                message = "Pokemon added!\nCurrent favorites:\n"
                for i,poke in enumerate(temp["favs"]):
                    message+=str(i+1) + ". " + poke.title() + "\n"
                dispatcher.utter_message(text = message)
                return []
            else:
                message = "Pokemon already in favorites.\nCurrent favorites are:\n"
                for i,poke in enumerate(result["favs"]):
                    message+=str(i+1) + ". " + poke.title() + "\n"
                dispatcher.utter_message(text = message)
                return []    

        return[]

class ShowFav(Action):
    def name(self) -> Text:
        return "action_show_fav"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user = tracker.sender_id
        query = {'userID':user}
        result = userdata.find_one(query)
        if result:
            message = "Okay, here are your favorite pokemons!\n"
            message += "Current favorite pokemons:\n"
            if len(result["favs"])>0:
                for i,poke in enumerate(result["favs"]):
                    message+=str(i+1) + ". " + poke.title() + "\n"
                message+="Total number of favorite pokemon: " + str(len(result["favs"]))
            else:
                message+="No pokemons added to favorites."
        else:
            message="No pokemons added to favorites."
        dispatcher.utter_message(text = message)
        
        return []

class SaveName(Action):
    def name(self) -> Text:
        return "action_save_name"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user = tracker.sender_id
        query = {'userID':user}
        result = userdata.find_one(query)
        user_name = next(tracker.get_latest_entity_values("username"),None)
        print(user_name,user)
        if not result:
            userdata.insert_one({"userID":user,"name":user_name})
            
        else:
            temp = userdata.find_one_and_update({"userID":user},{"$set":{"name":user_name}}, return_document = ReturnDocument.AFTER)
            message = "Name set to "+str(temp['name'])
            dispatcher.utter_message(text = message)
            return []
        # message = "Name set to: " + temp["name"] +"\n"
        # message += "Current favorite pokemons:\n"
        # for i,poke in enumerate(temp["favs"]):
        #     message+=str(i+1) + ". " + poke.title() + "\n"
        message = "Name set to "+str(user_name)
        dispatcher.utter_message(text = message)
        return []

class ShowName(Action):
    def name(self) -> Text:
        return "action_show_name"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user = tracker.sender_id
        query = {'userID':user}
        result = userdata.find_one(query)
        user_name = tracker.get_slot("user_name")
        if not result:
            message = "User data not saved. Please save your name first!"
            dispatcher.utter_message(text = message)
            return []
        
        if "name" not in result:
            message = "You haven't given me a name yet!"
            dispatcher.utter_message(text = message)
            return []

        print("name requested")
        message = "Your name is " + str(result["name"])
        dispatcher.utter_message(text = message)

        return []
    
class RemoveFavs(Action):
    def name(self) -> Text:
        return "action_remove_fav"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # grabbing the index to remove
        remove_id = next(tracker.get_latest_entity_values("removeId"),None)
        user = tracker.sender_id
        query = {'userID':user}
        result = userdata.find_one(query)

        if not remove_id:
            dispatcher.utter_message(text="That number doesn't correspond with a Pokemon!")
            return []

        if not result:
            dispatcher.utter_message(text="No favorites found!")
            return []
        
        if "favs" not in result:
            dispatcher.utter_message(text="No favorites found!")
            return []

        pokemon = result["favs"].pop(remove_id-1)
        temp = userdata.find_one_and_update({"userID":user},{"$set":{"favs":result["favs"]}}, return_document = ReturnDocument.AFTER)

        message = "Okay! Removing "+pokemon+" from your favorites!\nCurrent Favorite Pokemons are:\n"
        for i,poke in enumerate(temp["favs"]):
            message+=str(i+1) + ". " + poke.title() + "\n"

        dispatcher.utter_message(text=message)
        return []