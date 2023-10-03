import random as rd
import time
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup


def ligains():
    def li_basic():
        player_ids = []
        player_names = []
        player_values = []
        player_clubs = []
        player_born = []
        player_fitness = []
        player_position = []
        url = "https://www.ligainsider.de"

        page = requests.get(url)

        tree = BeautifulSoup(page.text, features="html5lib")

        vereine = tree.find_all(attrs={"class": "icon_holder"})

        for verein in vereine:
            links = verein.find_all("a", string="Kader")

        kader = []
        for link in links:
            kader.append(url + link.get("href"))

        for i in range(len(kader)):  # len(kader)
            page2 = requests.get(kader[i])
            time.sleep(rd.uniform(1, 3))
            tree2 = BeautifulSoup(page2.text, features="html5lib")

            alle_spieler = tree2.find_all(attrs={"class": "leg_table_main_row"})

            for spieler in alle_spieler:
                sp_links = spieler.find_all("a")

            spieler = []
            for link in sp_links:
                spieler.append(link.get("href"))

            spieler = spieler[::3]

            spieler = [url + link for link in spieler]

            for i in range(len(spieler)):
                thep = requests.get(spieler[i])
                time.sleep(rd.uniform(0, 0.5))
                tree = BeautifulSoup(thep.text, features="html5lib")
                name = tree.find(attrs={"itemprop": "name"}).text
                position = tree.find(string="Position:").parent.parent.small.text
                club = tree.find(attrs={"itemprop": "affiliation"}).text
                born = tree.find(attrs={"itemprop": "birthDate"}).text
                born = born[-4::]
                fitness = tree.find(class_="angeschlagen").img["title"]
                if tree.find(string="Marktwert") == None:
                    value = "-"
                else:
                    value = (
                        tree.find(string="Marktwert").find_parent().find_parent().text
                    )
                    value = value[0 : value.find("€") - 1]
                if tree.find(attrs={"class": "btn_box"}) == None:
                    id = 0
                else:
                    id = int(
                        tree.find(attrs={"class": "btn_box"})["href"]
                        .split("?")[0]
                        .split("/")[-1]
                    )

                player_names.append(name)
                player_values.append(value)
                player_clubs.append(club)
                player_born.append(born)
                player_fitness.append(fitness)
                player_position.append(position)
                player_ids.append(id)

        liplayerdf = pd.DataFrame(
            {
                "ID": player_ids,
                "Name": player_names,
                "Born": player_born,
                "Position": player_position,
                "Value": player_values,
                "Squad": player_clubs,
                "Zustand": player_fitness,
            }
        )

        return liplayerdf

    def li_points():
        url = "https://www.ligainsider.de/stats/kickbase/rangliste/feldspieler/gesamt/66929/"

        page = requests.get(url)

        tree = BeautifulSoup(page.text)

        table = tree.select_one("#DataTable")

        header_pkt = table.find("thead")
        header_txt_pkt = header_pkt.text

        header_txt_pkt = header_txt_pkt.replace("\n", " ")
        header_txt_pkt = header_txt_pkt.replace("  ", " ")
        header_txt_pkt = re.sub(r"^\s+|\s+$", "", header_txt_pkt)
        header_txt_pkt = header_txt_pkt.split()

        tabelle_pkt = table.find("tbody")

        tabelle_inhalt = tabelle_pkt.find_all(
            lambda tag: tag.has_attr("class") and tag.name == "td"
        )

        tabellebody = []

        for i in tabelle_inhalt:
            tabellebody.append(i.text.strip())

        name = tabellebody[::8]
        squad = tabellebody[1::8]
        position = tabellebody[2::8]
        points_md = tabellebody[3::8]
        value = tabellebody[4::8]
        value = [x[:-1] for x in value]
        appearances = tabellebody[5::8]
        avg_points = tabellebody[6::8]
        total_points = tabellebody[7::8]
        df_points = pd.DataFrame(
            {
                "Name": name,
                "Value": value,
                "Squad": squad,
                "Position": position,
                "Einsätze": appearances,
                "Spieltagspunkte": points_md,
                "Punkteschnitt": avg_points,
                "Punktetotal": total_points,
            }
        )

        url = "https://www.ligainsider.de/stats/kickbase/rangliste/torhueter/gesamt/66929/"

        page = requests.get(url)

        tree = BeautifulSoup(page.text)

        table = tree.select_one("#DataTable")

        header_pkt = table.find("thead")
        header_txt_pkt = header_pkt.text

        header_txt_pkt = header_txt_pkt.replace("\n", " ")
        header_txt_pkt = header_txt_pkt.replace("  ", " ")
        header_txt_pkt = re.sub(r"^\s+|\s+$", "", header_txt_pkt)
        header_txt_pkt = header_txt_pkt.split()

        tabelle_pkt = table.find("tbody")

        tabelle_inhalt = tabelle_pkt.find_all(
            lambda tag: tag.has_attr("class") and tag.name == "td"
        )

        tabellebody = []

        for i in tabelle_inhalt:
            tabellebody.append(i.text.strip())

        name = tabellebody[::8]
        squad = tabellebody[1::8]
        position = tabellebody[2::8]
        points_md = tabellebody[3::8]
        value = tabellebody[4::8]
        value = [x[:-1] for x in value]
        appearances = tabellebody[5::8]
        avg_points = tabellebody[6::8]
        total_points = tabellebody[7::8]

        df_points_gk = pd.DataFrame(
            {
                "Name": name,
                "Value": value,
                "Squad": squad,
                "Position": position,
                "Einsätze": appearances,
                "Spieltagspunkte": points_md,
                "Punkteschnitt": avg_points,
                "Punktetotal": total_points,
            }
        )
        df_points = pd.concat([df_points, df_points_gk], axis=0)
        return df_points

    a = li_basic()
    b = li_points()

    playerdf = a.merge(b, how="left", on=["Name", "Squad", "Position"])

    df = playerdf.loc[:, ~playerdf.columns.str.endswith("_y")]
    df.columns = df.columns.str.removesuffix("_x")
    df.fillna(0, inplace=True)
    df.head()

    df.to_csv("./data/li_pd.csv", index=False)
