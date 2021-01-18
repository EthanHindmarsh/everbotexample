from discord_webhook import DiscordEmbed, DiscordWebhook
import time
import datetime
import requests
import sys

def wherror(url, data, dtype, extra):
    if extra is None:
        extra = " "
    # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    disEmbed = {
        "content": "",  # "message content",
        # "username" : "custom username",
        # "avatar_url" : "url",
        # "tts" : False,
        # "file" : file,
        # embeds : defined below
        # "allowed_mentions" : None
    }
    # for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    timestamp = str(datetime.datetime.utcfromtimestamp(time.time()))
    disEmbed["embeds"] = [{
        "title": "Webhook Handler Error",
        "description": "WebhookHandler.py was unable to handle a request. Data is as follows: " + str(data),
        # str is hex - converts to decimal
        "color": int('242424', 16),
        "fields": [
             {
                "name": "Extra:",
                "value": str(extra)
              }],
        "footer": {
            "text": 'Data Type: ' + dtype,
            "icon_url": "https://cdn.discordapp.com/avatars/274771396792680449/a_cc795b596f39ef5a126724c08b45d4c8.png"
        },
        "timestamp": timestamp
    }
    ]

    result = requests.post(url, json=disEmbed)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
    return result


def customerror(url, data, dtype, extra):
    # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    disEmbed = {
        "content": "",  # "message content",x
        # "username" : "custom username",
        # "avatar_url" : "url",
        # "tts" : False,
        # "file" : file,
        # embeds : defined below
        # "allowed_mentions" : None
    }
    # for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    timestamp = str(datetime.datetime.utcfromtimestamp(time.time()))

    disEmbed["embeds"] = [{
        "title": str(extra),
        "description": str(data)[0:1500],
        # str is hex - converts to decimal
        "color": int('242424', 16),
        "footer": {
            "text": "Data Type:" + dtype,
        },
        "timestamp": timestamp,
    }
    ]

    result = requests.post(url, json=disEmbed)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
    return result


def chatbotResponse(url, data, dtype, extra):
    # Data = Original message data
    # Extra = [True/False, bot message]
    # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    disEmbed = {
        "content": "",  # "message content",x
        # "username" : "custom username",
        # "avatar_url" : "url",
        # "tts" : False,
        # "file" : file,
        # embeds : defined below
        # "allowed_mentions" : None
    }
    # for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    timestamp = str(datetime.datetime.utcfromtimestamp(time.time()))

    disEmbed["embeds"]=[{
              "title": 'New Bot Response',
              "description": extra[1],
              # str is hex - converts to decimal
              "color": int('242424',16),
              "fields": [
                {
                  "name": 'Original Message:',
                  "value": data["event"]["content"],
                  "inline": True
                },
                {
                  "name": "Command?:",
                  "value": str(extra[0]),
                  "inline": True
                },

                {
                  "name": 'Command author:',
                  "value": data["event"]["user"]["alias"],
                  "inline": True
                }
              ],
              "footer": {
                "text": 'Data Type: '+dtype,
              },
              "timestamp": timestamp,
            }
          ]
    result = requests.post(url, json=disEmbed)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
    return result


def message(url, data, dtype, extra):
    # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    disEmbed = {
        "content": "",  # "message content",x
        # "username" : "custom username",
        # "avatar_url" : "url",
        # "tts" : False,
        # "file" : file,
        # embeds : defined below
        # "allowed_mentions" : None
    }
    # for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    timestamp = str(datetime.datetime.utcfromtimestamp(time.time()))

    disEmbed["embeds"] = [{
          "title": 'New Message',
          "description": data["event"]["content"],
          # str is hex - converts to decimal
          "color": int('242424',16),
          "fields": [
              {
                  "name": 'User ID:',
                  "value": data["event"]["user"]["id"],
                  "inline": True
              },
              {
                  "name": 'Level:',
                  "value": data["event"]["user"]["level"],
                  "inline": True
              },
              {
                  "name": 'Role:',
                  "value": data["event"]["user"]["primary_role"],
                  "inline": True
              }
          ],
          "author": {
            "name": data["event"]["user"]["alias"],
            "url": "https://test.everskies.com/user/" + data["event"]["user"]["alias"] + "-" + str(data["event"]["user"]["id"]),
            "icon_url": "https://cdn-test.everskies.com/media/avatar/" + data["event"]["user"]["avatar_id"]
          },
          "footer": {
            "text": 'Data Type: ' + dtype
          },
          "timestamp": timestamp
        }
      ]
    if extra == "blacklisted":
        disEmbed["embeds"][0]["fields"].append(
              {
                  "name": 'Blacklisted:',
                  "value": 'True'
              })
    result = requests.post(url, json=disEmbed)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
    return result


