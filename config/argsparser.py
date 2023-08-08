import argparse

import config.variables as variables


def parse():
    parser = argparse.ArgumentParser(f"Movie_Data_Capture Ver. {variables.G_VERSION}")
    parser.add_argument("-c","--conf", dest='conf_file_path', default='', nargs='?', help="config file path")
    parser.add_argument("-s", "--search", dest='search_for_number', default='', nargs='?', help="Search number")
    variables.args = vars(parser.parse_args())