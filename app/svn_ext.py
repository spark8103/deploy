# coding: utf-8
import svn.remote
from config import Config

svn_username = Config.SVN_USER
svn_password = Config.SVN_PASSWORD


def svn_tag_list(url, tags_filter, username=svn_username, password=svn_password):
    svn_remote = svn.remote.RemoteClient(url, username=username, password=password)
    if tags_filter:
        tags_filter = tags_filter.replace('.*', '')
        #tag_list = [i.replace('/', '') for i in svn_remote.list() if((not i.find(tags_filter)) or (i.find('subversionservers')))]
        tag_list = [i.replace('/', '') for i in svn_remote.list() if not i.find(tags_filter)]
    else:
        #tag_list = [i.replace('/', '') for i in svn_remote.list() if not i.find('bd-')]
        tag_list = [i.replace('/', '') for i in svn_remote.list() if i.find('warning:') <= 0]
    return sorted(tag_list, reverse=True)