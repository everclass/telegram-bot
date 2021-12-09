import nonebot
from nonebot.adapters.telegram import Bot as TelegramBot

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter("telegram", TelegramBot)

nonebot.load_plugin("csu_class")
