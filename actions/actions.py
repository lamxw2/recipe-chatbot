# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import pandas as pd
import numpy as np
import logging

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionRetrieveRecipes(Action):

    logging.basicConfig(level=logging.DEBUG)

    global df
    df = pd.read_pickle('data/datasets/recipes_dataset.pkl')
    
    def search_recipe(self, cuisine, ingredient, category):
        recipes_df = df[df['ingredients'].str.contains(ingredient, case=False) & df['categories'].str.contains(category, case=False) & df['categories'].str.contains(cuisine, case=False)].sort_values(by=['calories', 'rating'], ascending=[True, False])
        recipes_df = recipes_df.head(5)
        
        recipes = []

        for index, row in recipes_df.iterrows():
            recipe = {}

            recipe['title'] = row['title']

            if row['desc'] is None:
                row['desc'] = ''
            recipe['desc'] = row['desc']

            if row['calories'] is None:
                row['calories'] = 'N.A'
            recipe['calories'] = row['calories']

            if row['protein'] is None:
                row['protein'] = 'N.A'
            recipe['protein'] = row['protein']
            
            recipe['ingredients'] = row['ingredients'].replace(', ', '\n')
            recipe['directions'] = row['directions'].replace('; ', '\n')

            recipes.append(recipe)

        # List of dicts
        return recipes

    def format_recipe(self, recipes):
        
        recipes_format = []
        for recipe in recipes:
            recipe_str = "Title: " + recipe['title'] + "\n" 
            recipe_str += "Description: " + recipe['desc'] + "\n"
            recipe_str += f"Calories: {recipe['calories']}\n"
            recipe_str += f"Protein: {recipe['protein']} \n"
            recipe_str += "Ingredients: \n" + recipe['ingredients'] + "\n"
            recipe_str += "Directions: \n" + recipe['directions']
            recipes_format.append(recipe_str)
        
        return recipes_format


    def name(self) -> Text:
        return "action_retrieve_recipes"
    
    def run(self, dispatcher, tracker, domain):
        
        recipes = []
        ingredients = ['dairy', 'fruits', 'grains', 'proteins', 'vegetables']

        entity_cuisine = next(tracker.get_latest_entity_values("cuisine"), None)

        entity_ingredient = None
        for ingredient in ingredients:
            entity_ingredient = next(tracker.get_latest_entity_values(ingredient), None)
            logging.info(f"ingredient: {entity_ingredient}")
            if entity_ingredient is not None:
                break
        
        entity_category = next(tracker.get_latest_entity_values("dish_categories"), None)
        
        logging.info(entity_cuisine)
        logging.info(entity_ingredient)
        logging.info(entity_category)

        if entity_cuisine is not None:
            recipes = self.search_recipe(cuisine=entity_cuisine, ingredient='', category='')

        elif entity_ingredient is not None:
            recipes = self.search_recipe(cuisine='', ingredient=entity_ingredient, category='')

        if entity_category is not None:
            recipes = self.search_recipe(cuisine='', ingredient='', category='entity_category')
        
        recommended_recipes = self.format_recipe(recipes)

        for recipe in recommended_recipes:
            dispatcher.utter_message(recipe)

        return []

