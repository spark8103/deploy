# coding: utf-8
import ConfigParser
from config import Config
import os, json, urllib2

ansible_inventory_file = Config.ANSIBLE_INVENTORY_FILE
deploy_inventory_file = Config.DEPLOY_INVENTORY_FILE

preurl = 'http://10.11.11.22/api/v0.1/ci/s?q='
header = {"Content-Type": "application/json"}


def get_inventory_group():
    """ get inventory group """
    cf = ConfigParser.ConfigParser()
    cf.read(ansible_inventory_file)
    return cf.sections()


def get_inventory_vars(group, var_name):
    """ get group_var values """
    cf = ConfigParser.ConfigParser()
    cf.read(deploy_inventory_file)
    result = ""

    try:
        result = cf.get(group, var_name)
    except:
        result = ""
    return result


def get_inventory_hosts(group):
    """Get inventory hosts"""
    cf = ConfigParser.ConfigParser()
    cf.read(deploy_inventory_file)
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
                result = i.split()[0]
            else:
                result = result + ";" + i.split()[0]
        except:
            return ""
    return result


def get_ansible_inventory_hosts(group):
    """Get inventory hosts"""
    cf = ConfigParser.ConfigParser()
    cf.read(ansible_inventory_file)
    try:
        options = cf.options(group)
    except:
        return ""

    result = []
    if len(options)==0:
        return ""

    for i in options:
        try:
            result.append(i.split()[0])
        except:
            return []
    return result


def get_all_pro():
    """ get cmdb branchs """
    branchs = []
    posturl = 'i_bu:农行,category:营业部,env:生产,~category_branch:(zp-prd-oa;zp-prd-hr;zp-stg-*;' \
              'bd-ucloud-*;zp-prd-windows;zp-prd-esxi;zp-prd-analysis)&facet=category_branch'
    url = str(preurl) + str(posturl)
    request = urllib2.Request(url)
    for key in header:
        request.add_header(key, header[key])
    result = urllib2.urlopen(request)
    response = json.loads(result.read())
    for branch in response['facet']['category_branch']:
        branchs.append(str(branch[0]))
    branchs.sort()
    return branchs


def get_hosts(branch):
    """ get branch hosts """
    hosts = []
    preurl2 = "i_bu:农行,category:营业部"
    posturl = ',category_branch:%s' % branch
    Url = str(preurl) + str(preurl2) + str(posturl)
    request = urllib2.Request(Url)
    for key in header:
        request.add_header(key, header[key])
    result = urllib2.urlopen(request)
    response = json.loads(result.read())
    for host in response['result']:
        hosts.append([str(host['hostname']), str(host['private_ip'][0])])
    hosts.sort()
    return hosts


def update_inventory():
    """ write inventory file """
    branchs = get_all_pro()
    inventory_info = ""

    for branch in branchs:
        inventory_info = inventory_info + "[" + branch + "]\r\n"
        hosts = get_hosts(branch)
        for i in hosts:
            inventory_info = inventory_info + i[0] + " ansible_ssh_host=" + i[1] + "\r\n"
        inventory_info = inventory_info + "\r\n"
    # write file
    with open(ansible_inventory_file, 'w') as outfile:
        outfile.write(inventory_info)
    return True


def get_playbook_list():
    return [ file for file in os.listdir(Config.ANSIBLE_PATH) if os.path.splitext(file)[1] == '.yml']
