#!/bin/bash
#Usage: deplay prod app.
#Last Modified: chuanshuang.
# ./deploy_test.sh -d lib,apps,config -m ppp -v laster
# ./deploy_test.sh -d lib,apps,sss -m ppp -v 1882

inventory_prd=/opt/soft_build/DEPLOY/inventory_dir/project
apprun_prd=/opt/soft_build/DEPLOY/inventory_dir/apprun

while getopts "m:d:v:" opt; do
  case $opt in
    m)
      module=$OPTARG
      ;;
    d)
      deploy_dir=$OPTARG
      ;;
    v)
      version=$OPTARG
      ;;
    ?)
      echo "Usage: `echo ${0} | awk -F'/' '{print $NF}'` -m module_name -d deploy_dir -v version"; exit 110;
      ;;
  esac
done


###Check module##
if [ ${module}xxx = ""xxx ]; then
   echo -e "Not found module_name, \n\nUsage: `echo ${0} | awk -F'/' '{print $NF}'` -m module_name -d deploy_dir -v version"; exit 110;
fi

###Check deploy_dir##
if [ ${deploy_dir}xxx = ""xxx ]; then
   echo -e "Not fond deploy_dir, \n\nUsage: `echo ${0} | awk -F'/' '{print $NF}'` -m module_name -d deploy_dir -v version"; exit 110;
fi

###Check version##
if [ ${version}xxx = ""xxx ]; then
   echo -e "Not fond version, \n\nUsage: `echo ${0} | awk -F'/' '{print $NF}'` -m module_name -d deploy_dir -v version"; exit 110;
fi

###Get app_type##
app_type=`/opt/app/applications/bd-deploy/scripts/get_inventory_var.py ${module} app_type`
if [ $? -ne 0 ]; then echo "Error: Get module ${module}'s app_type is fault! Please check ansible inventory."; exit 127; fi
if [ -z $app_type ]; then echo "Error: Get module ${module}'s app_type is null! Please check ansible inventory."; exit 127; fi

###Check module deploy_dir##
DEPLOY_DIR=/opt/soft_build/DEPLOY/${module}/${version}
if [ ! -d ${DEPLOY_DIR} ]; then
   echo -e "Not found dir ${DEPLOY_DIR}, \n\nUsage: `echo ${0} | awk -F'/' '{print $NF}'` -m module_name -d deploy_dir -v version"; exit 110;
fi


###Print deploy vars##
echo module: ${module}
echo deploy_dir: ${deploy_dir}
echo app_type: ${app_type}
echo version: ${version}
echo start_time: `date +'%Y-%m-%d-%H:%M:%S'`

echo ""


function update_apps(){
  echo "##### update apps_dir for ${module} #####"
  ansible ${module} -u apprun -i ${inventory_prd} --private-key=${apprun_prd} -m synchronize -a "src=${DEPLOY_DIR}/apps/ dest=/opt/app/applications/${module}/apps mode=push delete=yes checksum=yes"
  if [ $? -ne 0 ]; then echo "Error: Update apps_dir is fault!"; exit 127; fi
  echo ""
}

function update_lib(){
  echo "##### update lib_dir for ${module} #####"
  ansible ${module} -u apprun -i ${inventory_prd} --private-key=${apprun_prd} -m synchronize -a "src=${DEPLOY_DIR}/lib/ dest=/opt/app/applications/${module}/lib mode=push delete=yes checksum=yes"
  if [ $? -ne 0 ]; then echo "Error: Update lib_dir is fault!"; exit 127; fi
  echo ""
}

function update_config(){
  echo "##### update config_dir for ${module} #####"
  ansible ${module} -u apprun -i ${inventory_prd} --private-key=${apprun_prd} -m synchronize -a "src=${DEPLOY_DIR}/config/ dest=/opt/app/applications/${module}/config mode=push delete=yes checksum=yes"
  if [ $? -ne 0 ]; then echo "Error: Update config_dir is fault!"; exit 127; fi
  echo ""
}


function start_tomcat(){
  echo "###Start remote tomcat applications.##"
  ansible ${module} -u apprun -i ${inventory_prd} --private-key=${apprun_prd} -m shell -a "source /etc/profile && /opt/programs/tomcatctl/bin/tomcatctl ${module} start"
  if [ $? -ne 0 ]; then echo "Error: Start remote applications is fault!"; exit 127; fi
  echo ""
}

function stop_tomcat(){
  echo "###Stop remote tomcat applications.##"
  ansible ${module} -u apprun -i ${inventory_prd} --private-key=${apprun_prd} -m shell -a "source /etc/profile && /opt/programs/tomcatctl/bin/tomcatctl ${module} stop"
  if [ $? -ne 0 ]; then echo "Error: Stop remote applications is fault!"; exit 127; fi
  echo ""
}

function clean_tomcat_workspace(){
  echo "###Clean remote tomcat workspace.##"
  ansible ${module} -u apprun -i ${inventory_prd} --private-key=${apprun_prd} -m file -a "path=/opt/app/applications/${module}/work/Catalina state=absent"
  #ansible ${module} -u apprun -i ${inventory_prd} --private-key=${apprun_prd} -m shell -a "/bin/rm -rf /opt/app/applications/${module}/work/Catalina/localhost/${module}/ && /bin/echo /opt/app/applications/${module}/work/Catalina/localhost/ && /bin/ls -al /opt/app/applications/${module}/work/Catalina/localhost/"
  if [ $? -ne 0 ]; then echo "Error: Clean workspace is fault!"; exit 127; fi
  echo ""
}

function start_jar(){
  echo "###Start remote jar applications.##"
  ansible ${module} -u apprun -i ${inventory_prd} --private-key=${apprun_prd} -m shell -a "source /etc/profile && /opt/app/applications/${module}/bin/${module}.sh start"
  if [ $? -ne 0 ]; then echo "Error: Start remote applications is fault!"; exit 127; fi
  echo ""
}

function stop_jar(){
  echo "###Stop remote jar applications.##"
  ansible ${module} -u apprun -i ${inventory_prd} --private-key=${apprun_prd} -m shell -a "source /etc/profile && /opt/app/applications/${module}/bin/${module}.sh stop"
  if [ $? -ne 0 ]; then echo "Error: Stop remote applications is fault!"; exit 127; fi
  echo ""
}


if [ ${app_type}xxx = "tomcat"xxx ]; then
  stop_tomcat
  clean_tomcat_workspace
elif [ ${app_type}xxx = "jar"xxx ]; then
  stop_jar
else
  echo "Error: module ${module}'s app_type is fault! Please check ansible inventory."
  exit 127
fi


OLD_IFS="$IFS"
IFS=","
dir_arr=(${deploy_dir})
IFS="$OLD_IFS"

for i in ${dir_arr[@]}
do
  case ${i} in
    apps)
      update_apps
      ;;
    lib)
      update_lib
      ;;
    config)
      update_config
      ;;
    *)
      echo -e "Error input dir_type: ^^^ " ${i} " ^^^" ; exit 127
      ;;
  esac
done
echo -e "==================================================================="


if [ ${app_type}xxx = "tomcat"xxx ]; then
  start_tomcat
elif [ ${app_type}xxx = "jar"xxx ]; then
  start_jar
else
  echo "Error: app_type is fault!"
  exit 127
fi

echo ""
echo end_time: `date +'%Y-%m-%d-%H:%M:%S'`
exit 0