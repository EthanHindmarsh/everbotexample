# Everskies Work-In-Progress .py
import json
import time
import requests
import sys
import adminCBCMD
import chatbotcommands
import config
import webhookHandler
from bcolors import bcolors
from config import bconfig
from wc import sendData


def messageuser(message, convid, rs, mode=None):
    pass
    return [True, '']
    data = {
        "content": message,
        "attachments": [],
    }
    # Send message to user by conv id
    r = rs.post('https://api-test.everskies.com/user/message/' + str(convid) + '/reply', data=json.dumps(data))

    if mode == "retry":
        # rs arg will now represent a token
        print("Retrying message!")
        if r.ok:
            print("Message sent successfully! Quitting thread")
            sys.exit()
        else:
            print("Message failed to send. Quitting thread")
            sys.exit()
    else:
        # check if message sent correctly
        if r.ok:
            return [True, r.json()["id"]]
    
        # If it did not send, retry
        else:
            print("caught " + str(r.status_code) + " when trying to send message.")
            return [False, ""]


def editmessage(rs, message, convid, messageid):
    # edit messages using the messages/messageid/edit endpoint
    data = {
        "content": message,
        "attachments": [],
    }
    r = rs.post('https://api-test.everskies.com/user/message/' + str(convid) + '/messages/' + str(messageid) + '/edit',
                data=json.dumps(data))
    return r


def deletemessage(rs, convid, messageid):
    # Delete messages using the messages/messageid/delete endpoint
    r = rs.delete(
        'https://api-test.everskies.com/user/message/' + str(convid) + '/messages/' + str(messageid) + '/delete')
    return r


def cbRP(data, convid, rs):
    # ChatBot RePly
    msg = data["event"]["content"]
    """Do not import this function alone. Requires EverskiesNamespace as ns"""
    # Send 'Please wait for response', request response from api, edit original message to response + bot indicator
    # Will fail if token needs to be refreshed.
    smsg = messageuser(
        "```This is an automatically generated reply, and will be edited shortly.```"
        "\n```To recieve a list of commands, send '.help'.```"
        "\n```Sending chatbot request. This may take a few seconds.```"
        "\n```To disable the ai, type .ai```",
        convid, rs)
    # Create new temp var for edit request later
    if smsg[0]:
        lmsid = smsg[1]
    else:
        return False
    # Will await response from api
    rspn = sendData(str(msg))
    # Edit original message
    r = editmessage(rs, ('🤖: ' + str(rspn)), convid, lmsid)
    if r.status_code == 500:
        import ast
        bad_words = ast.literal_eval(r.json()["message"])
        for bad_word in bad_words:
            rspn = rspn.replace(bad_word, '[CENSORED]')
        editmessage(rs, ('🤖: ' + str(rspn)), convid, lmsid)
    # When done, log:
    print(bcolors.OKGREEN + "Chatbot has responded to msg: '%s'; with response: '%s'." % (msg, rspn) + bcolors.ENDC)
    webhookHandler.webhookhandler(config.wconfig["DAIWebhook"], data, "ai_response", rspn)
    return True


