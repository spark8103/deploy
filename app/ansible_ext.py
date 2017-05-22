import ConfigParser
from config import Config

inventory_file = Config.ANSIBLE_INVENTORY_FILE


def get_inventory_group():
    ''' get inventory group '''
    cf = ConfigParser.ConfigParser()
    cf.read(inventory_file)
    return cf.sections()