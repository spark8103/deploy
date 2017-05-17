import svn.remote
from config import Config

svn_username = Config.SVN_USER
svn_password = Config.SVN_PASSWORD

# r = svn.remote.RemoteClient('http://10.205.59.16/svn/java_code/xxxx/tags/', username='xxxxx', password='xxxxxx')


def svn_tag_list(url, job_name, username=svn_username, password=svn_password):
    svn_remote = svn.remote.RemoteClient(url, username=username, password=password)
    tag_list = [i for i in svn_remote.list() if not i.find(job_name)]
    return sorted(tag_list, reverse=True)