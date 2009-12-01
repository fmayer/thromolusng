import os

DATADIR = os.path.join(os.path.dirname(__file__), os.pardir, 'data')

def get_data(data):
    return os.path.abspath(os.path.join(DATADIR, data))