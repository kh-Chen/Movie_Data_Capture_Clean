import argparse

from config import constant, variables


def parse():
    parser = argparse.ArgumentParser(f"Movie_Data_Capture Ver. {constant.G_VERSION}")
    parser.add_argument("-c","--conf", dest='conf_file_path', default='', nargs='?', help="config file path")
    parser.add_argument("-s", "--search", dest='search_for_number', default='', nargs='?', help="Search number")
    parser.add_argument("-l", "--list-movie", dest='list_movie', action='store_true', help="print all movie path which will capture.")
    parser.add_argument("-u", "--scraping-url", dest='scraping_url', default='', nargs=2, help="get all movie info from url, write to excel. only support javdb! usage: --scraping-url url file")
    parser.add_argument("--over-config", dest='over_config', default='', nargs='+', help="over write params to config.ini usage: --over-config commom.enable_debug=0")
    variables.args = vars(parser.parse_args())
    for diyconf in variables.args["over_config"]:
        try:
            [key, value] = diyconf.split("=")
            variables.args[key.strip()] = value.strip()
        except Exception as e:
            print(e)

