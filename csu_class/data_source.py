import re
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from prettytable import ALL, PrettyTable

from .config import *


def get_data(id, student_info):
    data = {
        "type": "xs0101",
        "xnxq01id": semester,
        "xs0101id": id,
        "xs": student_info["name"],
    }
    url = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp"
    req = requests.post(url, data=data)
    class_info = student_info
    class_info["semester"] = semester
    soup = BeautifulSoup(req.text, "html.parser")
    for week_day in range(1, 8):
        for class_time in range(1, 7):
            query_selector = (
                'div[id="'
                + re.findall(r"value=\"(.*)-7-1\">", req.text)[class_time - 1]
                + "-"
                + str(week_day)
                + '-2"] a'
            )
            for i in soup.select(query_selector):  # i 为 a 元素
                if not str(week_day) in class_info:
                    class_info[str(week_day)] = {}
                class_info[str(week_day)][str(class_time)] = {
                    "clsname": i.contents[0],
                    "teacher": "None"
                    if not i.select('font[title="老师"]')
                    else i.select('font[title="老师"]')[0].string,
                    "duration": "None"
                    if not i.select('font[title="周次"]')
                    else i.select('font[title="周次"]')[0].string,
                    "week": "None"
                    if not i.select('font[title="单双周"]')
                    else i.select('font[title="单双周"]')[0].string,
                    "location": "None"
                    if not i.select('font[title="上课地点教室"]')
                    else i.select('font[title="上课地点教室"]')[0].string,
                }

    return class_info


def get_table(class_info):
    t = PrettyTable(
        title=class_info["name"]
        + "("
        + class_info["college"]
        + " "
        + class_info["class"]
        + ")的"
        + class_info["semester"]
        + "课表"
    )
    for week_day in range(1, 8):
        class_list = []
        for class_time in range(1, 6):
            try:
                class_tmp = class_info[str(week_day)][str(class_time)]
                class_list.append(
                    class_tmp["clsname"]
                    + "\n"
                    + class_tmp["teacher"]
                    + "\n"
                    + class_tmp["duration"]
                    + "("
                    + class_tmp["week"]
                    + ")\n"
                    + class_tmp["location"]
                )
            except:
                class_list.append("")
        t.add_column(str(week_day), class_list)
    return t.get_string(header=False, hrules=ALL)


def get_photo(class_info_table):
    space = 5
    font = ImageFont.truetype("wqy-zenhei-mono.ttf", 16, encoding="utf-8")
    im = Image.new("RGB", (10, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im, "RGB")
    # 根据插入图片中的文字内容和字体信息，来确定图片的最终大小
    img_size = draw.multiline_textsize(class_info_table, font=font)
    # 图片初始化的大小为10-10，现在根据图片内容要重新设置图片的大小
    im_new = im.resize((img_size[0] + space * 2, img_size[1] + space * 2))
    del draw
    del im
    draw = ImageDraw.Draw(im_new, "RGB")
    # 批量写入到图片中，这里的multiline_text会自动识别换行符
    draw.multiline_text(
        (space, space), class_info_table, fill=(255, 255, 255), font=font
    )

    buff = BytesIO()
    im_new.save(buff, "jpeg")
    return buff.getvalue()


def get_photo_bytes(id, student_info):
    return get_photo(get_table(get_data(id, student_info)))
