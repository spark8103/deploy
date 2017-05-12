import jenkins
import time

jenkins_url = 'http://172.31.217.62:8080/'
jenkins_username = 'zhangchuanshuang'
jenkins_password = 'XpqXvYy7rc5jyKMuw4'


def jobs_list_get():
    server = jenkins.Jenkins(jenkins_url, username=jenkins_username, password=jenkins_password)
    jobs = server.get_all_jobs()
    return [ i['fullname'] for i in jobs]


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
    pass

# from app.jenkins_ext import jobs_list_get, job_build

# bd-blink-server
# server = jenkins.Jenkins('http://172.31.217.62:8080/', username='zhangchuanshuang', password='XpqXvYy7rc5jyKMuw4')
# user = server.get_whoami()
# version = server.get_version()

# last_build_number = server.get_job_info(job_name)['lastBuild']['number']
# last_completed_build_number = server.get_job_info(job_name)['lastCompletedBuild']['number']
# build_info = server.get_build_info(job_name, last_build_number)