def aiResponse(url, data, dtype, extra):
    # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    disEmbed = {
        "content": "",  # "message content",x
        # "username" : "custom username",
        # "avatar_url" : "url",
        # "tts" : False,
        # "file" : file,
        # embeds : defined below
        # "allowed_mentions" : None
    }
    # for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    timestamp = str(datetime.datetime.utcfromtimestamp(time.time()))

    disEmbed["embeds"] = [{
          "title": 'New Response:',
          "description": extra,
          # str is hex - converts to decimal
          "color": int('242424',16),
          "fields": [
            {
              "name": "Original Message:",
              "value": data["event"]["content"]
            }
          ],
          "author": {
            "name": data["event"]["user"]["alias"],
            "url": "https://test.everskies.com/user/" + data["event"]["user"]["alias"] + "-"
                    +str(data["event"]["user"]["id"]),
            "icon_url": "https://cdn-test.everskies.com/media/avatar/" + data["event"]["user"]["avatar_id"]
          },
          "footer": {
            "text": 'Data Type: ' + dtype,
          },
          "timestamp": timestamp
        }
      ]

    result = requests.post(url, json=disEmbed)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
    return result

def sendUC(url, data, dtype, extra):
    webhook = DiscordWebhook(url=url)
    embed = DiscordEmbed(title='Current number of Online Users:', description=str(data["event"]), color=242424)

    # set footer
    embed.set_footer(text=('Data Type: ' + dtype))

    # set timestamp (default is now)
    embed.set_timestamp()

    # add embed object to webhook
    webhook.add_embed(embed)
    response = webhook.execute()
    return response


def notification(url, data, dtype, extra):
    #extra [0] - Title
    #extra [1] - Desc
    #extra [2] - Custom field? True / False
    #extra [3] - Field name
    #extra [4] - Field value

    webhook = DiscordWebhook(url=url)
    embed = DiscordEmbed(title=extra[0], description=extra[1], color=242424)

    try:
        embed.set_author(name=data["event"]["sourceUser"]["alias"],
                     url=("https://test.everskies.com/user/" + data["event"]["sourceUser"]["alias"] + "-" + str(
                         data["event"]["sourceUser"]["id"])),
                     icon_url=("https://cdn-test.everskies.com/media/avatar/" + data["event"]["sourceUser"][
                         "avatar_id"]))
        embed.add_embed_field(name='User ID:', value=data["event"]["sourceUser"]["id"])
        embed.add_embed_field(name='Level:', value=data["event"]["sourceUser"]["level"])
        embed.add_embed_field(name='Role:', value=data["event"]["sourceUser"]["primary_role"])
    except KeyError:
       embed.set_author(name="Unknown")
       embed.add_embed_field(name="User ID:", value="Unknown")
    if extra[2]:
        embed.add_embed_field(name=extra[3], value=extra[4], inline=False)
    # set footer
    embed.set_footer(text=('Data Type: ' + dtype))

    # set timestamp (default is now)
    embed.set_timestamp()

    # add embed object to webhook
    webhook.add_embed(embed)
    response = webhook.execute()
    return response


# def othernotification(url, data, dtype, extra):
#    print("lol!")

def webhookhandler(url, data="Data is blank!", dtype="error", extra="Data is blank!", mode=None):
    switcher = {
        "message": message,
        "cmd": chatbotResponse,
        "ai_response": aiResponse,
        "error": customerror,
        "usercount": sendUC,
        "notification": notification,
        "admincmd": notification,
        "comment": notification,
        "comment_reply": notification,
        "discussion_mention": notification,
        "comment_mention": notification,
        "profile_comment": notification,
        "friend_request_accepted": notification,
        # "snotification" : othernotification,
        "daily-reward": customerror
    }
    # Check if command exists
    try:
        # Get the function from switcher dictionary - Lambda as a backup
        func = switcher.get(dtype)
        # Execute the function
        a=func(url, data, dtype, extra)
    except (KeyError, TypeError) as error:
        from config import wconfig
        url = wconfig["DErrorWebhook"]
        a=wherror(url, data, dtype, extra)
    if mode=="Thread":
        sys.exit()
    else:
        return a

"""[{
          "title": "Webhook Handler Error",
          "description": "Look its a [webhook](https://support.discord.com/hc/en-us/articles/228383668)",
          "url": "https://google.com?q=title%20url",
          # str is hex - converts to decimal
          "color": int('242424',16),
          "fields": [
            {
              "name": "field title",
              "value": "field value",
              "inline": True
            }
          ],
          "author": {
            "name": "Author",
            "url": "https://google.com?q=author%20url",
            "icon_url": "https://cdn.discordapp.com/avatars/376971748127670273/b010fdf9351ca205eacc9d4ab85131cb.png"
          },
          "footer": {
            "text": "Data Type: Test",
            "icon_url": "https://cdn.discordapp.com/avatars/376971748127670273/b010fdf9351ca205eacc9d4ab85131cb.png"
          },
          "timestamp": timestamp,
          "image": {
            "url": "https://cdn.discordapp.com/avatars/376971748127670273/b010fdf9351ca205eacc9d4ab85131cb.png"
          },
          "thumbnail": {
            "url": "https://cdn.discordapp.com/avatars/376971748127670273/b010fdf9351ca205eacc9d4ab85131cb.png"
          }
        }
      ]"""
