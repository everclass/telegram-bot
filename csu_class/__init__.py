import json
import os

from httpx import AsyncClient

from nonebot import on_command
from nonebot.adapters.telegram import Bot, MessageSegment
from nonebot.adapters.telegram.event import PrivateMessageEvent
from nonebot.typing import T_State

from .data_source import get_photo_bytes

csu_class = on_command("csu_class", priority=5)


@csu_class.got("name", prompt="你想查询谁的课表呢？")
async def _(bot: Bot, event: PrivateMessageEvent, state: T_State):
    name = state["name"]

    fp = open("student_info.json", "r", encoding="utf-8")
    student_info_json = fp.read()
    fp.close()
    student_info = json.loads(student_info_json)

    student_list = []
    for k in student_info:
        if student_info[k]["name"] == name:
            student_list.append(k)

    if len(student_list) == 1:
        state["id"] = student_list[0]
    elif len(student_list) > 1:
        prompt_message = "找到了不止一个" + name + "，你找的是哪一个（请输入学号）？\n"
        for id in student_list:
            prompt_message += " ".join(student_info[id].values()) + "\n"
        await bot.send(event, prompt_message)
    else:
        await csu_class.finish("查无此人")


@csu_class.got("id")
@csu_class.handle()
async def _(bot: Bot, event: PrivateMessageEvent, state: T_State):
    id = state["id"]
    name = state["name"]

    if not id or not name:
        return

    fp = open("student_info.json", "r", encoding="utf-8")
    student_info_json = fp.read()
    fp.close()
    student_info = json.loads(student_info_json)
    async with AsyncClient() as client:
        await client.post(
            f"{bot.telegram_config.api_server}bot{bot.telegram_config.token}/sendPhoto",
            data={"chat_id": event.chat.id},
            files={"photo": get_photo_bytes(id, student_info[id])},
        )
    await csu_class.finish()