# Inform about healthy eating
class ActionInformHealthyEating(Action):

    logging.basicConfig(level=logging.DEBUG)
    
    # Informative messages for basic healthy eating knowledge
    def basic_inform_by_foodgroup(self, entity_foodgroup):

        basic_info_messages = []

        if entity_foodgroup is not None:

            if entity_foodgroup == "dairy":

                dairy_1st = "You should have 3 cups of dairy a day!"
                
                basic_info_messages.append(dairy_1st)

                dairy_2nd = "1 cup is equivalent to: \n"
                dairy_2nd += "- 1 cup of milk, yogurt, or fortified soymilk\n"
                dairy_2nd += "- 1.5 oz of natural cheese (e.g. cheddar cheese)"
                dairy_2nd += "- 2 oz of processed cheese (such as processed cheese slices)"
                
                basic_info_messages.append(dairy_2nd) 

            elif entity_foodgroup == "fruits":

                fruits_1st = "You should eat between 1.5-2.5 cups equivalent, or as part of your 5 a day! " 
                fruits_1st += "Each portion of fruit is 80g." 
                fruits_1st += "\nYou may have 100% fruit juice as part of your 5 a day, but not more than 150ml!"
                
                basic_info_messages.append(fruits_1st)

            elif entity_foodgroup == "grains":
                
                grains_1st = "At least half of your daily grain intake should be whole grain. " 
                grains_1st += "Aim to have 5-10 ounces, or 142-283g of grains a day!"
                
                basic_info_messages.append(grains_1st)

                grains_2nd = "1 oz (approximately 28g) is equivalent to: \n"
                grains_2nd += "- 1.5 cups (150g) of cooked rice, pasta, or cereal\n" 
                grains_2nd += "- 1 oz dry pasta or rice\n"
                grains_2nd += "- 1 medium slice of bread, tortilla or flatbread\n"
                grains_2nd += "- 1 oz of ready-to-eat cereal\n"
                grains_2nd += "\n"
                grains_2nd += "A typical day would include 1 breakfast food (bread or cereal) and 2 servings of rice or pasta!"
                
                basic_info_messages.append(grains_2nd)

            elif entity_foodgroup == "proteins":
                
                proteins_1st = "Proteins can be further categorized into 4 subgroups: \n "
                proteins_1st += "- lean meat, poultry, eggs\n "
                proteins_1st += "- seafood\n"
                proteins_1st += "- beans, peas and lentils (pulses)\n"
                proteins_1st += "- nuts, seeds and soy products"
                
                basic_info_messages.append(proteins_1st)

                proteins_2nd = "You should eat 5-7 ounces (142-198g) of proteins a day!\n"
                proteins_2nd += "Aim to have at least 2 portions of fish (with 1 portion being oily fish) weekly.\n"
                proteins_2nd += "A portion is 140g (4.9oz)."
        
                basic_info_messages.append(proteins_2nd)

                proteins_3rd = "However, don't exceed 90g (3.2 oz) of red meat in a day!\n"
                proteins_3rd += "The recommended NHS guideline is 70g (2.5 oz) a day.\n"
                proteins_3rd += "The equivalent of 90g is:\n"
                proteins_3rd += "- 3 thinly cut slices of beef, lamb or pork\n"
                proteins_3rd += "  where each slice is about the size of half a slice of bread\n"
                proteins_3rd += "A typical English breakfast, containing 2 British sausages and 2 rashes of bacon is equivalent to 130g!"

                basic_info_messages.append(proteins_3rd)

            elif entity_foodgroup == "vegetables":

                veg_1st = "Vegetables can be categorized into 5 subgroups - \n"
                veg_1st += " - dark-green\n"
                veg_1st += " - red and orange\n"
                veg_1st += " - beans, peas and lentils (pulses)\n"
                veg_1st += " - starchy\n"
                veg_1st += " - and others\n"

                basic_info_messages.append(veg_1st)

                veg_2nd = "Aim to eat a variety of colours!\n"
                veg_2nd += "Most adults should eat 2-4 cups equivalent, or as part of their 5 a day.\n"
                veg_2nd += "Each portion in 5 a day is 80g!"

                basic_info_messages.append(veg_2nd)

        # else return empty list, aka
        # basic_info_messages = []
        
        return basic_info_messages

    # Informative messages of examples of each food group
    def examples_by_foodgroup(self, entity_foodgroup):
        
        example_messages = []

        if entity_foodgroup is not None:

            if entity_foodgroup == "dairy":
                
                basic_info_messages.append(dairy_2nd) 

            elif entity_foodgroup == "fruits":

                fruits_1st = "You should eat between 1.5-2.5 cups equivalent, or as part of your 5 a day! " 
                

            elif entity_foodgroup == "grains":
                
                grains_1st = "At least half of your daily grain intake should be whole grain. " 
                

            elif entity_foodgroup == "proteins":
                
                

            elif entity_foodgroup == "vegetables":

                

        # else return empty list, aka
        # example_messages = []
        
        return example_messages


    def name(self) -> Text:
        return "action_retrieve_recipes"
    
    def run(self, dispatcher, tracker, domain):
        
        intent = tracker.get_intent_of_latest_message

        entity_foodgroup = ""
        foodgroup = ['dairy', 'fruits', 'grains', 'proteins', 'vegetables']

        # Get the food group (entity name)
        for group in foodgroup:

            # Go through each food group
            entity_value = next(tracker.get_latest_entity_values(group), None)
            logging.info(f"Food: {entity_value}")

            # When food group is identified
            if entity_value is not None:
                entity_foodgroup = group
                break
        
        # If user asks about basic healthy eating
        if intent.contains("ask_healthy_eating_basic") and entity_foodgroup != "":
            
            basic_info_messages = self.basic_inform_by_foodgroup(entity_foodgroup)

            for message in basic_info_messages:
                dispatcher.utter_message(message)

        # If user asks about examples of healthy food
        elif intent.contains("ask_healthy_eating_examples") and entity_foodgroup != "":
            
            example_info_messages = self.examples_by_foodgroup(entity_foodgroup)

            for message in example_info_messages:
                dispatcher.utter_message(message)
            
        else:
            # do something
            dispatcher.utter_message("Oops! Something went wrong.")

        return []
