#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage: get ansible vars

Created by spark8103 2017-02-27
ver: 1.0
Last Modified:
"""
import sys, os, ConfigParser

inventory_file = r"/opt/soft_build/DEPLOY/inventory_dir/project"
if not os.path.exists(inventory_file):
    print "ERROR: not exit " + inventory_file
    sys.exit(127)


def get_inventory_vars(group, var_name):
    """add field and key and values"""
    cf = ConfigParser.ConfigParser()
    cf.read(inventory_file)
    result = ""

    try:
        result = cf.get(group, var_name)
    except:
        result = ""
    return result

if __name__ == '__main__':
    """
    group = sys.argv[1]
    var_name = sys.argv[2]
    """
    if len(sys.argv) == 3:
        print get_inventory_vars(group=(sys.argv[1] + ":vars"), var_name=sys.argv[2])
    else:
        print u"""Error: requires 2 parameters (group, var_name)
Usage: get_inventory_var.py group var_name
get ansible vars
Example: get_inventory_var.py test-cmdb5 app_type
"""
        sys.exit(110)