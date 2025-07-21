import asyncio
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler   # pip install apscheduler
from astrbot.api.star import Star, register, Context
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api import logger
from astrbot.api.message_components import Plain, Image
from astrbot.api.all import AstrBotConfig

@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context,config: AstrBotConfig):
        super().__init__(context)
        self.context = context
        self.config = config
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        self._schedule_task()
        self.scheduler.start()
        logger.info("[xhs_auto] 每日推送任务已启动")

    # ---------- 定时任务 ----------
    def _schedule_task(self):
        hour, minute = map(int, self.config["push_time"].split(":"))
        self.scheduler.add_job(
            self._daily_push,
            trigger="cron",
            hour=hour,
            minute=minute,
            id="xhs_daily_push",
            replace_existing=True,
        )

    async def _daily_push(self):
        targets = self.config["targets"]
        text = self.config["push_text"]
        img  = self.config["push_image"]
        chain = [Plain(text), Image.fromURL(img)]

        logger.info(f"[xhs_auto] 开始推送，目标 {targets}")
        for umo in targets:
            try:
                await self.context.send_message(umo, chain)
                logger.info(f"[xhs_auto] 已推送至 {umo}")
            except Exception as e:
                logger.exception(f"[xhs_auto] 推送到 {umo} 失败: {e}")
        

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
