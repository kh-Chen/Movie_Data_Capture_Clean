import os,sys

def blockprint(func):
    def wrapper(*args, **kwargs):
        sys.stdout = open(os.devnull, 'w')
        results = func(*args, **kwargs)
        sys.stdout = sys.__stdout__
        return results
    return wrapper