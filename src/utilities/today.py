from datetime import date

from src.utilities.foo import print_info

print_info()

def get_current_date():
    '''Returns the current date'''
    return date.today().strftime('%d-%m-%Y')

