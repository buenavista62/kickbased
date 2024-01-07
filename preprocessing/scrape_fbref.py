import html
import random as rd
import re
import time

import html5lib
import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def fbref(season):
    def requests_retry_session(
        retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)
    ):
        session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def StandardPlayerStats():
        url = f"https://fbref.com/en/comps/20/{season}/stats/{season}-Bundesliga-Stats"
        session = requests_retry_session()
        page = session.get(url)

        if page.status_code != 200:
            print(f"Failed to retrieve data: Status code {page.status_code}")
            return None

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

        # df_fbref.to_csv(f"./data/{season}fbref_pd.csv", index=False)
        return df_fbref

    def AdvancedGKStats():
        url = f"https://fbref.com/en/comps/20/{season}/keepersadv/{season}-Bundesliga-Stats"
        session = requests_retry_session()
        page = session.get(url)

        if page.status_code != 200:
            print(f"Failed to retrieve data: Status code {page.status_code}")
            return None

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

        # df_fbref_advgk.to_csv(f"./data/{season}fbref_advgk.csv", index=False)
        return df_fbref_advgk

    def ShootingStats():
        url = (
            f"https://fbref.com/en/comps/20/{season}/shooting/{season}-Bundesliga-Stats"
        )
        session = requests_retry_session()
        page = session.get(url)

        if page.status_code != 200:
            print(f"Failed to retrieve data: Status code {page.status_code}")
            return None

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

        # df_fbref_shooting.to_csv(f"./data/{season}fbref_shooting.csv", index=False)
        return df_fbref_shooting

    def PassingStats():
        url = (
            f"https://fbref.com/en/comps/20/{season}/passing/{season}-Bundesliga-Stats"
        )
        session = requests_retry_session()
        page = session.get(url)

        if page.status_code != 200:
            print(f"Failed to retrieve data: Status code {page.status_code}")
            return None

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

        # df_fbref_passing.to_csv(f"./data/{season}fbref_passing.csv", index=False)
        return df_fbref_passing

    def GCAStats():
        url = f"https://fbref.com/en/comps/20/{season}/gca/{season}-Bundesliga-Stats"
        session = requests_retry_session()
        page = session.get(url)

        if page.status_code != 200:
            print(f"Failed to retrieve data: Status code {page.status_code}")
            return None

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

        # df_fbref_gca.to_csv(f"./data/{season}fbref_gca.csv", index=False)
        return df_fbref_gca

    def DefensiveStats():
        url = (
            f"https://fbref.com/en/comps/20/{season}/defense/{season}-Bundesliga-Stats"
        )
        session = requests_retry_session()
        page = session.get(url)

        if page.status_code != 200:
            print(f"Failed to retrieve data: Status code {page.status_code}")
            return None

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

        # df_fbref_defense.to_csv(f"./data/{season}fbref_defensive.csv", index=False)
        return df_fbref_defense

    def PossessionStats():
        url = f"https://fbref.com/en/comps/20/{season}/possession/{season}-Bundesliga-Stats"
        session = requests_retry_session()
        page = session.get(url)

        if page.status_code != 200:
            print(f"Failed to retrieve data: Status code {page.status_code}")
            return None

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

        # df_fbref_possession.to_csv(f"./data/{season}fbref_possession.csv", index=False)
        return df_fbref_possession

    def ScrapeFbref():
        df_fbref = StandardPlayerStats()
        df_fbref_advgk = AdvancedGKStats()
        df_fbref_shooting = ShootingStats()
        df_fbref_passing = PassingStats()
        df_fbref_gca = GCAStats()
        df_fbref_defensive = DefensiveStats()
        df_fbref_possession = PossessionStats()

        df = df_fbref.merge(
            df_fbref_advgk, how="left", on=["player", "birth_year", "team"]
        )
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")

        df = df.merge(
            df_fbref_shooting, how="left", on=["player", "birth_year", "team"]
        )
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")

        df = df.merge(df_fbref_passing, how="left", on=["player", "birth_year", "team"])
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")

        df = df.merge(df_fbref_gca, how="left", on=["player", "birth_year", "team"])
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")

        df = df.merge(
            df_fbref_defensive, how="left", on=["player", "birth_year", "team"]
        )
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")

        df = df.merge(
            df_fbref_possession, how="left", on=["player", "birth_year", "team"]
        )
        df = df.loc[:, ~df.columns.str.endswith("_y")]
        df.columns = df.columns.str.removesuffix("_x")
        df.to_csv(f"./data/{season}fbref_full.csv", index=False)
        # return df

    ScrapeFbref()


if __name__ == "__main__":
    for i in range(2023, 2024):
        season = str(i) + "-" + str(i + 1)
        fbref(season)
