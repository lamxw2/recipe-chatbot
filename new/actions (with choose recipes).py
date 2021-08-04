# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from mmap import ACCESS_DEFAULT
import pandas as pd
import numpy as np
import logging

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ValidateChooseRecipeForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_choose_recipe_form"

    def validate_cuisine(self, slot_value: Any, dispatcher, tracker, domain):
        
        recipe_id_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        if type(slot_value) is not int:
            slot_value = int(slot_value)

        if slot_value in recipe_id_values:
            return {"recipe_choice": slot_value}
        
        else:
            return {"recipe_choice": None}

class ActionChooseRecipe(Action):

    def name(self) -> Text:
        return "action_choose_recipe"
    
    def run(self, dispatcher, tracker, domain):
        
        # Get slots for recipe (list of dicts), button choices and recipe choices
        recipes = tracker.get_slot("recipe_results")
        recipe_choice = tracker.get_slot("recipe_choice")
        button_choice =  tracker.get_slot("button_choice")

        if type(recipe_choice) is not int:
            recipe_choice = int(recipe_choice)

        if button_choice == "yes":

            retrieve_recipes = ActionRetrieveRecipes()

            chosen_recipe = retrieve_recipes.format_chosen_recipe(recipes[recipe_choice])
            
            dispatcher.utter_message(chosen_recipe)
            dispatcher.utter_message("I hope you enjoy your choice! :)")
        
        return []

# Show Next 5 recipes
class ActionShowNextRecipes(Action):

    def name(self) -> Text:
        return "action_show_next_recipes"
    
    def run(self, dispatcher, tracker, domain):
        
        # Get slots for button choices
        recipes = tracker.get_slot("recipe_results")
        button_choice =  tracker.get_slot("button_choice")

        if button_choice == "yes":

            dispatcher.utter_message("Which recipe did you like? Please enter the recipe number below.")

        elif button_choice == "next":

            dispatcher.utter_message("I'm sorry that you didn't like any of my suggestions! :(")

        elif button_choice == "previous":

            retrieve_recipes = ActionRetrieveRecipes()
            # prev 5 recipes
            format_recipes = retrieve_recipes.format_recipe_previews(recipes, 0, 5)

            dispatcher.utter_message("Here are the recipes!")

            for recipe in format_recipes:
                dispatcher.utter_message(recipe)
            
            buttons = []

            buttons.append({"title": "Yes" , "payload": "/button_intent{\"button_choice\": \"yes\"}"})
            buttons.append({"title": "No" , "payload": "/button_intent{\"button_choice\": \"next\"}"})
            buttons.append({"title": "Previous" , "payload": "/button_intent{\"button_choice\": \"previous\"}"})
            buttons.append({"title": "Cancel" , "payload": "/button_intent{\"button_choice\": \"cancel\"}"})

            dispatcher.utter_message(text = "How about these?" , buttons=buttons)

        
        elif button_choice == "cancel":

            dispatcher.utter_message("Okay! What else would you like?")
        
        else:
            dispatcher.utter_message("ShowNextRecipes: Oops, my creator screwed up and something that shouldn't have gone wrong did go wrong.")

        return []

class ActionButtonChoice(Action):

    def name(self) -> Text:
        return "action_button_choice"
    
    def run(self, dispatcher, tracker, domain):
        
        # Get slots for recipe (list of dicts), button choices and recipe choices
        recipes = tracker.get_slot("recipe_results")
        logging.info(f"Get slot {recipes}")
        button_choice =  tracker.get_slot("button_choice")

        if button_choice == "yes":

            dispatcher.utter_message("Which recipe did you like? Please enter the recipe number below.")

        elif button_choice == "next":

            retrieve_recipes = ActionRetrieveRecipes()
            # next 5 recipes
            format_recipes = retrieve_recipes.format_recipe_previews(recipes, 5, len(retrieve_recipes)-1)

            dispatcher.utter_message("Here are the next few recipes!")

            for recipe in format_recipes:
                dispatcher.utter_message(recipe)
            
            buttons = []

            buttons.append({"title": "Yes" , "payload": "/button_intent{\"button_choice\": \"yes\"}"})
            buttons.append({"title": "No" , "payload": "/button_intent{\"button_choice\": \"next\"}"})
            buttons.append({"title": "Previous" , "payload": "/button_intent{\"button_choice\": \"previous\"}"})
            buttons.append({"title": "Cancel" , "payload": "/button_intent{\"button_choice\": \"cancel\"}"})

            dispatcher.utter_message(text = "How about these?" , buttons=buttons)
        
        elif button_choice == "cancel":

            dispatcher.utter_message("Okay! What else would you like?")
        
        else:
            dispatcher.utter_message("ButtonChoice: Oops, my creator screwed up and something that shouldn't have gone wrong did go wrong.")

        return []

