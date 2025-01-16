from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import *
import asyncio, secrets

user_bot = TelegramClient(StringSession(Var.SESSION_STRING),  2040, "b18441a1ff607e10a989891a5462e627")
dB = DataBase()
sch = AsyncIOScheduler()

async def start_bot() -> None:
    await user_bot.start()
    user_bot.me = await user_bot.get_me()
    print(user_bot.me.username, "is Online Now.")

async def send_to_bot(post_link, base_bot_id):
    await user_bot.send_message(base_bot_id, post_link)

def message_link(self):
    if hasattr(self.chat, "username") and self.chat.username:
        return f"https://t.me/{self.chat.username}/{self.id}"
    if (self.chat and self.chat.id):
        chat = self.chat.id
    elif self.chat_id:
        if str(self.chat_id).startswith("-" or "-100"):
            chat = int(str(self.chat_id).replace("-100", "").replace("-", ""))
        else:
            chat = self.chat_id
    else:
        return
    return f"https://t.me/c/{chat}/{self.id}"

@user_bot.on(events.NewMessage(outgoing=True, pattern=".listch"))
async def ch_list(event):
    data = dB.get_channels()
    txt = ""
    for i in data:
        txt += f"`{i['_id']}` - `{i['surplus_views']}+` - `{i['interval']}min`\n"
    await event.edit(txt)

@user_bot.on(events.NewMessage(outgoing=True, pattern=".bbot"))
async def badd(event):
    await dB.add_base_channel(event.chat_id)
    await event.edit("`Succesfully Added This Channel/Group As Base Channel`")

@user_bot.on(events.NewMessage(outgoing=True, pattern=".add"))
async def aadd(event):
    texts = event.text.split(" ")
    try:
        channel_id = int(texts[1])
        plus_views = int(texts[2])
        interval = int(texts[3])
    except:
        return await event.edit("Wrong Input!!")
    if not await dB.get_base_channel():
        return await event.edit("`First Add Base Channel`")
    await dB.add_channel(channel_id, plus_views, interval)
    await event.edit(f"`Successfully Added {channel_id} With Surplus Views Of {plus_views}`")

@user_bot.on(events.NewMessage(outgoing=True, pattern=".rem"))
async def aadd(event):
    texts = event.text.split(" ")
    try:
        channel_id = int(texts[1])
    except:
        return await event.edit("Wrong Input!!")
    await dB.rem_channel(channel_id)
    await event.edit(f"`Sucessfully Removed {channel_id} From Watch!`")

@user_bot.on(events.NewMessage())
async def k(e: Message):
    yes, views, interval = await dB.is_channel_on_list(e.chat_id)
    if yes:
        print("recieved")
        base_bot_id = await dB.get_base_channel()
        current_views = e.views
        final_views = current_views + views
        asyncio.create_task(deleter(e.id, final_views, e.chat_id ,base_bot_id, interval, message_link(e)))

async def deleter(fwd_msg_id, final_views, chat_id , base_bot_id, time, post_link):
    print("started")
    sch_id = secrets.token_hex(6)
    sch.add_job(send_to_bot, "interval", minutes=time, args=(post_link, base_bot_id), id=sch_id)
    try:
        while True:
            msg = await user_bot.get_messages(chat_id, ids=[fwd_msg_id])
            if msg[0].views >= final_views:
                sch.remove_job(sch_id)
                return await user_bot.delete_messages(chat_id, fwd_msg_id)
            await asyncio.sleep(20)
    except:
        await user_bot.delete_messages(chat_id, fwd_msg_id)
        sch.remove_job(sch_id)

sch.start()
user_bot.loop.run_until_complete(start_bot())
user_bot.run_until_disconnected()