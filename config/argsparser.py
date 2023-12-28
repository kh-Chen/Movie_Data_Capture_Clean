import argparse

from config import constant, variables


def parse():
    parser = argparse.ArgumentParser(f"Movie_Data_Capture Ver. {constant.G_VERSION}")
    parser.add_argument("-c","--conf", dest='conf_file_path', default='', nargs='?', help="config file path")
    parser.add_argument("-s", "--search", dest='search_for_number', default='', nargs='?', help="Search number")
    parser.add_argument("-f", "--specify-file", dest='specify_file', default='', nargs='?', help="specify file to scraper")
    parser.add_argument("-l", "--list-movie", dest='list_movie', action='store_true', help="print all movie path which will capture.")
    parser.add_argument("-u", "--scraping-url", dest='scraping_url', default='', nargs=2, help="get all movie info from url, write to excel. only support javdb! usage: --scraping-url url file")
    parser.add_argument("--with-cover", dest='with_cover', action='store_true', help="Only effective in scraping-url mode. Simultaneously download the cover image.")
    parser.add_argument("--over-config", dest='over_config', default='', nargs='+', help="over write params to config.ini usage: --over-config commom.enable_debug=0")
    parser.add_argument("--test", dest='test_mode', action='store_true', help="run test mode")
    variables.args = vars(parser.parse_args())
    for diyconf in variables.args["over_config"]:
        try:
            [key, value] = diyconf.split("=")
            variables.args[key.strip()] = value.strip()
        except Exception as e:
            print(e)