class ActionRetrieveRecipes(Action):

    logging.basicConfig(level=logging.DEBUG)

    global df
    df = pd.read_pickle('data/datasets/recipes_dataset.pkl')
    
    def create_recipe_choices(self, df):

        recipes = []
        id = 1

        for index, row in df.iterrows():
            recipe = {}

            recipe['id'] = id

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

            id += 1
        
        return recipes

    def search_recipes(self, cuisine_list, ingredient_list, category_list):

        if not cuisine_list:
            cuisine_category_list = category_list
        else:
            cuisine_category_list = cuisine_list + category_list

        base = r'^{}'
        expr = '(?=.*{})'
        category_query_string = base.format(''.join(expr.format(w) for w in cuisine_category_list))
        ingredient_query_string = base.format(''.join(expr.format(w) for w in ingredient_list))

        recipes_df = df[df['ingredients'].str.contains(ingredient_query_string, case=False)
        & df['categories'].str.contains(category_query_string, case=False)].sort_values(by=['calories', 'rating'], ascending=[True, False])

        recipes_df = recipes_df.head()

        return recipes_df

    # List of recipes to choose from
    def format_recipe_previews(self, recipes, start_index, end_index):
    
        if (end_index > len(recipes)-1) or end_index is None:
            end_index = len(recipes) -1

        if start_index is None:
            start_index = 0

        recipes_format = []
        for recipe in recipes[start_index:end_index]:
            recipe_str = f"ID: {recipe['id']}\n"
            recipe_str += "Title: " + recipe['title'] + "\n" 
            recipe_str += "Description: " + recipe['desc'] + "\n"
            recipe_str += f"Calories: {recipe['calories']}\n"
            recipe_str += f"Protein: {recipe['protein']} \n"
            recipe_str += "Ingredients: \n" + recipe['ingredients'] + "\n"
            # recipe_str += "Directions: \n" + recipe['directions']
            recipes_format.append(recipe_str)
    
        return recipes_format

    def format_chosen_recipe(self, recipe):

        recipe_str = "Title: " + recipe['title'] + "\n" 
        recipe_str += "Description: " + recipe['desc'] + "\n"
        recipe_str += f"Calories: {recipe['calories']}\n"
        recipe_str += f"Protein: {recipe['protein']} \n"
        recipe_str += "Ingredients: \n" + recipe['ingredients'] + "\n"
        recipe_str += "Directions: \n" + recipe['directions']

        return recipe_str

    def name(self) -> Text:
        return "action_retrieve_recipes"
    
    def run(self, dispatcher, tracker, domain):
        
        # modify this for multiple entities tmr
        recipes = []
        ingredients = ['dairy', 'fruits', 'grains', 'proteins', 'vegetables']

        entity_cuisine = list(tracker.get_latest_entity_values("cuisine"))

        entity_ingredient = None
        for ingredient in ingredients:

            entity_ingredient = list(tracker.get_latest_entity_values(ingredient))
            logging.info(f"ingredient type: {ingredient}")

            if entity_ingredient:

                logging.info(f"ingredient: {entity_ingredient}")
                break
            else:
                logging.info(f"else: {entity_ingredient}")
        
        entity_category = list(tracker.get_latest_entity_values("dish_categories"))
        
        logging.info(entity_cuisine)
        logging.info(entity_ingredient)
        logging.info(entity_category)

        recipes_df = self.search_recipes(entity_cuisine, entity_ingredient, entity_category)

        if ~recipes_df.empty:

            recipes = self.create_recipe_choices(recipes_df)
            recommended_recipes = self.format_recipe_previews(recipes, 0, 5)

            logging.info(f"Slot was set: {type(recipes)}")

            dispatcher.utter_message("Here are the recipes!")

            for recipe in recommended_recipes:
                dispatcher.utter_message(recipe)
            
            buttons = []

            buttons.append({"title": "Yes" , "payload": "/button_intent{\"button_choice\": \"yes\"}"})

            if len(recommended_recipes) > 5:
                buttons.append({"title": "Next" , "payload": "/button_intent{\"button_choice\": \"next\"}"})

            buttons.append({"title": "Cancel" , "payload": "/button_intent{\"button_choice\": \"cancel\"}"})
            
            dispatcher.utter_message(text = "Do you like any of the recipes?" , buttons=buttons)
            
        else:

            error_message = "Sorry, I am unable to find recipes with what you've asked for. "
            error_message += "Trying a different phrasing (e.g. switching from plural to singular, or vice versa) would help!"
            dispatcher.utter_message(error_message)

        return [SlotSet("recipe_results", recipes)]

