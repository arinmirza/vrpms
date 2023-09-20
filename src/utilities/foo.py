import os

def print_info():
    return {
                'cwd': os.getcwd(),
                'cwd_content': os.listdir(os.getcwd()),
                'parent': os.path.dirname(os.getcwd()),
                'parent_content': os.listdir(os.path.dirname(os.getcwd())),
            }