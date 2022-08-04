import json
def addnewjob(data,stage):
    job = {
        'job': stage["name"],
        'displayName': stage["name"],
        'condition': "eq(variables['Build.SourceBranch'], 'refs/heads/%s')"%stage["branch"],
        'variables': [
            {
                'group': stage["variablegroup"]
            }
        ],
        'steps': [
            {
                'template': 'templates/build.yml',
                'parameters': {
                    'env': stage["name"],
                    'tag': '$(tag)',
                    'imageRepository': stage["imageRepository"],
                    'dockerRegistryServiceConnection': '$(dockerRegistryServiceConnection)'
                }
            }
        ]
    }
    data["stages"][0]["jobs"].append(job)
    return data

def addnewTrigger(data,trigger):
    data["trigger"].append(trigger)
    return data

def replaceVariables(data,vname,value):
    data["variables"][vname] = value
    return data

