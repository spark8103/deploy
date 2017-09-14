# coding: utf-8
import gitlab
from config import Config

gitlab_server = Config.GITLAB_SERVER
gitlab_token = Config.GITLAB_TOKEN


def gitlab_tag_list(url, server=gitlab_server, token=gitlab_token):
    gl = gitlab.Gitlab(server, token, api_version=4)
    gl.auth()
    projects = gl.projects.list(per_page=1000)

    git_url = url.replace("root@gitlab.bdeastmoney.com","zp-prd-ops-13")
    for i in projects:
        if i.http_url_to_repo == git_url:
            project = i

    tags = project.tags.list()
    tag_list = [ i.name for i in tags]
    return sorted(tag_list, reverse=True)