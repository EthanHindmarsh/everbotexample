# Everskies Work-In-Progress .py
import os
import threading
import time

import requests
from requests.exceptions import ConnectionError
import socketio
import urllib3
import json

import DMHandler
import config
import notificationHandler
import webhookHandler
import userHandler
from bcolors import bcolors
from config import bconfig

class EverskiesNamespace(socketio.ClientNamespace):
    """Handles all everskies communications."""
    rs = requests.Session()
    rs.headers.update({
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.36 "
    })
    # Init
    exit = False
    prefix = "."
    # user count counter lol
    ucx = 0
    retry = []

    def refresh_token(self):
        retries=10
        while True:
            retries-=1
            try:
                # Get new access token
                print(bcolors.OKBLUE + "Refreshing access token" + bcolors.ENDC)
                r = self.rs.post("https://api-test.everskies.com/user/refresh-token",
                                 json={"token": bconfig["refresh_token"]})
                if r.ok:
                    self.token = r.json()["access_token"]
                    self.rs.headers.update({
                        "authorization": "Bearer " + self.token
                    })
                    break
            except ConnectionError as err:
                time.sleep(1)
            if retries == 0:
                print(bcolors.FAIL + "Could not refresh token" + bcolors.ENDC)
                self.disconnect()
    def on_connect(self):
        # Notify when connected
        # refresh token, get user info, and authenticate
        print(bcolors.OKBLUE + "Connected" + bcolors.ENDC)
        self.refresh_token()
        try:
            self.rs.headers.update({
                "authorization": "Bearer " + self.token,
                "content-type": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            })
        #if initial refresh failed
        except AttributeError:
            print("Refresh_Token failed! Retrying")
            self.refresh_token()
        self.user = self.rs.get("https://api-test.everskies.com/user").json()
        self.emit("a", self.token)

    def on_connect_error(self, data):
        # Notify when there is a connection error, and print out the error
        print(bcolors.WARNING + "Connection Error" + bcolors.ENDC)
        print(data)

    def on_disconnect(self):
        # Notify when disconnected
        print(bcolors.WARNING + "Disconnected" + bcolors.ENDC)

    def on_a(self, data):
        print(data)
        # Connect to websocket, bind events to uuids
        print(bcolors.UNDERLINE + bcolors.HEADER + "Connecting to websocket" + bcolors.ENDC)
        if data:
            print(bcolors.BOLD + bcolors.OKGREEN + "Authentication successful" + bcolors.ENDC)
            self.emit("bind", [{"uuid": "messageevent", "options": None, "event": "message/event"}])
            self.emit("bind", [{"uuid": "usernotification", "options": None, "event": "user/notification"}])
            self.emit("bind", [{"uuid": "usercount", "options": None, "event": "user/count"}])
            self.emit("bind", [{"uuid": "userreward", "options": None, "event": "user/reward"}])
        else:
            print(bcolors.FAIL + "Authentication Failed" + bcolors.ENDC)
            self.refresh_token()
            self.emit("authenticate", {"access_token": self.token})

    def redo(self, retryl):
        print("Caught REDO. Data: ", retryl)
        # retry.append["dm", data]
        # [0] == "dm" - message needs to be re-eval'd - [1] will be message data
        # [0] == "messageuser" - message eval'd but reply did not send, [1][0] will be str to resend, [1][1] will be convid
        if retryl[0] == "messageuser":
            thread = threading.Thread(target=DMHandler.messageuser,
                                  args = (retryl[1][0], retryl[1][1], self.rs, "retry"))
            thread.start()
        elif retryl[0] == "dm":
            thread = threading.Thread(target=DMHandler.handle,
                                      args=(retryl[1], self.token, self.exit, self.retry, self.user))
            thread.start()
        elif retryl[0] == "claimreward":
            thread = threading.Thread(target=userHandler.claim_reward,
                                      args=(self.rs, self.retry, retryl[1]))
            thread.start()
        self.retry = []

    def on_users(self, data):
        print(data)
        print(data.decode('utf-8'))
    def on_event(self, data):
        print(data)
        if self.retry:
            self.refresh_token()
            self.rs.headers.update({
            "authorization": "Bearer " + self.token,
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            })
            self.redo(self.retry)
        if self.exit:
            print(bcolors.FAIL + "Self.EXIT: Disconnecting." + bcolors.ENDC)
            self.disconnect()
            exit()
            while True:
                time.sleep(100000)
        # print("Trying to understand: ", data)

        # usercount at top as it is most common - reduce if else usage
        if data["uuid"] == "usercount":
            print(data)
            # logging shit lol
            # user count interval sending
            config.writeCount(data["event"])
            self.ucx += 1
            if self.ucx == 2:
                thread = threading.Thread(target=webhookHandler.webhookhandler,
                                          args=(config.wconfig["DUserCountWebhook"], data, "usercount", None, "thread"))
                thread.start()
                self.ucx = 0
        # Direct message (DM)
        elif data["uuid"] == "messageevent":
            thread = threading.Thread(target=DMHandler.handle,
                                      args=(data, self.token, self.exit, self.retry, self.user))
            thread.start()
        # any notification
        elif data["uuid"] == "usernotification":
            # start on new thread to prevent sleep issues
            #notificationHandler takes creates its own rs - update
            thread = threading.Thread(target=notificationHandler.notificationhandler, args=(data, self.token, "thread"))
            thread.start()
        #user reward called
        elif data["uuid"] == "userreward":
            # start on new thread to prevent sleep issues
            # pass in RS to prevent cloned RS sessions - keep RAM limited
            thread = threading.Thread(target=userHandler.claim_reward, args=(self.rs, self.retry, "thread"))
            thread.start()

        # No idea what the fuck this is then LOL
        else:
            print(bcolors.FAIL + "No case for: " + bcolors.ENDC, data)
            # thread = threading.Thread(target=, args=)
            # thread.start()
            thread = threading.Thread(target=webhookHandler.webhookhandler, args=(
                config.wconfig["DErrorWebhook"], data, "error", "No case for data type in eschatbot:", "thread"))
            thread.start()


# check if bot is in insecure mode
if bconfig["insecure"]:
    urllib3.disable_warnings()
    sio = socketio.Client(ssl_verify=False, json=json)
    os.environ["CURL_CA_BUNDLE"] = ""
else:
    sio = socketio.Client(json=json, logger=True)

# start up bot
ns = EverskiesNamespace("/")
sio.register_namespace(ns)
sio.connect("wss://socket-test.everskies.com/socket.io/", transports=["websocket"])

