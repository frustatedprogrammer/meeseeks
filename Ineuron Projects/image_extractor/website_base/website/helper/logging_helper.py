import os

'''
create log folder if not exists
'''


def log_folder():
    path = './log/'
    if not os.path.exists(path):
        os.mkdir(path)