def handle(data, token, exit, retry, user):
    """Always run on its own thread - Else sys.exit() will call, quitting program."""
    rs = requests.Session()
    rs.headers.update({
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.36 ",
        "authorization": "Bearer " + token
    })
    """Message event response from websocket"""
    # logging shit lol
    print("===New message detected===")
    ca = data["event"]
    # Check if it is a user message
    if "user" in ca:
        msguser = data["event"]["user"]
        convid = data["event"]["conversation_id"]
        print(bcolors.OKCYAN + "user " + msguser["alias"] + " sent the message: " + ca["content"] + bcolors.ENDC)
        print("===================")
        # Print message info to console
        if msguser["alias"] == user["alias"]:
            print("this is literally me")
            # Check for most common indicators of bot response)
            if (ca["content"][0:2]) in ["🤖:", "``", "!["]:
                print(bcolors.OKBLUE + "this is probably a chatbot response lol" + bcolors.ENDC)

            # Notify when administrator command detected (as they are significant)
            elif (ca["content"][0]) == bconfig["aprefix"]:
                print(ca["content"][0:2])
                print(bcolors.HEADER + "Admin command detected: ", ca["content"] + bcolors.ENDC)
                extra = [
                    # title
                    "ADMIN COMMAND DETECTED",
                    # desc
                    ca["content"],
                    # Custom field enabled?
                    False,
                    # Custom field name
                    "",
                    # Custom field value
                    ""
                ]
                webhookHandler.webhookhandler(config.wconfig["DMesgBWebhook"], data, "admincmd", extra)
                # Check for exit command
                if (ca["content"]).lower()[1::] == "exit":
                    # Check for exit command
                    exit = True
                    sys.exit()

                # eval and message back
                else:
                    commandResponse = adminCBCMD.interpretCommand(data)
                    if commandResponse[0]:
                        a = messageuser(str(commandResponse[1]), convid, rs)
                        if not a[0]:
                            retry.append(["messageuser", [str(commandResponse[1]), convid]])
                            sys.exit()
                    else:
                        print(
                            bcolors.FAIL + "Admin command: " + ca[
                                "content"] + " has failed to execute." + bcolors.ENDC)

            # Check for normal commands from user
            elif (ca["content"][0]) == bconfig["prefix"]:
                commandResponse = chatbotcommands.interpretCommand(data)
                if commandResponse[0]:
                    a = messageuser(str(commandResponse[1]), convid, rs)
                    if not a[0]:
                        retry.append(["messageuser", [str(commandResponse[1]), convid]])
                        sys.exit()
            # Not a handled command / Not a command
            else:
                print("not a command lol")
        #it is not me
        else:
            # Check if user is blacklisted
            if msguser['id'] in config.blacklist:
                # If user is blacklisted:
                # Notify of blacklisted user message
                webhookHandler.webhookhandler(config.wconfig["DMesgBWebhook"], data, "message", "blacklisted")
                # Annoy specific users in blacklist LOL
                if msguser['alias'] in config.annoy:
                    from random import choice
                    fun = ''.join(choice((str.upper, str.lower))(c) for c in ca['content'])
                    a = messageuser(fun, convid, rs)
                    if not a[0]:
                        retry.append(["messageuser", [fun, convid]])
                        sys.exit()
                # Basic logging shit
                print(bcolors.WARNING + "This user is blacklisted." + bcolors.ENDC)
            else:
                # User not blacklisted
                # Send data to WebhookHandler
                webhookHandler.webhookhandler(config.wconfig["DMesgWebhook"], data, "message")
                # Check if first message bot has seen:
                if msguser['id'] not in config.welcomed:
                    a = messageuser("Hi!", convid, rs)
                    if not a[0]:
                        retry.append(["dm", data])
                        sys.exit()
                    time.sleep(.05)
                    messageuser((chatbotcommands.welcomeUser(data)), convid, rs)
                    config.welcomed.append(msguser['id'])
                    config.writeDB("welcomed", config.welcomed)
                    print("Added %s to the Welcomed list!" % (msguser['id']))
                    sys.exit()

                # check for 'hi's
                if (ca["content"]).lower() in ["hi", "hihi", "hii", "hello", "hi.", "hii.", "hey", "hey." "hello."]:
                    a = messageuser(("🤖: hi " + msguser["alias"]), convid, rs)
                    if not a[0]:
                        retry.append(["messageuser", ["🤖: hi ", convid]])
                        sys.exit()
                    messageuser("![](https://cdn.discordapp.com/emojis/750180280005820466.png)", convid, rs)
                # Check if this looks like a command
                elif (ca["content"][0]) == bconfig["prefix"]:
                    # Use chatbotcommands to interpret data
                    commandResponse = chatbotcommands.interpretCommand(data)
                    if commandResponse[0]:
                        a = messageuser(str(commandResponse[1]), convid, rs)
                        if not a[0]:
                            retry.append(["messageuser", [str(commandResponse[1]), convid]])
                            sys.exit()
                # If it doesn't look like a command:
                else:
                    if msguser['id'] in config.disabled:
                        print("User has disabled bot. No response.")
                    # Check if user has enabled AI
                    elif msguser['id'] in config.enabled:
                        # Basic logging shit
                        print(bcolors.WARNING + "User %s-%s has initiated chatbot request '%s'" % (
                            msguser['alias'], msguser['id'], ca["content"]) + bcolors.ENDC)
                        cbRP(data, convid, rs)
                    # Check if user has disabled automatic "this is not a command" message

                    # User has not enabled AI and disabled the "this is not a command" message
                    else:
                        a = messageuser(
                            "Invalid command."
                            "\nType `.help` for a list of commands."
                            "\nType `.disable` to remove this response.",
                            convid, rs)
                        if not a[0]:
                            retry.append(["messageuser", [
                                "Invalid command."
                                "\nType `.help` for a list of commands."
                                "\nType `.disable` to remove this response.",
                                convid]])
                            sys.exit()
    # If not from a user
    else:
        # Check for trade offer - common
        try:
            if "content" in data["event"]:
                if data["event"]["content"] == "Trade Offer":
                    print(bcolors.OKBLUE + "boring trade shit" + bcolors.ENDC)
            # Check if it was a message edit
            elif "type" in data["event"]:
                if data["event"]["type"] == "edited":
                    print(bcolors.OKBLUE + "Message edited or smth lol, new content:" + bcolors.ENDC + data["event"][
                        "content"])
                elif data["event"]["type"] == "typing":
                    print("caught typing in dmhandler, ignore.")
            # this is new unhandled data
            else:
                print(bcolors.WARNING + "no case for this data: " + bcolors.ENDC, data)
                webhookHandler.webhookhandler(config.wconfig["DMesgBWebhook"], data, "error",
                                              "Unknown Data Type in messageevent/user in DMHandler:")

        except KeyError:
            webhookHandler.webhookhandler(config.wconfig["DErrorWebhook"], data, "error",
                                          "KeyError in messageevent/user ('Not User') in DMHandler")
    sys.exit()
