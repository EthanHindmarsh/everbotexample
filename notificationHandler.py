"""Handles user notifications for everskies chatbot - Seperate file as this is not a 'Chatbot' function but rather a
notification handler """

import webhookHandler
import config
import json
import requests
import time
import sys

rs = requests.Session()
rs.headers.update({
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/58.0.3029.110 Safari/537.36"})

dataTypesStr = {
    0: "COMMENT", 1: "COMMENT_REPLY", 2: "DISCUSSION_MENTION", 3: "COMMENT_MENTION", 4: "LEVEL_UP",
    5: "SUBMISSION_CHANGED", 6: "TYPE_ACHIEVEMENT", 7: "MAGAZINE_CHANGED", 8: "TRADE_CREATED",
    9: "TRADE_UPDATED", 10: "OUTLET_SOLD", 11: "OUTLET_EXPIRED", 12: "OUTLET_OUTBID",
    13: "PROFILE_COMMENT", 14: "FRIEND_REQUEST", 15: "FRIEND_REQUEST_ACCEPTED",
    16: "REPORT_CREATED", 17: "PREMIUM_PAID", 18: "UNKNOWNONE", 19: "UNKNOWNTWO", 20: "UNKNOWNTHREE"
}


def refresh_token():
    from bcolors import bcolors
    # Get new access token
    print(bcolors.OKBLUE + "Refreshing access token" + bcolors.ENDC)
    r = rs.post("https://api-test.everskies.com/user/refresh-token", json={"token": config.bconfig["refresh_token"]})
    if r.ok:
        rs.headers.update({
            "authorization": "Bearer " + r.json()["access_token"]
        })
        return r.json()["access_token"]
    else:
        print(bcolors.FAIL + "Could not refresh token" + bcolors.ENDC)


def FRIEND_REQUEST(data):
    print("Caught friend request. Attempting to accept!")
    # Request URL: https://api-test.everskies.com/user/friends/112568/accept
    if (json.loads(data["event"]["content"])["friend_request"]["message"]) is not None:
        message = (json.loads(data["event"]["content"])["friend_request"]["message"])
    else:
        message = ""
    extra = [
        # title
        "New friend request:",
        # desc
        message,
        # Custom field enabled?
        True,
        # custom field
        "/friends/UID/accept Status Code:"]

    # Try to accept friend request
    r = rs.post('https://api-test.everskies.com/user/friends/' + str(data["event"]["sourceUser"]["id"]) + '/accept')

    # check if message sent correctly
    if r.ok:
        extra.append(500)
        webhookHandler.webhookhandler(config.wconfig["DINotificationWebhook"], data, "notification", extra)
        print("lol friend request accepted")
        return True
    # If it did not send, retry
    else:
        print("caught " + str(r.status_code) + " when trying to accept friend.")
        attempts = 0
        extra.append(r.status_code)
        webhookHandler.webhookhandler(config.wconfig["DINotificationWebhook"], data, "notification", extra)
        while attempts < 10:
            refresh_token()
            if r.status_code != 200:
                r = rs.post(
                    'https://api-test.everskies.com/user/friends/' + str(data["event"]["sourceUser"]["id"]) + '/accept')
                print("refreshed token and attempted to send message again. Response: ", r.status_code)
                time.sleep(0.5)
            else:
                return True
            attempts += 1


def commenthandler(data, ntype):
    # print("Caught comment!: ")
    # print(data)
    # "reply_id":2572710}',
    pdata = json.loads(data['event']['content'])
            #'{"profile_unique_id":"tru-113451","reply_id":3728418}'
    replyid = pdata['reply_id']
            #"reply_id":3728418}

    # removes "referenced before assignment" error in IDE lol
    path = "none"
    discussionuniqueid = "none"
    durl = "none"
    url = "none"

    if ntype == "forums":
        discussionuniqueid = pdata['discussion_unique_id']
        if discussionuniqueid:
            path = "discussion/" + str(pdata['discussion_unique_id'].split('-')[-1])
            durl = "(https://test.everskies.com/community/" + pdata['discussion_unique_id']+ "#" + str(replyid) + ")"
        else:
            path = "user/" + str(pdata['profile_unique_id'].split('-')[-1])
            discussionuniqueid = path
            durl = "(https://test.everskies.com/user/" + pdata["profile_unique_id"] + "/" + "guestbook#" + str(
            replyid) + ")"
        url = config.wconfig["DNotificationWebhook"]
    elif ntype == "profile":
        path = "user/" + str(data['event']['user_id'])
        discussionuniqueid = path
        # 'event': {'id': 6350031, 'user_id': 113451
        url = config.wconfig["DINotificationWebhook"]
        durl = "(https://test.everskies.com/user/" + pdata["profile_unique_id"] + "/" + "guestbook#" + str(replyid) + ")"
    # !! Get Reply !!

    base = "https://api-test.everskies.com/" + str(path) \
           + "/replies?limit=5&sort=-posted_at&search=[{%22attribute%22:%22id%22," \
             "%22comparator%22:%22eq%22,%22value%22:" + str(replyid) \
           + "}]"
    #if error- print base and check what result is manually
    r = rs.get(base).json()

    comment = "Empty"
    for comments in r:
        comment = comments["content"]
    # !! Get Reply !!

    extra = [
        # title
        "New comment on "+ntype+"!",
        # desc
        comment,
        # Custom field enabled?
        True,
        # Custom field name
        "Discussion Unique ID:",
        # Custom field value
        # Example url embed:[webhook](https://support.discord.com/hc/en-us/articles/228383668)
        str("[" + str(discussionuniqueid) + "]" + durl)
    ]
    dtype = data["event"]["type"]
    dtype = dataTypesStr.get(dtype).lower()

    webhookHandler.webhookhandler(url, data, dtype, extra)


def COMMENT(data):
    commenthandler(data, "forums")

def COMMENT_REPLY(data):
    commenthandler(data, "forums")

def COMMENT_MENTION(data):
    commenthandler(data, "forums")


def DISCUSSION_MENTION(data):
    pass


def LEVEL_UP(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught LEVEL_UP")


def SUBMISSION_CHANGED(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught SUBMISSION_CHANGED")


def TYPE_ACHIEVEMENT(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught TYPE_ACHIEVEMENT")


def MAGAZINE_CHANGED(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught MAGAZINE_CHANGED")


def TRADE_CREATED(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught TRADE_CREATED")


def TRADE_UPDATED(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught TRADE_UPDATED")


def OUTLET_SOLD(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught OUTLET_SOLD")


def OUTLET_EXPIRED(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught OUTLET_EXPIRED")


def OUTLET_OUTBID(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught  OUTLET_OUTBID")


def PROFILE_COMMENT(data):
    commenthandler(data, "profile")


def FRIEND_REQUEST_ACCEPTED(data):
    #pass to webhook handler, data can be handled there
    webhookHandler.webhookhandler(config.wconfig["DINotificationWebhook"], data, "friend_request_accepted",
                                  ["Friend Request Accepted!", None, False])


def REPORT_CREATED(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught REPORT_CREATED")


def PREMIUM_PAID(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught PREMIUM_PAID")


def UNKNOWNONE(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught UNKNOWNONE")


def UNKNOWNTWO(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught UNKNOWNTWO")


def UNKNOWNTHREE(data):
    webhookHandler.webhookhandler(config.wconfig["DNotificationWebhook"], data, "error", "Caught UNKNOWNTHREE")


dataTypes = {
    0: COMMENT,
    1: COMMENT_REPLY,
    2: DISCUSSION_MENTION,
    3: COMMENT_MENTION,
    4: LEVEL_UP,
    5: SUBMISSION_CHANGED,
    6: TYPE_ACHIEVEMENT,
    7: MAGAZINE_CHANGED,
    8: TRADE_CREATED,
    9: TRADE_UPDATED,
    10: OUTLET_SOLD,
    11: OUTLET_EXPIRED,
    12: OUTLET_OUTBID,
    13: PROFILE_COMMENT,
    14: FRIEND_REQUEST,
    15: FRIEND_REQUEST_ACCEPTED,
    16: REPORT_CREATED,
    17: PREMIUM_PAID,
    18: UNKNOWNONE,
    19: UNKNOWNTWO,
    20: UNKNOWNTHREE
}


def notificationhandler(data, token, mode=None):
    dtype = data["event"]["type"]
    print("caught notif dtype: ", dtype)
    # print("dtype = " + str(dtype))
    rs.headers.update({
        "authorization": "Bearer " + token
    })
    try:
        # Declare func
        func = dataTypes.get(dtype)
        # Check if func exists // Execute the function
        func(data)
        a = True
    except (KeyError, TypeError) as error:
        print("dtype " + str(dtype) + " did not handle successfully.")
        webhookHandler.webhookhandler(config.wconfig["DErrorWebhook"], data, "error",
                                      "KeyError - notificationHandler failed to handle notification: " + str(error))
        a = False
    if mode == "thread":
        sys.exit()
    else:
        return a
