from unidecode import unidecode


def SearchPlayer(df, search):
    return df.loc[
        (
            df["Name"]
            .apply(lambda x: unidecode(x))
            .str.contains(unidecode(str(search)), case=False)
        )
        | (df["Name"].str.contains(str(search), case=False))
    ]


def mergeKB(df_full, df_kb):
    df_kb.drop(
        ["ID", "Position", "Status", "Punkteschnitt", "Trend", "Bild"],
        axis=1,
        inplace=True,
    )
    df_kb["Name_uni"] = df_kb["Name"].apply(lambda x: unidecode(x))
    df_full["Marktwert"] = df_full["Value"].str.replace(".", "")
    df_full["Marktwert"] = df_full["Marktwert"].astype("float64")
    df_full["Name_uni"] = df_full["Name"].apply(lambda x: unidecode(x))
    df = df_full.merge(df_kb, how="inner", on=["Name_uni", "Marktwert"])
    df = df.loc[:, ~df.columns.str.endswith("_y")]
    df.columns = df.columns.str.removesuffix("_x")
    df.drop(["Name_uni", "Marktwert"], axis=1, inplace=True)

    return df
