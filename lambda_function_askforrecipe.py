"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""
import random
import dateutil.parser
import logging
import boto3
from boto3.dynamodb.conditions import Attr

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dyn_client = boto3.client("dynamodb")
TABLE_NAME = "bakingrecipes"

""" --- Helper functions for dynamodb"""


def safe_int(n):
    """
    safely convert n value to int
    """

    if n is not None:
        return int(n)
    return n


def get_random_recipe_index(list_length):
    return random.randint(0, list_length - 1)


def try_ex(func):
    """
    call passed in function in try block .if keyerror is encountered return None.
    this function is intended to be used to safely access dicitonary.
    note that this functions would hae negative impact on performance
    """
    try:
        return func()
    except KeyError:
        return None


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ConfirmIntent",
            "intentName": intent_name,
            "slots": slots,
            "message": message,
        },
    }


""" --- Dynamodb query"""


def retrive_recipe(item, filter_strings=None):
    query_limit = 100
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("bakingrecipes4_keywordsv2")

    key_condition_expression = "keywords = :keyword"
    expression_attribute_values = {":keyword": str(item)}

    response = table.query(
        IndexName="keywords-index",
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_attribute_values,
        Limit=query_limit,
    )

    print("Query parameters: ")
    print("IndexName: ", "keywords-index")
    print("KeyConditionExpression: ", key_condition_expression)
    print("ExpressionAttributeValues: ", expression_attribute_values)

    print("this is response")
    print(response["Items"])

    if filter_strings:
        filter_strings = [s.lower() for s in filter_strings]
        print("this is filter_strings length: " + str(len(filter_strings)))
        print(filter_strings)

        filtered_items = []
        for item in response["Items"]:
            title = item["title"].lower()
            if all(string in title for string in filter_strings):
                filtered_items.append(item)

        print("Filtered results: ", filtered_items)
        return filtered_items

    return response["Items"]


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request["sessionState"]["intent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def close(session_attributes, intent_name, fulfillment_state, message):
    response = {
        "sessionState": {
            "sessionAttributes": session_attributes,
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": fulfillment_state,
            },
            "intent": {"name": intent_name, "state": fulfillment_state},
        },
        "messages": [message],
    }

    return response


def delegate(session_attributes, slots):
    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


def validate_ask_for_recipe(item, flavor, dietary_restrictions):
    allowed_dietary_restrictions = [
        "gluten free",
        "nuts free",
        "vegan",
        "vegetarian",
        "sugar free",
        "dairy free",
        "kosher",
        "halal",
        "none",
    ]
    if (
        dietary_restrictions is not None
        and dietary_restrictions not in allowed_dietary_restrictions
    ):
        return build_validation_result(
            False,
            "dietary_restrictions",
            "I did not understand that, your dietary restriction is not in our list. Please try again",
        )

    return build_validation_result(True, None, None)


def valid_item(dietaryRestriction, NER):
    if dietaryRestriction == "none":
        return True
    glutenfree = [
        "bread",
        "pasta",
        "cereal",
        "crackers",
        "beer",
        "gravy",
        "ale",
        "wheat",
        "cookies",
    ]
    nutsfree = [
        "almonds",
        "walnuts",
        "pecans",
        "cashews",
        "hazelnuts",
        "peanuts",
        "macadamia nuts",
        "pine nuts",
        "Brazil nuts",
        "pistachios",
        "butternuts",
    ]
    vegan = [
        "eggs",
        "egg",
        "cheese",
        "milk",
        "ice cream",
        "honey",
        "meat",
        "mayonnaise",
        "fish",
        "tuna",
        "salmon",
        "beef",
        "lamb",
        "veal",
        "pork",
        "kangaroo",
        "chicken",
        "turkey",
        "duck",
        "emu",
        "goose",
        "fish",
        "tuna",
        "crab",
        "lobster",
        "mussel",
        "oyster",
        "clam",
        "scallop",
    ]
    vegetarian = [
        "beef",
        "lamb",
        "veal",
        "pork",
        "kangaroo",
        "chicken",
        "turkey",
        "duck",
        "emu",
        "goose",
        "fish",
        "tuna",
        "crab",
        "lobster",
        "mussel",
        "oyster",
        "clam",
        "scallop",
    ]
    sugarfree = [
        "sugar",
        "brown sugar" "honey",
        "maple syurp",
        "syrup",
        "ice cream",
        "icing",
        "candy",
    ]
    dairyfree = [
        "milk",
        "cheese",
        "yogurt",
        "butter",
        "milkshake",
        "cream",
        "ice cream",
        "custard",
        "Casein",
        "lactose",
        "frozen",
    ]
    kosher = [
        "pork",
        "rabbit",
        "squirrel",
        "camel",
        "kangaroo",
        "horse",
        "pork loin",
        "bacon",
        "pork chop",
        "pork chops",
        "pork belly",
        "sausage",
        "gelatin",
        "eagle",
        "owl",
        "gull",
        "hawk",
        "flank",
        "beef flank",
        "short loin",
        "sirloin",
        "round",
        "shank",
    ]
    halal = [
        "pork",
        "bird",
        "pork loin",
        "bacon",
        "pork chop",
        "pork chops",
        "pork belly",
        "sausage",
        "gelatin",
    ]

    if dietaryRestriction == "gluten free":
        for item in glutenfree:
            if item in NER:
                return False
    elif dietaryRestriction == "nuts free":
        for item in nutsfree:
            if item in NER:
                return False
    elif dietaryRestriction == "vegan":
        for item in vegan:
            if item in NER:
                return False
    elif dietaryRestriction == "vegetarian":
        for item in vegetarian:
            if item in NER:
                return False
    elif dietaryRestriction == "sugar free":
        for item in sugarfree:
            if item in NER:
                return False
    elif dietaryRestriction == "dairy free":
        for item in dairyfree:
            if item in NER:
                return False
    elif dietaryRestriction == "kosher":
        for item in kosher:
            if item in NER:
                return False
    elif dietaryRestriction == "halal":
        for item in halal:
            if item in NER:
                return False
    return True


