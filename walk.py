from telethon.sync import TelegramClient, events
from prettytable import PrettyTable

import asyncio
import random
import re
import utils
from datetime import datetime, timedelta

BOT_STATE = {"enabled": True}
STATE = {}
CUR_BUILD = ""
CUR_ROOM = ""
LAST_EVENT = datetime.now()
# BOT_NAME = "@czo_offical_bot"
BOT_NAME = "@LastGangStandingBot"
CURRENT_POSITION = 0


async def sleep():
    random_number = random.randint(500, 1000)
    await asyncio.sleep(0.001 * random_number)


async def worker(name, client, quiet):
    global BOT_STATE, STATE, CUR_BUILD, CUR_ROOM, LAST_EVENT, BOT_NAME, CURRENT_POSITION

    while True:
        await sleep()

        if "enabled" not in BOT_STATE or not BOT_STATE["enabled"]:
            continue

        # print("!!test!!")

        message = "⚔️ Дать отпор"
        if int(CURRENT_POSITION) in quiet:
            message = "🏃 Сбежать"

        if LAST_EVENT < datetime.now() - timedelta(seconds=5):
            LAST_EVENT = datetime.now()

            if CUR_ROOM:
                print(f"{name} -> click:", CUR_ROOM)
                await client.send_message(BOT_NAME, CUR_ROOM)
                continue
            if CUR_BUILD == message:
                print(f"{name} -> click:", message)
                await client.send_message(BOT_NAME, message)
                continue
            if CUR_BUILD:
                print(f"{name} -> click:", "⬅️ Выйти из здания")
                await client.send_message(BOT_NAME, "⬅️ Выйти из здания")
                continue

            print(f"{name} -> click:", message)
            await client.send_message(BOT_NAME, message)


async def check_rooms(client, event, key):
    global BOT_STATE, STATE, CUR_BUILD, CUR_ROOM, BOT_NAME
    if key == '👤 Профиль':
        return

    if event.message.buttons:
        row = event.message.buttons[0]
        for button in row:
            b_key = button.text
            if "rooms" in STATE[key]:
                if b_key in STATE[key]["rooms"]:
                    if STATE[key]["rooms"][b_key]["state"] == "💩":
                        utils.sleep()
                        print("click:", b_key)
                        await sleep()
                        await client.send_message(BOT_NAME, b_key)
                        CUR_ROOM = b_key
                        break


def check_state() -> bool:
    global BOT_STATE, STATE, CUR_BUILD, CUR_ROOM, BOT_NAME
    clear = False

    if CUR_BUILD != "":
        if CUR_BUILD in STATE and "rooms" in STATE[CUR_BUILD]:
            clear = all(STATE[CUR_BUILD]["rooms"][x].get("state") == "✅" for x in STATE[CUR_BUILD]["rooms"])
        if clear:
            STATE[CUR_BUILD]["state"] = "✅"

    return clear


def parse_intervals(text):
    result = []
    # Разделяем строку по запятым
    parts = text.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            # Если это диапазон, разделяем по дефису
            start, end = map(int, part.split('-'))
            # Добавляем все числа от start до end включительно
            result.extend(range(start, end + 1))
        else:
            # Если это одиночное число
            if part:  # проверка на пустую строку
                result.append(int(part))

    return result


