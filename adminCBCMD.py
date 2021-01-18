# Administrator Chatbot Commands .py
# Import pretty colors for printing!
from bcolors import bcolors
# Import config data.
import config
import webhookHandler


# Every command must return a string or data that is convertable to string.

def cbBlacklist(data):
    args = data["event"]["content"].split(" ")
    config.invBlacklist(args[1::])
    return str("Okay! Inverted " + (' '.join([str(elem) for elem in args[1::]])) + " in the BL.")


def cbDisable(data):
    args = data["event"]["content"].split(" ")
    config.invDisable(args[1::])
    return str("Okay! Inverted " + (' '.join([str(elem) for elem in args[1::]])) + " in the Disabled list.")


def interpretCommand(data):
    ca = data["event"]
    # Remove case sensitivity, Purge prefix from message
    execute = (((ca["content"]).lower()).split(" "))[0][1::]
    switcher = {
        "blacklist": cbBlacklist,
        "disable": cbDisable
    }
    # Check if command exists
    try:
        # Get the function from switcher dictionary
        func = switcher.get(execute)
        # Execute the function
        response = [True, func(data)]
    except (KeyError, TypeError) as error:
        # If command does not exist, return false.
        response = [False, ""]
    webhookHandler.webhookhandler(config.wconfig["DCMDWebhook"], data, "cmd", response)
    return (response)


# Notify when file loaded.
print("Administrator chatbot commands loaded!")
