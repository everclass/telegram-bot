import json

from httpx import AsyncClient
from nonebot import on_command
from nonebot.adapters.telegram import Bot
from nonebot.adapters.telegram.event import PrivateMessageEvent
from nonebot.typing import T_State

from .data_source import get_photo_bytes

csu_class = on_command("csu_class")
with open("student_info.json", "r", encoding="utf-8") as f:
    student_info = json.load(f)


def issemester(arg):
    result = False
    arg = arg.split("-")
    try:
        if (
            len(arg) == 3
            and int(arg[1]) - int(arg[0]) == 1
            and int(arg[2]) in range(1, 3)
        ):
            result = True
    except:
        pass
    return result


@csu_class.handle()
async def _(bot: Bot, event: PrivateMessageEvent, state: T_State):
    if "semester" in state:
        return

    state["semester"] = bot.config.semester
    for arg in str(event.message).strip().split(" "):
        if not arg.isascii():
            state["name"] = arg
        elif issemester(arg):
            state["semester"] = arg


@csu_class.got("name", prompt="你想查询谁的课表呢（请输入姓名）？")
async def _(bot: Bot, event: PrivateMessageEvent, state: T_State):

    student_list = []
    for k in student_info:
        if student_info[k]["name"] == state["name"]:
            student_list.append(k)

    if len(student_list) == 1:
        state["id"] = student_list[0]
    elif len(student_list) > 1:
        prompt_message = "找到了不止一个" + state["name"] + "，你找的是哪一个（请输入学号）？\n"
        for id in student_list:
            print(student_info[id].values())
            prompt_message += " ".join(student_info[id].values()) + "\n"
        await bot.send(event, prompt_message)
    else:
        await csu_class.finish("查无此人！")


@csu_class.got("id")
async def _(bot: Bot, event: PrivateMessageEvent, state: T_State):
    if (
        state["id"] in student_info
        and student_info[state["id"]]["name"] == state["name"]
    ):
        async with AsyncClient() as client:
            await client.post(
                f"{bot.telegram_config.api_server}bot{bot.telegram_config.token}/sendPhoto",
                data={"chat_id": event.chat.id},
                files={
                    "photo": get_photo_bytes(
                        state["id"], student_info[state["id"]], state["semester"]
                    )
                },
            )
    else:
        await bot.send(event, "学号不存在或与所查姓名不对应！")
