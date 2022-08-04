import json
import os
import shutil
import sys
from distutils.dir_util import copy_tree
from hashlib import new

sys.path.append('../.modules/') 


import newjob
import yaml
from yaml.loader import SafeLoader

f = open('./init.json')
config = json.load(f)["parameters"]
name = config["name"]
rg = config["rg"]
localpath = config["localpath"]
stages = config["stages"]
f.close()


print(" ======================================= ")
print(" ANGULAR + NGINX ")
print(" ======================================= ")
bicepParamsPath = './.src/bicep-params/'

#colocar isso em um módulo
if not os.path.exists(bicepParamsPath):
    os.mkdir(bicepParamsPath)
for stage in stages:
    params = open('./.src/bicep-params.json')
    bicep = json.load(params)
    print(" PREPARANDO PARAMETROS (%s)"%stage["name"])
    stageParams = open('%sparams-%s.json'% (bicepParamsPath, stage["name"]),'w') 
    bicepName = config["name"]+stage["name"]
    sku = stage["sku"]
    imageRepository = stage["imageRepository"] + ":latest"

    bicep["parameters"]["commomName"]["value"] = name
    bicep["parameters"]["name"]["value"] = bicepName
    bicep["parameters"]["sku"]["value"] = sku
    bicep["parameters"]["dockerImage"]["value"] = imageRepository
    bicep = json.dumps(bicep)
    stageParams.write(bicep)
    stageParams.close()

for stage in stages:
    print(" ======================================= ")
    print(' CRIANDO AMBIENTE AZURE (%s)'%stage["name"])
    print(" ======================================= ")

    paramsFile = '%sparams-%s.json'% (bicepParamsPath, stage["name"])

    cmd = "az deployment group create --resource-group %s --template-file ./angular-nginx.bicep --parameters %s" % (rg, paramsFile)
    os.system(cmd)



print(" ======================================= ")

print(" GERANDO 'DockerFile' ")
shutil.copy("./.src/Dockerfile", localpath)

print(" CRIANDO 'nginx.conf' ")
shutil.copy("./.src/nginx.conf", localpath)

print(" ALTERE o valor `outputPath`: `dist/` no arquivo 'angular.json' ")

os.system("pause")

print(" ======================================= ")
print(" GERANDO PASTA '.azuredevops' ")
print(" ======================================= ")

## colocar isso em um módulo
with open('./.src/az-pipeline.yml','r') as f:
    data = yaml.load(f, Loader=SafeLoader)
    for stage in stages:
        data = newjob.replaceVariables(data,"envtargetFile",config["envtargetFile"])
        data = newjob.replaceVariables(data,"dockerRegistryServiceConnection","acr%s"%name)
        data = newjob.addnewTrigger(data,stage["branch"])
        data = newjob.addnewjob(data,stage)

with open('./.src/.azuredevops/azure-pipelines.yml','w') as x:
    yaml.dump(data, x, sort_keys=False, default_flow_style=False)

print(" MOVENDO PASTA '.azuredevops' ")
azpath = "%s/.azuredevops"%localpath
copy_tree("./.src/.azuredevops/",azpath)

print(" =======================================")
