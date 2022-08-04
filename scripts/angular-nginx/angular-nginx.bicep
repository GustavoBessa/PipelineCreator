@sys.description('Nome do projeto')
param commomName string
param name string
param sku string
param dockerImage string

// param location string = resourceGroup().location
param location string = 'eastus2'

param planname string = toLower('${name}-plan')
param acrname string = toLower('acr${commomName}')

param imgname string = '${acrname}.azurecr.io/${dockerImage}'

resource appServicePlan 'Microsoft.Web/serverfarms@2020-06-01' = {
  name: planname
  location: location
  properties: {
    reserved: true
  }
  sku: {
    name: sku
  }
  kind: 'linux'
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2021-06-01-preview' = {
  name: acrname
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

resource webApp 'Microsoft.Web/sites@2021-01-01' = {
  name: name
  location: location
  tags: {}
  properties: {
    siteConfig: {
      appSettings: [ {
          name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
          value: containerRegistry.listCredentials().passwords[0].value
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: '${acrname}.azurecr.io'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_USERNAME'
          value: containerRegistry.listCredentials().username
        }]
      linuxFxVersion: 'DOCKER|${imgname}'
    }
    serverFarmId: appServicePlan.id
  }
}
