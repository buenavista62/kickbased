from preprocessing import merge, scrape_fbref, scrape_li


def preprocess():
    scrape_fbref.fbref()
    scrape_li.ligains()
    merge.merge()
    # radarcharts.radarcharts()
    print("ok")


preprocess()
