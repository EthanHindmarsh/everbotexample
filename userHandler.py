import webhookHandler
import config
import json
import time
import sys


def claim_reward(rs, retry, mode=None):
    print("Trying to claim reward lol")
    webhookHandler.webhookhandler(config.wconfig["DTradeWebhook"], "Function claim_reward called.", "daily-reward",
                                  "Trying to claim reward.")
    retry = 0
    from random import randint
    time.sleep(randint(10, 60))
    data = {
        "done": "true"
    }
    # Send message to user by conv id
    r = rs.post('https://api-test.everskies.com/user/claim-reward', data=json.dumps(data))

    # check if message sent correctly
    if r.ok:
        webhookHandler.webhookhandler(config.wconfig["DTradeWebhook"], str(r.status_code), "daily-reward",
                                      "Successfully claimed reward!")
        a = True


    # If it did not send, retry
    else:
        webhookHandler.webhookhandler(config.wconfig["DTradeWebhook"], str(r.status_code), "daily-reward",
                                      "Error in claiming reward. Will retry.")
        print("caught " + str(r.status_code) + " when trying to send message.")
        retry.append(["claimreward",mode])
        sys.exit()

    if mode == "thread":
        sys.exit()
    else:
        return a