class ActionInformHealthyEatingBasic(Action):

    logging.basicConfig(level=logging.DEBUG)
    
    global dairy_df, fruit_df, grains_df, proteins_df, veg_df
    dairy_df = pd.read_pickle('data/datasets/dairy_dataset.pkl')
    fruit_df = pd.read_pickle('data/datasets/fruit_dataset.pkl')
    grains_df = pd.read_pickle('data/datasets/grains_dataset.pkl')
    proteins_df = pd.read_pickle('data/datasets/proteins_dataset.pkl')
    veg_df = pd.read_pickle('data/datasets/veg_dataset.pkl')

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
    
    def name(self) -> Text:
        return "action_inform_healthy_eating_basic"
    
    def run(self, dispatcher, tracker, domain):
        
        intent = tracker.get_intent_of_latest_message()
        logging.info(intent)

        entity_foodgroup = None
        foodgroup = ['dairy', 'fruits', 'grains', 'proteins', 'vegetables']
        entity_fooditem = None

        # Get the food group (entity name)
        for group in foodgroup:

            # Go through each food group
            entity_fooditem = next(tracker.get_latest_entity_values(group), None)
            logging.info(f"Food: {entity_fooditem}")

            # When food group is identified
            if entity_fooditem is not None:
                entity_foodgroup = group
                break
        
        # If user asks about basic healthy eating
        #if "ask_healthy_eating_basic" in intent and entity_foodgroup is not None:
        if entity_foodgroup is not None:

            basic_info_messages = self.basic_inform_by_foodgroup(entity_foodgroup)

            for message in basic_info_messages:
                dispatcher.utter_message(message)
        
        elif entity_foodgroup is None:

            example_info_messages = []

            basic_message_1st = "A balanced diet consists of: \n"
            basic_message_1st += " - at least 5 portions of fruit and vegetables a day\n"
            basic_message_1st += " - a source of protein, such as meat, eggs or pulses\n"
            basic_message_1st += " - high-fibre carbohydrates, including whole-grain bread\n"
            basic_message_1st += " - some dairy, including plant milk fortified with calcium"

            example_info_messages.append(basic_message_1st)

            basic_message_2nd = "Having a balanced diet daily keeps you healthy!"
            example_info_messages.append(basic_message_2nd)

            for message in example_info_messages:
                dispatcher.utter_message(message)
            
        else:
            # do something
            dispatcher.utter_message("Oops! Something went wrong in retrieving basic information.")

        return []

