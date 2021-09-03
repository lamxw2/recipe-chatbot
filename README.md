# CoCo - The Cooking Companion

A chatbot created as a final year school project, with the aim of educating users about a healthy diet, and recommend healthy recipes according to ingredients and dish type. A minimal implementation was created for chit chat.

A typical conversation starts with greeting CoCo, then asking about a healthy diet, types of healthy food, or obtaining recipe suggestions.

# About the Chatbot
CoCo was created on the Rasa platform.

Data for the chatbot about healthy eating and ingredient querying was manually obtained from the USDA Dietary Guidelines for Americans (2020-2025) and NHS Eatwell Guide. I read through the guides thoroughly to compile the information into small, easy-to-read chunks to be used by CoCo in its responses.

The recipe dataset was obtained from https://www.kaggle.com/hugodarwood/epirecipes.

# Using CoCo
## Getting Started

The user can ask CoCo for help on how to use the chatbot.<br>
![Image of greeting](screenshots\greet.png)

## Healthy Eating

The user can ask CoCo about what a healthy diet consists of, how much of a food group they should eat, and types of food within a food group.

Examples of conversations about a healthy diet:

Asking about a basic healthy diet<br>
![Image of generic balanced diet](screenshots\balanced_diet_generic.png)<br>

Asking about how much chicken to have in a healthy diet<br>
![Image of balanced diet about protein](screenshots\balanced_diet_protein.png)<br>

Asking about how much milk to have in a healthy diet<br>
![Image of balaned diet about dairy](screenshots\balanced_diet_dairy.png)<br>

Asking if ice-cream is healthy<br>
![Image of balaned diet about dairy](screenshots\ice-cream.png)<br>

Example of types of healthy food:

Asking about types of cheeses<br>
![Image of examples of cheese](screenshots\cheese_examples.png)

Asking if salmon is a type of oily fish<br>
![Image of types of oily fish](screenshots\salmon_oily_fish.png)

Asking about other types of dark-green vegetables<br>
![Image of types of dark green vegetables](screenshots\dark_green_examples.png)

## Recipe Suggestions
The user can ask for recipes based on ingredients or the dish type.

A preview of asking for breakfast taco recipe:<br>
![Image of breakfast taco recipe](screenshots\recipe_preview.png)

Cancelling the recipe:<br>
![Image of cancelling recipe](screenshots\recipe_cancel.png)

## Chitchat
CoCo is able to handle chitchat, albeit very minimally.

CoCo can tell a few jokes, respond to thanks and goodbye.<br>
![Image of chitchat](screenshots\chitchat.png)
