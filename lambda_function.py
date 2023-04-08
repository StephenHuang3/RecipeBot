"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""
import math
import dateutil.parser
import datetime
import time
import os
import logging
import json
import boto3
import uuid

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

def retrive_recipe(item, flavor, dietary_restrictions):
    
""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request["currentIntent"]["slots"]


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


def close(session_attributes, fulfillment_state, message):
    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
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


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def validate_order_flowers(item, flavor, dietary_restrictions):
    items = ["cake", "bread", "cup cakes"]
    if item is not None and item.lower() not in items:
        return build_validation_result(
            False,
            "Item",
            "We do not have {}, would you like a different type of flower?  "
            "Our most popular flowers are roses".format(item),
        )

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
    # if flavor is not None:
    #     if not isvalid_date(flavor):
    #         return build_validation_result(
    #             False,
    #             "PickupDate",
    #             "I did not understand that, what date would you like to pick the flowers up?",
    #         )
    #     elif (
    #         datetime.datetime.strptime(flavor, "%Y-%m-%d").date()
    #         <= datetime.date.today()
    #     ):
    #         return build_validation_result(
    #             False,
    #             "PickupDate",
    #             "You can pick up the flowers from tomorrow onwards.  What day would you like to pick them up?",
    #         )

    # if servings is not None:
    #     if len(servings) != 5:
    #         # Not a valid time; use a prompt defined on the build-time model.
    #         return build_validation_result(False, "PickupTime", None)

    #     hour, minute = servings.split(":")
    #     hour = parse_int(hour)
    #     minute = parse_int(minute)
    #     if math.isnan(hour) or math.isnan(minute):
    #         # Not a valid time; use a prompt defined on the build-time model.
    #         return build_validation_result(False, "PickupTime", None)

    #     if hour < 10 or hour > 16:
    #         # Outside of business hours
    #         return build_validation_result(
    #             False,
    #             "PickupTime",
    #             "Our business hours are from ten a m. to five p m. Can you specify a time during this range?",
    #         )

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


def order_flowers(intent_request):
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

        validation_result = validate_order_flowers(item, flavor, dietary_restrictions)
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
        if item is not None:
            output_session_attributes["Price"] = len(item) * 5  # Elegant pricing model

        return delegate(output_session_attributes, get_slots(intent_request))

    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": "Thanks, your order for {} has been placed and will be ready for pickup by {} on {}".format(
                item, dietary_restrictions, flavor
            ),
        },
    )


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug(
        "dispatch userId={}, intentName={}".format(
            intent_request["userId"], intent_request["currentIntent"]["name"]
        )
    )

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to your bot's intent handlers
    if intent_name == "OrderFlowers":
        return order_flowers(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ["TZ"] = "America/New_York"
    time.tzset()
    logger.debug("event.bot.name={}".format(event["bot"]["name"]))

    return dispatch(event)
