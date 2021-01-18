#User Chatbot Commands .py
#Import pretty colors for printing!
#Import config data
import requests

import config
import webhookHandler


#These commands should only be run by trusted users.
#Every command must return a string or data that is convertable to string.

#Data none- optional arg.
def welcomeUser(data=None):
    return("I am a chatbot! My name is TruBOT; but you can call me whatever you like! \n"+
           "I am an artificial intelligence powered chatbot, and I am here to help you! \n"+
           "To get started, simply say anything! If at any point you wish to send a message to my owner, simply type `.disable` and I will stop talking to you.\n"+
           "If you are confused or would like to learn more, type '.help'.\n"+
           "The prefix for my commands is `.`\n"+
           "This message will only be sent once! Goodbye!")

#Data none- optional arg.
def catjpg(data=None):
    return("![](https://proxy.everskies.com/a/https://cdn.discordapp.com/attachments/618768746152198175/785535273320448020/catjpg.jpg)")

#Data none- optional arg.
def cbHelp(data=None):
    return("1. `.catjpg`\t: catjpg\n"+
           "2. `.disable`\t: Prevent automatic chatbot responses.\n"+
           "3. `.info`\t: Learn about me!\n"+
           "4. `.ai`\t: Allow the AI chatbot to learn from / speak to you, you can disable by running the command again\n"+
           "5. `.catfact`\t: Send a cool cat fact!\n"+
           "6. `.joke`\t: Send a funny joke!\n"+
           "To use the commands just type the name before the :\n"+
           "For example to get a catjpg you would send \".catjpg\" (without the quotes)\n"+
           "If the command is not working then try again\n"+
           "The prefix for my commands is `.`")

#Data none- optional arg.
def cbInfo(data=None):
    return("Hi!\n"+
           "To get started, try `.ai`! This will allow you to talk to me!\n"+
           "If at any point you wish to send a message directly to my owner, simply type `.disable` and I will stop talking to you.\n"+
           "If you are confused or would like to learn more, type '.help'.\n"+
           "The prefix for my commands is `.`")

def cbcDisable(data):
    msguser = data["event"]["user"]
    newDisable=config.invDisable([msguser['id']])
    if newDisable:
        return("Okay! The bot will no longer respond to your non-command messages. To undo this, type '.disable' again.")
    else:
        return("Okay! Re-enabled the bot!")

def cbcEnable(data):
    msguser = data["event"]["user"]
    print(msguser['id'])
    newEnable=config.invEnable([msguser['id']])
    if newEnable:
        return("Okay! Enabled the ai!")
    else:
        return("Okay! The ai will no longer respond to your messages. To continue talking to the AI, simply send '.ai' again.")
    
#Data=None, args optional
def catFact(data=None):
    #we really dont need it lol
    data=None
    r = requests.get('https://some-random-api.ml/facts/cat?key=' + config.bconfig["apikey"] + '')
    if r.status_code == 429:
        return("Please try again later :(")
    else:
        return("🤖: "+r.json()["fact"])

#data=None, args optional
def joke(data=None):
    #we really dont need the data
    data=None
    r=requests.get('https://some-random-api.ml/joke?key=' + config.bconfig["apikey"] + '')
    if r.status_code == 429:
        return("Please try again later :(")
    else:
        return("🤖: "+r.json()["joke"])

def interpretCommand(data):
    ca = data["event"]
    #Remove case sensitivity, Purge prefix from message
    execute=((ca["content"]).lower())[1::]
    switcher = {
            "catjpg" : catjpg,
            "help" : cbHelp,
            "info" : cbInfo,
            "disable" : cbcDisable,
            "ai" : cbcEnable,
            "catfact" : catFact,
            "joke" : joke
    }
    #Check if command exists
    try:
        # Get the function from switcher dictionary
        func = switcher.get(execute)
        # Execute the function
        response=[True, func(data)]
        webhookHandler.webhookhandler(config.wconfig["DCMDWebhook"], data, "cmd", response)
        return(response)
    #If not a function
    except (KeyError, TypeError) as error:
        response=[False, ""]
        webhookHandler.webhookhandler(config.wconfig["DCMDWebhook"], data, "cmd", response)
        #If command does not exist, return False
        return(response)

#Notify when file loaded.
print("Chatbot commands loaded!")
