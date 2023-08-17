import argparse

from config import constant, variables


def parse():
    parser = argparse.ArgumentParser(f"Movie_Data_Capture Ver. {constant.G_VERSION}")
    parser.add_argument("-c","--conf", dest='conf_file_path', default='', nargs='?', help="config file path")
    parser.add_argument("-s", "--search", dest='search_for_number', default='', nargs='?', help="Search number")
    parser.add_argument("-l", "--list-movie", dest='list_movie', action='store_true', help="print all movie path which will capture.")
    variables.args = vars(parser.parse_args())