""" --- Functions that control the bot's behavior --- """


def ask_for_recipe(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    item = get_slots(intent_request)["Item"]
    flavor = get_slots(intent_request)["Flavor"]
    dietary_restrictions = get_slots(intent_request)["DietaryRestrictions"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_ask_for_recipe(item, flavor, dietary_restrictions)
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )

        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        output_session_attributes = (
            intent_request["sessionAttributes"]
            if intent_request["sessionAttributes"] is not None
            else {}
        )

        return {
            "sessionState": {
                "sessionAttributes": output_session_attributes,
                "dialogAction": {
                    "type": "Delegate",
                    "slots": get_slots(intent_request),
                },
            },
            "requestAttributes": intent_request.get("requestAttributes"),
        }

    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    print("Item: ", item["value"]["interpretedValue"])
    print("Flavor: ", flavor["value"]["interpretedValue"])

    item_last = item["value"]["interpretedValue"].split(" ")[-1]
    flavor_plus_descriptors = item["value"]["interpretedValue"].split(" ")
    flavor_plus_descriptors.pop()

    print("flavor_plus_descriptors after splitting item:", flavor_plus_descriptors)

    if (
        flavor["value"]["interpretedValue"] != "any"
        and flavor["value"]["interpretedValue"] != "none"
        and flavor["value"]["interpretedValue"] != "no"
    ):
        flavor_plus_descriptors.extend(flavor["value"]["interpretedValue"].split(" "))

    print("Item last: ", item_last)
    print("flavor_plus_descriptors after adding flavor:", flavor_plus_descriptors)

    results = retrive_recipe(item_last, flavor_plus_descriptors)

    filtered_dietary_results = [
        result
        for result in results
        if valid_item(dietary_restrictions["value"]["interpretedValue"], result["NER"])
    ]

    print("Filtered results: ", filtered_dietary_results)
    print("intent_request: ", intent_request)
    if len(filtered_dietary_results) == 0:
        return close(
            intent_request["sessionState"]["sessionAttributes"],
            intent_request["sessionState"]["intent"]["name"],
            "Fulfilled",
            {
                "contentType": "PlainText",
                "content": "Sorry, we don't have any recipes for {} with a flavor of {}.".format(
                    item["value"]["interpretedValue"],
                    flavor["value"]["interpretedValue"],
                ),
            },
        )
    else:
        random_index = get_random_recipe_index(len(filtered_dietary_results))
        recipe = filtered_dietary_results[random_index]
        title = recipe["title"]
        ingredients = "\n".join(recipe["ingredients"])
        directions = "\n".join(recipe["directions"])
        source = recipe["link"]

        message_content = f"Here's the recipe for {title}:\n\nIngredients:\n{ingredients}\n\nDirections:\n{directions}\n\nSource: {source}\n\n"

        return close(
            intent_request["sessionState"]["sessionAttributes"],
            intent_request["sessionState"]["intent"]["name"],
            "Fulfilled",
            {
                "contentType": "PlainText",
                "content": message_content,
            },
        )


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["sessionState"]["intent"]["name"]

    logger.debug(
        "dispatch sessionId={}, intentName={}".format(
            intent_request["sessionId"], intent_name
        )
    )

    # Dispatch to your bot's intent handlers
    if intent_name == "AskforRecipe":
        return ask_for_recipe(intent_request)

    raise Exception(
        "Intent with name "
        + (intent_name if intent_name else "None")
        + " not supported"
    )


""" --- Main handler --- """


def lambda_handler(event, context):
    logger.debug(f"Received event: {event}")

    intent_request = event
    return dispatch(intent_request)
