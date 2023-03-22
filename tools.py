import os
import random
import re
import asyncio


def clean_filename(url: str) -> str:
    match = re.search(r'checkIn=(\d{4}-\d{2}-\d{1,2})', url)
    if match:
        filename = match.group(1) + ".html"
    else:
        filename = "unknown.html"
    return filename


async def random_wait(min_time=1.0, max_time=3.0):
    seconds = random.uniform(min_time, max_time)
    # logging.info(f"{task_name}{filename}随机等待 {seconds:.2f} 秒")
    await asyncio.sleep(seconds)


def delete_html_files():
    for filename in os.listdir("."):
        if filename.endswith(".html"):
            os.remove(filename)
