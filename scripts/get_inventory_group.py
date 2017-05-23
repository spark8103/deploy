#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage: get inventory group

Created by spark 2017-05-22
ver: 1.0
Last Modified:
"""
import sys, os, ConfigParser

inventory_file = r"/opt/app/applications/bd-deploy/scripts/inventory_prod"
if not os.path.exists(inventory_file):
    print "ERROR: not exit " + inventory_file
    sys.exit(127)


def get_inventory_group():
    """get inventory group"""
    cf = ConfigParser.ConfigParser()
    cf.read(inventory_file)

    try:
        result = ','.join(cf.sections())
    except:
        result = ""
    return result

if __name__ == '__main__':
    print get_inventory_group()