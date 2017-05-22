# coding: utf-8
import jenkins, time
from config import Config
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

jenkins_url = Config.JENKINS_URL
jenkins_username = Config.JENKINS_USER
jenkins_password = Config.JENKINS_TOKEN


def jobs_list_get():
    server = jenkins.Jenkins(jenkins_url, username=jenkins_username, password=jenkins_password)
    jobs = server.get_all_jobs()
    return [ i['fullname'] for i in jobs if(i['fullname'].find('bd-')==0)]


def job_build(job_name):
    server = jenkins.Jenkins(jenkins_url, username=jenkins_username, password=jenkins_password)
    next_bn = server.get_job_info(job_name)['nextBuildNumber']
    server.build_job(job_name)

    while 1:
        if server.get_job_info(job_name)['lastBuild']['number'] == next_bn and \
                not server.get_build_info(job_name, next_bn)['building']:
            break
        else:
            time.sleep(5)
    build_info = server.get_build_info(job_name, next_bn)
    return build_info


def job_get_number(job_name):
    server = jenkins.Jenkins(jenkins_url, username=jenkins_username, password=jenkins_password)
    job_info = server.get_job_info(job_name)
    last_number = job_info['lastCompletedBuild']['number']
    return range((last_number - 4), (last_number + 1))[::-1]


def job_get_svn(job_name):
    server = jenkins.Jenkins(jenkins_url, username=jenkins_username, password=jenkins_password)
    job_config = server.get_job_config(job_name)
    root = ET.fromstring(job_config.encode('utf8'))
    svn_url = root.find('scm/locations/hudson.scm.SubversionSCM_-ModuleLocation/remote')
    if ET.iselement(svn_url):
        svn_url = svn_url.text
    tag_dir = root.find('properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/' +
                        'hudson.scm.listtagsparameter.ListSubversionTagsParameterDefinition/tagsDir')
    if ET.iselement(tag_dir):
        tag_dir = tag_dir.text
    tags_filter = root.find('properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/' +
                        'hudson.scm.listtagsparameter.ListSubversionTagsParameterDefinition/tagsFilter')
    if ET.iselement(tags_filter):
        tags_filter = tags_filter.text
    return {'svn_url':svn_url, 'tag_dir': tag_dir, 'tags_filter': tags_filter}

# from app.jenkins_ext import jobs_list_get, job_build

# bd-blink-server
# server = jenkins.Jenkins(jenkins_url, username=jenkins_username, password=jenkins_password)
# user = server.get_whoami()
# version = server.get_version()

# last_build_number = server.get_job_info(job_name)['lastBuild']['number']
# last_completed_build_number = server.get_job_info(job_name)['lastCompletedBuild']['number']
# build_info = server.get_build_info(job_name, last_build_number)

