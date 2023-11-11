import asyncio
import aiohttp
import re
import pandas as pd
from bs4 import BeautifulSoup
from collections import deque


async def fetch_url(session, url):
    timeout = aiohttp.ClientTimeout(total=10)  # Set a timeout for each request
    async with session.get(url, timeout=timeout) as response:
        return await response.text()


async def fetch_all_urls(session, urls):
    return await asyncio.gather(*(fetch_url(session, url) for url in urls))


async def ligains_async():
    base_url = "https://www.ligainsider.de"
    player_stats = []
    pattern = re.compile(r"(\d+,\d+%?|\d+%?)")  # Compiled regex

    async with aiohttp.ClientSession() as session:
        main_page_content = await fetch_url(session, base_url)
        tree = BeautifulSoup(main_page_content, "lxml")
        vereine = tree.find_all(attrs={"class": "icon_holder"})

        kader_links = [
            base_url + link.get("href")
            for verein in vereine
            for link in verein.find_all("a", string="Kader")
        ]

        kader_pages_content = await fetch_all_urls(session, kader_links)
        all_spieler_links = deque()

        for kader_page_content in kader_pages_content:
            tree = BeautifulSoup(kader_page_content, "lxml")
            alle_spieler = tree.find_all(attrs={"class": "leg_table_main_row"})
            sp_links = [
                base_url + link.get("href")
                for spieler in alle_spieler
                for link in spieler.find_all("a")
            ]
            all_spieler_links.extend(sp_links[::3])

        all_pages_content = await fetch_all_urls(session, all_spieler_links)

        for page_content in all_pages_content:
            tree = BeautifulSoup(page_content, "lxml")

            player_id = 0
            btn_box = tree.find(attrs={"class": "btn_box"})
            if btn_box:
                player_id = int(btn_box["href"].split("?")[0].split("/")[-1])

            stats = tree.find_all(attrs={"class": "progress_info pull-left"})

            d = {}
            for stat in stats:
                key = stat.span.text
                value = stat.strong.text
                match = pattern.search(value)
                if match:
                    d[key] = match.group(1).strip()

            player_stats.append({"ID": player_id, **d})

    return pd.DataFrame(player_stats)


if __name__ == "__main__":
    df = asyncio.run(ligains_async())
    df.to_csv("./data/ligainsider_df.csv", index=False)
