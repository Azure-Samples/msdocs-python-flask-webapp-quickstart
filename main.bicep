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

var adminUsernameSecretName = 'adminPasswordSecretName0'
var adminPasswordSecretName = 'adminPasswordSecretName1'

module containerRegistryModule './modules/cr.bicep' = {
  name: 'containerRegistryDeployment'
  params: {
    name: containerRegistryName
    location: location
  }
}

module appServicePlanModule './modules/cr.bicep' = {
  name: 'appServicePlanDeployment'
  params: {
    name: appServicePlanName
    location: location
  }
}

module webAppModule './modules/web.bicep' = {
  name: 'webAppDeployment'
  params: {
    name: webAppName
    location: location
    appServicePlanId: appServicePlanModule.outputs.id
    dockerRegistryName: containerRegistryName
    dockerRegistryImageName: containerRegistryImageName
    dockerRegistryImageVersion: containerRegistryImageVersion
    dockerRegistryServerUserName: adminUsernameSecretName
    dockerRegistryServerPassword: adminPasswordSecretName
  }
}
