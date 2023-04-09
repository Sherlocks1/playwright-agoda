# -*- coding = utf-8 -*-
# @Time : 2023/4/3 0:14
# @Author : Sherlock
# @File : tools.py
# @Software : PyCharm
import os
import random
import re
import asyncio
from settings import MIN_TIME, MAX_TIME


def clean_date(url: str) -> str:
    match = re.search(r'checkIn=(\d{4}-\d{2}-\d{1,2})', url)
    if match:
        date = match.group(1)
    else:
        date = "unknown"
    return date


async def random_wait(min_time=MIN_TIME, max_time=MAX_TIME):
    seconds = random.uniform(min_time, max_time)
    # logging.info(f"{task_name}{filename}随机等待 {seconds:.2f} 秒")
    await asyncio.sleep(seconds)
