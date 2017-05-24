#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage: get inventory hosts

Created by spark8103 2017-05-24
ver: 1.0
Last Modified:
"""
import sys, os, ConfigParser

inventory_file = r"/opt/soft_build/DEPLOY/inventory_dir/project"
if not os.path.exists(inventory_file):
    print "ERROR: not exit " + inventory_file
    sys.exit(127)


def get_inventory_hosts(group):
    """Get inventory hosts"""
    cf = ConfigParser.ConfigParser()
    cf.read(inventory_file)
    try:
        options = cf.options(group)
    except:
        return ""

    result = ""
    if len(options)==0:
        return ""

    for i in options:
        try:
            if len(result) == 0:
                result = i.split()[0] + "@" + cf.get(group, i)
            else:
                result = result + ";" + i.split()[0] + "@" + cf.get(group, i)
        except:
            return ""
    return result

if __name__ == '__main__':
    """
    group = sys.argv[1]
    """
    if len(sys.argv) == 2:
        print get_inventory_hosts(group=(sys.argv[1]))
    else:
        print u"""Error: requires 1 parameters (group)
Usage: get_inventory_hosts.py group
get inventory hosts
Example: get_inventory_hosts.py test-cmdb5
"""
        sys.exit(110)