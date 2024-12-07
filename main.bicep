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

@description('The Key Vault name')
param keyVaultName string
@description('The Key Vault SKU')
param keyVaultSku string
param enableSoftDelete bool 
@sys.description('The role assignments for the Key Vault')
param keyVaultRoleAssignments array 
var adminPasswordSecretName = 'adminPasswordSecretName'
var adminUsernameSecretName = 'adminUsernameSecretName'

module keyVault 'modules/kv.bicep' = {
  name: keyVaultName
  params: {
    name: keyVaultName
    location: location
    sku: keyVaultSku
    roleAssignments: keyVaultRoleAssignments
    enableVaultForDeployment: true
    enableSoftDelete: enableSoftDelete
  }
}

module containerRegistryModule './modules/cr.bicep' = {
  name: containerRegistryName
  params: {
    keyVaultResourceId: keyVault.outputs.resourceId
    keyVaultSecreNameAdminUsername: adminUsernameSecretName
    keyVaultSecreNameAdminPassword: adminPasswordSecretName
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

resource keyVaultReference 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
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
    dockerRegistryServerUserName: keyVaultReference.getSecret(adminUsernameSecretName)
    dockerRegistryServerPassword: keyVaultReference.getSecret(adminPasswordSecretName)

  }
}
