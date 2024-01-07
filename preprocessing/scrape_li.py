import asyncio
import aiohttp
import re
import pandas as pd
from bs4 import BeautifulSoup


async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()


async def ligains_async():
    player_ids = []
    player_name = []
    player_teams = []
    player_born = []
    player_stats = []
    player_playeratio = []
    base_url = "https://www.ligainsider.de"

    async with aiohttp.ClientSession() as session:
        main_page_content = await fetch_url(session, base_url)
        tree = BeautifulSoup(main_page_content, features="html5lib")
        vereine = tree.find_all(attrs={"class": "icon_holder"})

        kader_links = [
            base_url + link.get("href")
            for verein in vereine
            for link in verein.find_all("a", string="Kader")
        ]
        all_spieler_links = []

        for kader_link in kader_links:
            kader_page_content = await fetch_url(session, kader_link)
            tree2 = BeautifulSoup(kader_page_content, features="html5lib")
            alle_spieler = tree2.find_all(attrs={"class": "leg_table_main_row"})
            sp_links = [
                link.get("href")
                for spieler in alle_spieler
                for link in spieler.find_all("a")
            ]
            all_spieler_links.extend(sp_links[::3])

        all_spieler_links = [base_url + link for link in all_spieler_links]

        tasks = [fetch_url(session, spieler_link) for spieler_link in all_spieler_links]
        all_pages_content = await asyncio.gather(*tasks)

        for page_content in all_pages_content:
            tree = BeautifulSoup(page_content, features="html5lib")

            if tree.find(attrs={"class": "btn_box"}) == None:
                player_id = 0
            else:
                player_id = int(
                    tree.find(attrs={"class": "btn_box"})["href"]
                    .split("?")[0]
                    .split("/")[-1]
                )
            stats = tree.find_all(attrs={"class": "progress_info pull-left"})

            d = {}
            for stat in stats:
                d[stat.span.text] = stat.strong.text
            pattern = re.compile(r"(\d+,\d+%?|\d+%?)")
            for key, value in d.items():
                match = pattern.search(value)
                if match:
                    d[key] = match.group(1).strip()

            einsatzquote = tree.find(attrs={"class": "progress_signal pull-right"}).text
            pattern2 = re.search(r"(\d+)%", einsatzquote)
            einsatzquote = pattern2.group(1)
            name = tree.find(attrs={"itemprop": "name"}).text
            born = tree.find(attrs={"itemprop": "birthDate"}).text
            born = born[-4::]
            player_team = tree.find(attrs={"itemprop": "affiliation"}).text
            player_name.append(name)
            player_born.append(born)
            player_stats.append(d)
            player_ids.append(player_id)
            player_teams.append(player_team)
            player_playeratio.append(int(einsatzquote))

    liplayerdf = pd.DataFrame(
        {
            "ID": player_ids,
            "Name": player_name,
            "Team": player_teams,
            "birth_year": player_born,
            "Stats": player_stats,
            "Einsatzquote": player_playeratio,
        }
    )

    return liplayerdf


if __name__ == "__main__":
    # To run the async function
    df = asyncio.run(ligains_async())
    df.to_csv("./data/ligainsider_df.csv", index=False)