# Inform about healthy eating
class ActionInformHealthyEatingExamples(Action):

    logging.basicConfig(level=logging.DEBUG)
    
    global dairy_df, fruit_df, grains_df, proteins_df, veg_df
    dairy_df = pd.read_pickle('data/datasets/dairy_dataset.pkl')
    fruit_df = pd.read_pickle('data/datasets/fruit_dataset.pkl')
    grains_df = pd.read_pickle('data/datasets/grains_dataset.pkl')
    proteins_df = pd.read_pickle('data/datasets/proteins_dataset.pkl')
    veg_df = pd.read_pickle('data/datasets/veg_dataset.pkl')

    # Format list of food examples in a string
    def format_food_list(self, df):

        # Get names of food items
        food_list = list(df['name'])
        # Get plural form of food if applicable
        food_list = [x.split('/')[0] for x in food_list]
        # Join list as string and add 'and' right before last food item
        format_food_list = [str(x) for x in food_list[:-1]]
        food_examples = ", ".join(format_food_list) + ' and ' + str(food_list[-1] + '.')

        return food_examples

    # Informative messages of examples of each food group
    # @entity_foodgroup - food group
    # @entity_fooditem - specific food item, aka entity value
    def format_examples_by_foodgroup(self, entity_foodgroup, entity_fooditem):
        
        example_messages = []
        df, unhealthy_message, error_message = self.get_result(entity_foodgroup, entity_fooditem)

        # Make sure dataframe isnt empty
        if ~df.empty:

            # Dairy food group
            if entity_foodgroup == "dairy":
                
                # If user asks about other types of dairy food
                if entity_fooditem == "dairy":

                    food_list = list(df['name'])
                    format_food_list = [str(n) for n in food_list[:-1]]

                    dairy_1st = "Examples of healthy dairy food include: "
                    dairy_1st += ", ".join(format_food_list) + ' and ' + str(food_list[-1] + '.')
                    example_messages.append(dairy_1st)
                
                # If user asks about an unhealthy type of dairy food
                elif unhealthy_message is not None:

                    dairy_1st = unhealthy_message
                    dairy_1st += " Why not try a low-fat version or a healthier substitute? "
                    dairy_1st += "Yogurt is a common, tasty substitute for ice-cream and cream cheese!"

                    example_messages.append(dairy_1st)
                
                # If user asks about specific dairy food
                elif (unhealthy_message is None) & (entity_fooditem != "dairy"):

                    sub_group = list(df['sub_group'].unique())[0].lower()

                    food_examples = self.format_food_list(df)

                    dairy_1st = f"{entity_fooditem.capitalize()} is a type of {sub_group}.\n"
                    dairy_1st += f"Other types of {sub_group}s include: "
                    dairy_1st += food_examples

                    example_messages.append(dairy_1st)

            # Fruit food group
            elif entity_foodgroup == "fruits":

                sub_groups = ['berries', 'berry', 'citrus', 'melons']

                if "fruit" in entity_fooditem.lower():

                    food_examples = self.format_food_list(df)

                    fruit_1st = f"Examples of {entity_fooditem} include: "
                    fruit_1st += food_examples

                    example_messages.append(fruit_1st)

                # If asking for sub-group only
                elif entity_fooditem.lower() in sub_groups:

                    food_examples = self.format_food_list(df)

                    fruit_1st = "You can have fruit in fresh, frozen or canned (in 100% juice)!\n"

                    if entity_fooditem.lower() == "citrus":
                        fruit_1st += f"Examples of {entity_fooditem} fruit include: "
                    elif entity_fooditem.lower() == "berry":
                        fruit_1st += f"Examples of berries include: "
                    
                    fruit_1st += food_examples

                    example_messages.append(fruit_1st)

                # If asking if specific fruit is part of a subgroup
                else:

                    # Get sub-group name
                    sub_group = list(df['sub_group'].unique())[0].lower() 
                    # Get food item names under the same sub-group
                    food_examples = self.format_food_list(df)

                    fruit_1st = f"{entity_fooditem.capitalize()} is a type of {sub_group}.\n"

                    if entity_fooditem.lower() == "citrus":
                        fruit_1st += f"Other types of {entity_fooditem} fruit include: "
                    elif entity_fooditem.lower() == "berry":
                        fruit_1st += f"Other types of berries include: "

                    fruit_1st += food_examples
                    fruit_1st += "\nYou can have fruit in fresh, frozen or canned (in 100% juice)!"

                    example_messages.append(fruit_1st)
                
            elif entity_foodgroup == "grains":
                
                sub_groups_whole = ['whole-grains', 'whole grains', 'whole-grain', 'whole grain']
                sub_groups_refined = ['refined-grains', 'refined grains', 'refined-grain', 'refined grain']
                sub_groups_processed = ['processed-grains', 'processed grains', 'processed grain', 'processed-grain']

                if (("carbohydrate" in entity_fooditem)
                    or (entity_fooditem in sub_groups_whole) 
                    or (entity_fooditem in sub_groups_refined) 
                    or (entity_fooditem in sub_groups_processed)):

                    food_examples = self.format_food_list(df)

                    grains_1st = f"Examples of {entity_fooditem} include: "
                    grains_1st += food_examples

                    example_messages.append(grains_1st)
                
                else:

                    # Get sub-group name
                    sub_group = list(df['sub_group'].unique())[0].lower()
                    food_examples = self.format_food_list(df)

                    grains_1st = f"{entity_fooditem.capitalize()} is a type of {sub_group}.\n"
                    grains_1st += f"Other types of {sub_group} include: "
                    grains_1st += food_examples

                    example_messages.append(grains_1st)
                
            elif entity_foodgroup == "proteins":

                sub_groups = ['red meat', 'poultry', 'seafood', 'white fish', 'oily fish',
                        'shellfish', 'nuts', 'seeds', 'soy', 'vegetarian', 'seafood'] 
                        
                # Listing examples in each subgroup
                if "protein" in entity_fooditem.lower() or entity_fooditem.lower() in sub_groups:

                    food_examples = self.format_food_list(df)

                    proteins_1st = f"Examples of {entity_fooditem} include: "
                    proteins_1st += food_examples

                    example_messages.append(proteins_1st)
            
                # Type of sub-group food item is in
                else:

                    # Get sub-group name
                    sub_group = list(df['sub_group'].unique())[0].lower()
                    food_examples = self.format_food_list(df)

                    proteins_1st = f"{entity_fooditem.capitalize()} is a type of {sub_group}.\n"
                    proteins_1st += f"Other types of {sub_group} include: "
                    proteins_1st += food_examples

                    example_messages.append(proteins_1st)
                
            elif entity_foodgroup == "vegetables":

                sub_groups = ['dark-green', 'dark green', 'red and orange', 'pulses', 'beans', 'lentils', 'starchy', 'others']

                # If asking for sub-group only
                if "vegetable" in entity_fooditem.lower() or entity_fooditem.lower() in sub_groups:

                    food_examples = self.format_food_list(df)

                    veg_1st = "Vegetables can be eaten fresh, frozen or canned!\n"
                    veg_1st += f"Examples of {entity_fooditem} include: "
                    veg_1st += food_examples

                    example_messages.append(veg_1st)

                # If asking if specific vegetable is part of a subgroup
                else:

                    # Get sub-group name
                    sub_group = list(df['sub_group'].unique())[0].lower()
                    food_examples = self.format_food_list(df)

                    if ((entity_fooditem == "pulses") or (entity_fooditem == "beans")
                        or (entity_fooditem == "lentils")):
                        veg_1st = f"{entity_fooditem.capitalize()} is a type of {sub_group}.\n"
                    else:
                        veg_1st = f"{entity_fooditem.capitalize()} is a type of {sub_group} vegetable.\n"

                    veg_1st += f"Other types of {sub_group} include: "
                    veg_1st += food_examples
                    veg_1st += "\nVegetables can be eaten fresh, frozen or canned!"

                    example_messages.append(veg_1st)

        else:
        
            example_messages.append(error_message)
        
        return example_messages

    def get_result(self, entity_foodgroup, entity_fooditem):

        df = None
        unhealthy_message = None
        error_message = None

        if entity_foodgroup == "dairy":

            # If user asks for list of dairy food
            if entity_fooditem == "dairy":
                # Every food that is healthy
                df = dairy_df[~dairy_df['sub_group'].str.contains('unhealthy', case=False)]
            
            # If user asks about specific dairy food
            else:

                # If food item is unhealthy (subgroup == unhealthy)
                if list(dairy_df.loc[dairy_df['name'].str.contains(entity_fooditem), 'sub_group'].str.lower())[0] == 'unhealthy':
                    unhealthy_message = f"{entity_fooditem.capitalize()} is not a healthy source of dairy!"

                else:        
                    # Get sub-group
                    sub_group = list(dairy_df.loc[dairy_df['name'].str.contains(entity_fooditem, case=False), 'sub_group'])[0]
                    # Get all other food items under the same sub-group
                    df = dairy_df[(dairy_df['sub_group'].str.contains(sub_group, case=False) 
                    & ~dairy_df['sub_group'].str.contains('unhealthy', case=False))] # Excludes 'unhealthy'

        elif entity_foodgroup == "fruit":
            
            sub_groups = ['berries', 'citrus', 'melons']

            if "fruit" in entity_fooditem.lower():
                df = fruit_df

            # If asking for sub-group only
            elif entity_fooditem.lower() in sub_groups:
                df = fruit_df[fruit_df[('sub_group')].str.contains(entity_fooditem, case=False)]
            
            elif (entity_fooditem.lower() == "berries") or (entity_fooditem.lower() == "berry"):
                df = fruit_df[fruit_df[('sub_group')].str.contains('berries', case=False)]

            # If asking if specific fruit is part of a subgroup
            else:

                sub_group = list(fruit_df.loc[fruit_df['name'].str.contains(entity_fooditem, case=False), 'sub_group'])[0]
                df = fruit_df[fruit_df['sub_group'].str.contains(sub_group, case=False)]
        
        elif entity_foodgroup == "grains":
            
            sub_groups_whole = ['whole-grains', 'whole grains', 'whole-grain', 'whole grain']
            sub_groups_refined = ['refined-grains', 'refined grains', 'refined-grain', 'refined grain']
            sub_groups_processed = ['processed-grains', 'processed grains', 'processed grain', 'processed-grain']

            if "carbohydrate" in entity_fooditem.lower():
                df = grains_df

            # If asking for sub-group only
            elif entity_fooditem.lower() in sub_groups_whole:
                df = grains_df[grains_df[('sub_group')].str.contains('whole grains', case=False)]

            elif entity_fooditem.lower() in sub_groups_refined or entity_fooditem.lower() in sub_groups_processed:
                df = grains_df[grains_df[('sub_group')].str.contains('refined grains', case=False)]

            # If asking if specific grain food is part of a subgroup
            else:

                sub_group = list(grains_df.loc[grains_df['name'].str.contains(entity_fooditem, case=False), 'sub_group'])[0]
                df = grains_df[grains_df['sub_group'].str.contains(sub_group, case=False)]

        elif entity_foodgroup == "proteins":

            sub_groups = ['red meat', 'poultry', 'seafood', 'white fish', 'oily fish',
                        'shellfish', 'nuts', 'seeds', 'soy', 'vegetarian', 'seafood'] 

            if "protein" in entity_fooditem.lower():
                df = proteins_df

            # Listing examples in each subgroup
            elif entity_fooditem.lower() in sub_groups:
                df = proteins_df[proteins_df[('sub_group')].str.contains(entity_fooditem, case=False)]
        
            # Type of sub-group food item is in
            else:
                sub_group = list(proteins_df.loc[proteins_df['name'].str.contains(entity_fooditem, case=False), 'sub_group'])[0]
                df = proteins_df[proteins_df['sub_group'].str.contains(sub_group, case=False)]

        elif entity_foodgroup == "vegetables":
        
            sub_groups = ['dark-green', 'dark green', 'red and orange', 'pulses', 'beans', 'lentils', 'starchy', 'others']

            if "vegetable" in entity_fooditem.lower():
                df = veg_df

            # If asking for sub-group only
            elif entity_fooditem.lower() in sub_groups:

                if entity_fooditem.lower() == "dark-green" or entity_fooditem.lower() == 'dark green':
                    df = veg_df[veg_df[('sub_group')].str.contains('dark green', case=False)]
                else:
                    df = veg_df[veg_df[('sub_group')].str.contains(entity_fooditem, case=False)]

            # If asking if specific vegetable is part of a subgroup
            else:

                sub_group = list(veg_df.loc[veg_df['name'].str.contains(entity_fooditem, case=False), 'sub_group'])[0]
                df = veg_df[veg_df['sub_group'].str.contains(sub_group, case=False)]

        else:
            error_message = "Sorry, I didn't understand that. Try to reword your phrasing please!"
        
        return df, unhealthy_message, error_message


    def name(self) -> Text:
        return "action_inform_healthy_eating_examples"
    
    def run(self, dispatcher, tracker, domain):
        
        intent = tracker.get_intent_of_latest_message()
        logging.info(intent)

        entity_foodgroup = None
        foodgroup = ['dairy', 'fruits', 'grains', 'proteins', 'vegetables']
        entity_fooditem = None

        # Get the food group (entity name)
        for group in foodgroup:

            # Go through each food group
            entity_fooditem = next(tracker.get_latest_entity_values(group), None)
            logging.info(f"Food: {entity_fooditem}")

            # When food group is identified
            if entity_fooditem is not None:
                entity_foodgroup = group
                break
        
        logging.info(type(intent))

        # If user asks about examples of healthy food
        # if "ask_healthy_eating_examples" in intent and entity_foodgroup is not None:
        if entity_foodgroup is not None:
            example_info_messages = self.format_examples_by_foodgroup(entity_foodgroup, entity_fooditem)

            for message in example_info_messages:
                dispatcher.utter_message(message)

        else:
            # do something
            dispatcher.utter_message("Oops! Something went wrong.")

        return []
