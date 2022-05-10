# Rasa Chatbot - PokeBot

## Introduction
Pokebot is a chatbot developed using the Rasa 3.x framework. It leverages the rasa framework to help a user with their Pokemon related queries. 

## Run instructions
- install all the dependencies mentioned in the requirements.txt
- replace the mongoDB connection string in actions.py (the current string will remain active till 05/30/2022)
- To run the chatbot in CLI
    - if using a virtual environment like venv, put in ```source venv/bin/activate``` to start the virtual environment.
    - In the same terminal and run ```rasa shell``` to start the chatbot
    - In another terminal, start the rasa actions server by using ```rasa run actions```
- To run the chatbot locally and then expose the IP+port you can use [ngrok](https://ngrok.com/).

## Recommended story path
1. "Hi"
2. "I'm good"
2. "Call me Ujjwal"
3. "Show me a pikachu"
4. "Tell me more about it"
5. "Add that to my favs"
6. "What are its powers"
7. "What are dragon type pokemons"
8. "Tell me more about that"
9. "Add that to my favorites"
10. "Show me my favorites"

- - - -
## Current Issues
- When asking to add a pokemon not in the original 151 list to the database favorites, it fails to identify the pokemon and inserts the last pokemon available in the slot.
- Ocasionally bugs out and doesn't give any output on the command "I need help"
