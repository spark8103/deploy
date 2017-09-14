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
    return [ i['fullname'] for i in jobs if(i['fullname'].find('bd-') == 0 or i['fullname'].find('test-cmdb5') == 0)]


def job_build(job_name, tag, job_type):
    server = jenkins.Jenkins(jenkins_url, username=jenkins_username, password=jenkins_password)
    next_bn = server.get_job_info(job_name)['nextBuildNumber']

    try:
        if job_type == "svn":
            server.build_job(job_name, parameters={"SVN_TAG": tag})
        elif job_type == "git":
            server.build_job(job_name, parameters={"GIT_TAG": tag})
    except:
        return 0

    return next_bn


def get_job_build_status(job_name, build_number, job_type):
    server = jenkins.Jenkins(jenkins_url, username=jenkins_username, password=jenkins_password)
    try:
        next_bn = server.get_job_info(job_name)['nextBuildNumber']
    except jenkins.NotFoundException:
        return {"result": "ERROR",
                "build_number": build_number,
                "out": "Requested item could not be found"}

    if build_number >= next_bn:
        build_info = {"result": "PENDING",
                      "build_number": build_number,
                      "out": "BuildNumber is Error.",
                      "building": "true"}
    else:
        try:
            time.sleep(5)
            result = server.get_build_info(job_name, build_number)
            if job_type == "svn":
                build_info = {'result': result['result'],
                              'build_number': result['number'],
                              'revisions': result['changeSet']['revisions'],
                              'building': result['building']}
            elif job_type == "git":
                build_info = {'result': result['result'],
                              'build_number': result['number'],
                              'revisions': [{u'module': result['actions'][2]['remoteUrls'][0],
                                             u'revision': result['actions'][2]['lastBuiltRevision']['SHA1'] }],
                              'building': result['building']}
            else:
                build_info = {"result": "ERROR",
                              "build_number": build_number,
                              "out": "Not found job_type."}
        except jenkins.NotFoundException:
            build_info = {"result": "ERROR",
                          "build_number": build_number,
                          "out": "Requested item could not be found"}
    return build_info


def job_get_number(job_name):
    server = jenkins.Jenkins(jenkins_url, username=jenkins_username, password=jenkins_password)
    job_info = server.get_job_info(job_name)
    try:
        last_number = job_info['lastCompletedBuild']['number']
    except:
        return 0
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


def get_repo_info(job_name):
    server = jenkins.Jenkins(jenkins_url, username=jenkins_username, password=jenkins_password)
    job_config = server.get_job_config(job_name)
    root = ET.fromstring(job_config.encode('utf8'))
    if ET.iselement(root.find('scm/locations/hudson.scm.SubversionSCM_-ModuleLocation/remote')):
        svn_url = root.find('scm/locations/hudson.scm.SubversionSCM_-ModuleLocation/remote').text
        tag_dir = root.find('properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/' +
                            'hudson.scm.listtagsparameter.ListSubversionTagsParameterDefinition/tagsDir')
        if ET.iselement(tag_dir):
            tag_dir = tag_dir.text
        tags_filter = root.find('properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/' +
                            'hudson.scm.listtagsparameter.ListSubversionTagsParameterDefinition/tagsFilter')
        if ET.iselement(tags_filter):
            tags_filter = tags_filter.text
        return {'svn_url':svn_url, 'tag_dir': tag_dir, 'tags_filter': tags_filter, 'job_type': 'svn'}
    elif ET.iselement(root.find('scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url')):
        git_url = root.find('scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url').text
        return {'git_url':git_url, 'job_type': 'git'}
    else:
        return {'job_type': None}

# from app.jenkins_ext import jobs_list_get, job_build

# bd-blink-server
# server = jenkins.Jenkins(jenkins_url, username=jenkins_username, password=jenkins_password)
# user = server.get_whoami()
# version = server.get_version()

# last_build_number = server.get_job_info(job_name)['lastBuild']['number']
# last_completed_build_number = server.get_job_info(job_name)['lastCompletedBuild']['number']
# build_info = server.get_build_info(job_name, last_build_number)