def main(name="", api_id="", api_hash="", start=20, finish=64, pauses="", quiet=""):
    global BOT_STATE, STATE, CUR_BUILD, CUR_ROOM, LAST_EVENT, BOT_NAME

    client = TelegramClient(name, api_id, api_hash)
    pauses = parse_intervals(pauses)
    quiet = parse_intervals(quiet)

    @client.on(events.NewMessage(chats='me'))
    async def handler(event):
        # event.message.out указывает, что сообщение отправлено вами
        if event.message.out and event.text.startswith("/lgs "):
            print(f"Поймано сообщение самому себе: {event.text}")

            if event.text == '/lgs disabled':
                BOT_STATE["enabled"] = False

            if event.text == '/lgs enabled':
                BOT_STATE["enabled"] = True

    @client.on(events.NewMessage(chats=BOT_NAME, outgoing=True))
    async def my_outgoing_handler(event):
        global BOT_STATE, STATE, CUR_BUILD, CUR_ROOM, LAST_EVENT, BOT_NAME

        if "enabled" not in BOT_STATE or not BOT_STATE["enabled"]:
            return

        LAST_EVENT = datetime.now()

        content = event.raw_text
        print(f'Текст: {content}')
        # CUR_ROOM = event.raw_text
        if CUR_BUILD == "":
            for b in STATE:
                if b in content:
                    CUR_BUILD = content
        else:
            CUR_ROOM = content

        if content == "⬅️ Назад":
            CUR_BUILD = ""
            CUR_ROOM = ""

        if content == "⬅️ Выйти из здания":
            CUR_BUILD = ""
            CUR_ROOM = ""

        print(f"state: {CUR_BUILD}, {CUR_ROOM}")

    @client.on(events.NewMessage(chats=BOT_NAME, incoming=True))
    async def my_new_message(event):
        global BOT_STATE, STATE, CUR_BUILD, CUR_ROOM, LAST_EVENT, BOT_NAME, CURRENT_POSITION

        if "enabled" not in BOT_STATE or not BOT_STATE["enabled"]:
            return

        LAST_EVENT = datetime.now()

        content = event.raw_text
        hunger, thirst = 0, 0
        if "Ты отправляешься на следующую улицу" in content:
            STATE = {}
            CUR_BUILD, CUR_ROOM = "", ""
            r = re.match(r'.* 🍗 Голод: (\d+)% \| 💧 Жажда: (\d+)%', content, re.DOTALL)
            if r:
                print("Голод,Жажда:", r.groups())
                hunger, thirst = int(r.group(1)), int(r.group(2))
        if "Ты ещё в пути к следующей улице…" in content:
            LAST_EVENT = datetime.now() + timedelta(minutes=1)
            STATE = {}
            CUR_BUILD, CUR_ROOM = "", ""
            r = re.match(r'.* 🍗 Голод: (\d+)% \| 💧 Жажда: (\d+)%', content, re.DOTALL)
            if r:
                print("Голод,Жажда:", r.groups())
                hunger, thirst = int(r.group(1)), int(r.group(2))

        # if (hunger+thirst) > 20:
        #     print("квас!!")
        #     await sleep()
        #     await client.send_message(BOT_NAME, "/myfood8")
        if hunger > 40:
            print("поел!!")
            await sleep()
            await client.send_message(BOT_NAME, random.choice(
                ["/myfood1", "/myfood2", "/myfood3", "/myfood4", "/myfood9", ]
            ))
        if thirst > 40:
            print("попил!!")
            await sleep()
            await client.send_message(BOT_NAME, random.choice(
                ["/myfood4", "/myfood5", "/myfood7", "/myfood8", "/myfood9", "/myfood10", ]
            ))

        if "Ты используешь" in content or "Ты отправляешься на следующую улицу" in content:
            LAST_EVENT = datetime.now() + timedelta(minutes=1)
            print("!!PAUSE!!", datetime.now(), LAST_EVENT)

        if "Ты отправляешься обратно" in content:
            LAST_EVENT = datetime.now() + timedelta(minutes=5)
            print("!!PAUSE!!", datetime.now(), LAST_EVENT)

        if "Лагерь фракции Ультиматы" in content:
            LAST_EVENT = datetime.now() + timedelta(minutes=5)
            await sleep()
            await client.send_message(BOT_NAME, "🚪 Выйти на вылазку")
            print("🚪 Выйти на вылазку", "!!PAUSE!!", datetime.now(), LAST_EVENT)

        if "Дизель чихает и оживает" in content or "🚛 Едешь на грузовике" in content:
            LAST_EVENT = datetime.now() + timedelta(minutes=5)
            print("!!PAUSE!!", datetime.now(), LAST_EVENT)

        if "зачищена!" in content or "с усилием выламываешь её! 💪" in content:
            if CUR_BUILD != "" and CUR_ROOM != "":
                if CUR_ROOM in STATE[CUR_BUILD]["rooms"]:
                    STATE[CUR_BUILD]["rooms"][CUR_ROOM]["state"] = "✅"

            check_state()
            await check_rooms(client, event, CUR_BUILD)

        if "Ты обыскал всю комнату, но ничего в ней нашел, в другой раз повезет" in content:
            print(f"state: {CUR_BUILD}, {CUR_ROOM}")
            if CUR_BUILD != "" and CUR_ROOM != "":
                if CUR_ROOM in STATE[CUR_BUILD]["rooms"]:
                    STATE[CUR_BUILD]["rooms"][CUR_ROOM]["state"] = "✅"

            check_state()
            await check_rooms(client, event, CUR_BUILD)

        if "км от лагеря" in content:
            r = re.match(r'.* (\d+) км от лагеря', content, re.DOTALL)
            if r:
                current_position = r[1]
                CURRENT_POSITION = current_position
                print(f"!!ты в {current_position} км от лагеря!! {datetime.now()}")
                if int(current_position) == 1:
                    await sleep()
                    await client.send_message(BOT_NAME, "🚛 Автостоянка")
                    utils.sleep()
                    cmd = "🚛 50 км — 24 000 ₽"
                    if int(start) == 10:
                        cmd = "🚛 10 км — 3 000 ₽"
                    if int(start) == 20:
                        cmd = "🚛 20 км — 6 000 ₽"
                    if int(start) == 30:
                        cmd = "🚛 30 км — 10 500 ₽"
                    if int(start) == 40:
                        cmd = "🚛 40 км — 16 500 ₽"
                    await sleep()
                    await client.send_message(BOT_NAME, cmd)
                    await sleep()
                    await client.send_message(BOT_NAME, "✅ Точно ехать")
                if int(current_position) > int(finish):
                    await sleep()
                    await client.send_message(BOT_NAME, "⬅️ В лагерь")
                    await sleep()
                    await client.send_message(BOT_NAME, "⬅️ В лагерь")
                    print("⬅️ В лагерь")
                    return

                if int(current_position) in quiet:
                    LAST_EVENT = datetime.now() + timedelta(minutes=1)
                    print("!!PAUSE!!", datetime.now(), LAST_EVENT)
                    await sleep()
                    await client.send_message(BOT_NAME, "➡️ Следующая улица")
                    return

                # print("Обнаружены кнопки:")
                if event.message.buttons:
                    row = event.message.buttons[0]
                    for button in row:
                        key = button.text
                        if key not in STATE:
                            STATE[key] = {"name": key, "state": "💩", "rooms": {}}
                    idx = 0
                    all_clear = False

                    if STATE:
                        all_clear = True
                    for button in row:
                        key = button.text
                        if key in STATE and int(current_position) >= int(start) and int(current_position) <= int(
                                finish) and current_position not in pauses:
                            if STATE[key]["state"] == "💩":
                                await sleep()
                                await client.send_message(BOT_NAME, key)
                                CUR_BUILD = key
                                all_clear = False
                                break
                        idx = idx + 1

                    if len(STATE) == 2 and "⚔️ Дать отпор" in STATE:
                        all_clear = False

                    if all_clear and int(current_position) >= int(start) and int(current_position) <= int(
                            finish) and current_position not in pauses:
                        LAST_EVENT = datetime.now() + timedelta(minutes=1)
                        print("!!PAUSE!!", datetime.now(), LAST_EVENT)
                        await sleep()
                        await client.send_message(BOT_NAME, "➡️ Следующая улица")
                if STATE:
                    table = PrettyTable()
                    table.field_names = ["Здания"] + list(STATE.keys())
                    states = [obj.get("state") for obj in STATE.values()]
                    table.add_row(["Статус"] + list(states))

                    rooms = [obj.get("rooms", []) for obj in STATE.values()]
                    # print("ROOMS", rooms)
                    rrr = []
                    for rr in rooms:
                        names = []
                        if rr:
                            for r in rr:
                                names.append(rr[r]["name"] + " - " + rr[r]["state"])
                        if names:
                            rrr.append("\n".join(names))
                        else:
                            rrr.append("пусто")
                    if rrr:
                        table.add_row(["Комнаты"] + list(rrr))
                    print(table)

        if "Ты подходишь к зданию" in content:
            for key in STATE:
                r = re.match(r'Ты подходишь к зданию ' + key, content)
                if r:
                    if "Нет, тихо" in content:
                        STATE[key]["state"] = "✅"
                    else:
                        await check_rooms(client, event, key)
                    first_click = False
                    if event.message.buttons:
                        row = event.message.buttons[0]
                        if row and row[0].text != "⚔️ Дать отпор":
                            if "rooms" in STATE[key] and len(STATE[key]["rooms"]) == 0:
                                first_click = True

                            for button in row:
                                b_key = button.text
                                if "rooms" in STATE[key]:
                                    if b_key not in STATE[key]["rooms"]:
                                        STATE[key]["rooms"][b_key] = {"name": b_key, "state": "💩"}
                            if first_click:
                                await sleep()
                                await client.send_message(BOT_NAME, row[0].text)

        if event.message.buttons:
            row = event.message.buttons[0]

            click = False
            for button in row:
                b_key = button.text
                if b_key == "⚔️ Убить всех":
                    await sleep()
                    await client.send_message(BOT_NAME, b_key)
                    click = True

            if not click:
                for button in row:
                    b_key = button.text
                    if b_key == "⚔️ Убить одного":
                        await sleep()
                        await client.send_message(BOT_NAME, b_key)
                        click = True

            if check_state():
                for row in event.message.buttons:
                    for button in row:
                        b_key = button.text
                        if b_key == "⬅️ Выйти из здания":
                            CUR_BUILD = ""
                            CUR_ROOM = ""
                            await sleep()
                            await client.send_message(BOT_NAME, b_key)

    with client:
        worker_task = client.loop.create_task(worker('worker-1', client, quiet))
        # client.send_message(BOT_NAME, "🚪 Выйти на вылазку")
        client.run_until_disconnected()
        worker_task.cancel()