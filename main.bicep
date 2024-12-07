@description('Name of the Azure Container Registry')
param containerRegistryName string

@description('Location of resources')
param location string

@description('Image name for the container')
param containerRegistryImageName string

@description('Image version for the container')
param containerRegistryImageVersion string

@description('Name of the App Service Plan')
param appServicePlanName string

@description('Name of the Web App')
param webAppName string


module containerRegistryModule './modules/cr.bicep' = {
  name: containerRegistryName
  params: {
    containerRegistryName: containerRegistryName
    location: location
  }
}

module appServicePlanModule './modules/apsp.bicep' = {
  name: appServicePlanName
  params: {
    appServicePlanName: appServicePlanName
    location: location
  }
}

module webAppModule './modules/web.bicep' = {
  name: webAppName
  params: {
    webAppName: webAppName
    location: location
    appServicePlanId: appServicePlanModule.outputs.id
    containerRegistryName: containerRegistryName
    dockerRegistryImageName: containerRegistryImageName
    dockerRegistryImageVersion: containerRegistryImageVersion
    dockerRegistryServerUserName: containerRegistryModule.outputs.adminUsername
    dockerRegistryServerPassword: containerRegistryModule.outputs.adminPassword
    
  }
}
