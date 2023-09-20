from datetime import date

def get_current_date():
    '''Returns the current date'''
    return date.today().strftime('%d-%m-%Y')