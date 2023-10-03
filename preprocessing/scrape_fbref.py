import html
import random as rd
import re
import time

import html5lib
import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment


def fbref():
    def StandardPlayerStats():
        url = "https://fbref.com/en/comps/20/stats/Bundesliga-Stats"
        page = requests.get(url)

        tree = BeautifulSoup(page.text, "html.parser")

        tabelle = tree.find(class_="table_wrapper", id="all_stats_standard")

        comments = tabelle.find_all(string=lambda text: isinstance(text, Comment))

        for comment in comments:
            comment_content = BeautifulSoup(comment, "html.parser").prettify()
            unescaped_content = html.unescape(comment_content)
            new_tag = BeautifulSoup(unescaped_content, "html.parser")
            comment.replace_with(new_tag)

        elements = tabelle.find_all(attrs={"data-stat": True})

        header = [element["data-stat"] for element in elements]
        header = header[header.index("player") : header.index("matches") + 1]

        body = tabelle.find("tbody")

        body_data = []

        for i in body:
            body_data = body.find_all("td")

        body_col = []

        for i in body_data:
            body_col.append(i.text)

        cleaned_col = [i.strip() for i in body_col]
        cleaned_col = [i.replace("\n", "") for i in cleaned_col]
        cleaned_col = [i.replace("       ", " ") for i in cleaned_col]
        cleaned_col = [i.replace("  ", " ") for i in cleaned_col]
        data_dict = {}
        for i in header:
            data_dict[str(i)] = cleaned_col[header.index(i) :: len(header)]

        df_fbref = pd.DataFrame(data_dict)

        df_fbref.to_csv("./data/fbref_pd.csv", index=False)
        return df_fbref

    def AdvancedGKStats():
        url = "https://fbref.com/en/comps/20/keepersadv/Bundesliga-Stats"
        page = requests.get(url)

        tree = BeautifulSoup(page.text, "html.parser")

        tabelle = tree.select_one("#all_stats_keeper_adv")
        comments = tabelle.find_all(string=lambda text: isinstance(text, Comment))

        for comment in comments:
            comment_content = BeautifulSoup(comment, "html.parser").prettify()
            unescaped_content = html.unescape(comment_content)
            new_tag = BeautifulSoup(unescaped_content, "html.parser")
            comment.replace_with(new_tag)

        elements = tabelle.find_all(attrs={"data-stat": True})

        header = [element["data-stat"] for element in elements]
        header = header[header.index("player") : header.index("matches") + 1]

        body = tabelle.find("tbody")

        body_data = []

        for i in body:
            body_data = body.find_all("td")

        body_col = []

        for i in body_data:
            body_col.append(i.text)

        cleaned_col = [i.strip() for i in body_col]
        cleaned_col = [i.replace("\n", "") for i in cleaned_col]
        cleaned_col = [i.replace("       ", " ") for i in cleaned_col]
        cleaned_col = [i.replace("  ", " ") for i in cleaned_col]
        data_dict = {}
        for i in header:
            data_dict[str(i)] = cleaned_col[header.index(i) :: len(header)]

        df_fbref_advgk = pd.DataFrame(data_dict)

        """
        for i in range(len(data_dict["Name"])):
            createID(data_dict["Name"][i], data_dict["Squad"][i], player_id_fbref)
        """

        df_fbref_advgk.to_csv("./data/fbref_advgk.csv", index=False)
        return df_fbref_advgk

    def ShootingStats():
        url = "https://fbref.com/en/comps/20/shooting/Bundesliga-Stats"
        page = requests.get(url)

        tree = BeautifulSoup(page.text, "html.parser")

        tabelle = tree.select_one("#all_stats_shooting")
        comments = tabelle.find_all(string=lambda text: isinstance(text, Comment))

        for comment in comments:
            comment_content = BeautifulSoup(comment, "html.parser").prettify()
            unescaped_content = html.unescape(comment_content)
            new_tag = BeautifulSoup(unescaped_content, "html.parser")
            comment.replace_with(new_tag)

        elements = tabelle.find_all(attrs={"data-stat": True})

        header = [element["data-stat"] for element in elements]
        header = header[header.index("player") : header.index("matches") + 1]

        body = tabelle.find("tbody")

        body.find("tr")
        body_data = []

        for i in body:
            body_data = body.find_all("td")

        body_col = []

        for i in body_data:
            body_col.append(i.text)
        """ for i in body_data:
            try:
                if body_data.index(i) % 36 == 0:
                    body_col.append(i.find("a").text)
                else:
                    body_col.append(i.find("td").text)
            except:
                break
        """

        cleaned_col = [i.strip() for i in body_col]
        cleaned_col = [i.replace("\n", "") for i in cleaned_col]
        cleaned_col = [i.replace("       ", " ") for i in cleaned_col]
        cleaned_col = [i.replace("  ", " ") for i in cleaned_col]
        data_dict = {}
        for i in header:
            data_dict[str(i)] = cleaned_col[header.index(i) :: len(header)]

        df_fbref_shooting = pd.DataFrame(data_dict)

        """
        for i in range(len(data_dict["Name"])):
            createID(data_dict["Name"][i], data_dict["Squad"][i], player_id_fbref)
        """

        df_fbref_shooting.to_csv("./data/fbref_shooting.csv", index=False)
        return df_fbref_shooting

    def PassingStats():
        url = "https://fbref.com/en/comps/20/passing/Bundesliga-Stats"
        page = requests.get(url)

        tree = BeautifulSoup(page.text, "html.parser")

        tabelle = tree.select_one("#all_stats_passing")
        comments = tabelle.find_all(string=lambda text: isinstance(text, Comment))

        for comment in comments:
            comment_content = BeautifulSoup(comment, "html.parser").prettify()
            unescaped_content = html.unescape(comment_content)
            new_tag = BeautifulSoup(unescaped_content, "html.parser")
            comment.replace_with(new_tag)

        elements = tabelle.find_all(attrs={"data-stat": True})

        header = [element["data-stat"] for element in elements]
        header = header[header.index("player") : header.index("matches") + 1]

        body = tabelle.find("tbody")

        body.find("tr")
        body_data = []

        for i in body:
            body_data = body.find_all("td")

        body_col = []

        for i in body_data:
            body_col.append(i.text)
        """ for i in body_data:
            try:
                if body_data.index(i) % 36 == 0:
                    body_col.append(i.find("a").text)
                else:
                    body_col.append(i.find("td").text)
            except:
                break
        """

        cleaned_col = [i.strip() for i in body_col]
        cleaned_col = [i.replace("\n", "") for i in cleaned_col]
        cleaned_col = [i.replace("       ", " ") for i in cleaned_col]
        cleaned_col = [i.replace("  ", " ") for i in cleaned_col]
        data_dict = {}
        for i in header:
            data_dict[str(i)] = cleaned_col[header.index(i) :: len(header)]

        df_fbref_passing = pd.DataFrame(data_dict)

        """
        for i in range(len(data_dict["Name"])):
            createID(data_dict["Name"][i], data_dict["Squad"][i], player_id_fbref)
        """

        df_fbref_passing.to_csv("./data/fbref_passing.csv", index=False)
        return df_fbref_passing

    def GCAStats():
        url = "https://fbref.com/en/comps/20/gca/Bundesliga-Stats"
        page = requests.get(url)

        tree = BeautifulSoup(page.text, "html.parser")

        tabelle = tree.select_one("#all_stats_gca")
        comments = tabelle.find_all(string=lambda text: isinstance(text, Comment))

        for comment in comments:
            comment_content = BeautifulSoup(comment, "html.parser").prettify()
            unescaped_content = html.unescape(comment_content)
            new_tag = BeautifulSoup(unescaped_content, "html.parser")
            comment.replace_with(new_tag)

        elements = tabelle.find_all(attrs={"data-stat": True})

        header = [element["data-stat"] for element in elements]
        header = header[header.index("player") : header.index("matches") + 1]

        body = tabelle.find("tbody")

        body.find("tr")
        body_data = []

        for i in body:
            body_data = body.find_all("td")

        body_col = []

        for i in body_data:
            body_col.append(i.text)
        """ for i in body_data:
            try:
                if body_data.index(i) % 36 == 0:
                    body_col.append(i.find("a").text)
                else:
                    body_col.append(i.find("td").text)
            except:
                break
        """

        cleaned_col = [i.strip() for i in body_col]
        cleaned_col = [i.replace("\n", "") for i in cleaned_col]
        cleaned_col = [i.replace("       ", " ") for i in cleaned_col]
        cleaned_col = [i.replace("  ", " ") for i in cleaned_col]
        data_dict = {}
        for i in header:
            data_dict[str(i)] = cleaned_col[header.index(i) :: len(header)]

        df_fbref_gca = pd.DataFrame(data_dict)

        """
        for i in range(len(data_dict["Name"])):
            createID(data_dict["Name"][i], data_dict["Squad"][i], player_id_fbref)
        """

        df_fbref_gca.to_csv("./data/fbref_gca.csv", index=False)
        return df_fbref_gca

    def DefensiveStats():
        url = "https://fbref.com/en/comps/20/defense/Bundesliga-Stats"
        page = requests.get(url)

        tree = BeautifulSoup(page.text, "html.parser")

        tabelle = tree.select_one("#all_stats_defense")
        comments = tabelle.find_all(string=lambda text: isinstance(text, Comment))

        for comment in comments:
            comment_content = BeautifulSoup(comment, "html.parser").prettify()
            unescaped_content = html.unescape(comment_content)
            new_tag = BeautifulSoup(unescaped_content, "html.parser")
            comment.replace_with(new_tag)

        elements = tabelle.find_all(attrs={"data-stat": True})

        header = [element["data-stat"] for element in elements]
        header = header[header.index("player") : header.index("matches") + 1]

        body = tabelle.find("tbody")

        body.find("tr")
        body_data = []

        for i in body:
            body_data = body.find_all("td")

        body_col = []

        for i in body_data:
            body_col.append(i.text)

        cleaned_col = [i.strip() for i in body_col]
        cleaned_col = [i.replace("\n", "") for i in cleaned_col]
        cleaned_col = [i.replace("       ", " ") for i in cleaned_col]
        cleaned_col = [i.replace("  ", " ") for i in cleaned_col]
        data_dict = {}
        for i in header:
            data_dict[str(i)] = cleaned_col[header.index(i) :: len(header)]

        df_fbref_defense = pd.DataFrame(data_dict)

        """
        for i in range(len(data_dict["Name"])):
            createID(data_dict["Name"][i], data_dict["Squad"][i], player_id_fbref)
        """

        df_fbref_defense.to_csv("./data/fbref_defensive.csv", index=False)
        return df_fbref_defense

    def PossessionStats():
        url = "https://fbref.com/en/comps/20/possession/Bundesliga-Stats"
        page = requests.get(url)

        tree = BeautifulSoup(page.text, "html.parser")

        tabelle = tree.select_one("#all_stats_possession")
        comments = tabelle.find_all(string=lambda text: isinstance(text, Comment))

        for comment in comments:
            comment_content = BeautifulSoup(comment, "html.parser").prettify()
            unescaped_content = html.unescape(comment_content)
            new_tag = BeautifulSoup(unescaped_content, "html.parser")
            comment.replace_with(new_tag)

        elements = tabelle.find_all(attrs={"data-stat": True})

        header = [element["data-stat"] for element in elements]
        header = header[header.index("player") : header.index("matches") + 1]

        body = tabelle.find("tbody")

        body_data = []

        for i in body:
            body_data = body.find_all("td")

        body_col = []

        for i in body_data:
            body_col.append(i.text)
        """ for i in body_data:
            try:
                if body_data.index(i) % 36 == 0:
                    body_col.append(i.find("a").text)
                else:
                    body_col.append(i.find("td").text)
            except:
                break
        """

        cleaned_col = [i.strip() for i in body_col]
        cleaned_col = [i.replace("\n", "") for i in cleaned_col]
        cleaned_col = [i.replace("       ", " ") for i in cleaned_col]
        cleaned_col = [i.replace("  ", " ") for i in cleaned_col]
        data_dict = {}
        for i in header:
            data_dict[str(i)] = cleaned_col[header.index(i) :: len(header)]

        df_fbref_possession = pd.DataFrame(data_dict)

        """
        for i in range(len(data_dict["Name"])):
            createID(data_dict["Name"][i], data_dict["Squad"][i], player_id_fbref)
        """

        df_fbref_possession.to_csv("./data/fbref_possession.csv", index=False)
        return df_fbref_possession

    def ScrapeFbref():
        df_fbref = StandardPlayerStats()
        df_fbref_advgk = AdvancedGKStats()
        df_fbref_shooting = ShootingStats()
        df_fbref_passing = PassingStats()
        df_fbref_gca = GCAStats()
        df_fbref_defensive = DefensiveStats()
        df_fbref_possession = PossessionStats()

        df = df_fbref.merge(df_fbref_advgk, how="left", on=["player", "birth_year"])
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")

        df = df.merge(df_fbref_shooting, how="left", on=["player", "birth_year"])
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")

        df = df.merge(df_fbref_passing, how="left", on=["player", "birth_year"])
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")

        df = df.merge(df_fbref_gca, how="left", on=["player", "birth_year"])
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")

        df = df.merge(df_fbref_defensive, how="left", on=["player", "birth_year"])
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")

        df = df.merge(df_fbref_possession, how="left", on=["player", "birth_year"])
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")
        df.to_csv("./data/fbref_full.csv", index=False)
        # return df

    ScrapeFbref()
