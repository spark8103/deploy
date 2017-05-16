import svn.remote
from config import Config

svn_url = Config.SVN_URL
svn_username = Config.SVN_USER
svn_password = Config.SVN_PASSWORD

# r = svn.remote.RemoteClient('http://10.205.59.16/svn/java_code/xxxx/tags/', username='xxxxx', password='xxxxxx')


def tag_list_get(url, username, password):
    svn_remote = svn.remote.RemoteClient((url + 'tags'), username=username, password=password)
    return [i[:-1] for i in svn_remote.list()]