from telethon import TelegramClient, events

import utils


def main(name="", api_id="", api_hash="", index="1", count=1):
    client = TelegramClient(name, api_id, api_hash)

    with client:
        client.start()
        for i in range(int(count)):
            # utils.sleep(min=1000, max=3000)
            # client.send_message("@LastGangStandingBot", "/myfood")
            utils.sleep()
            client.send_message("@LastGangStandingBot", index)
