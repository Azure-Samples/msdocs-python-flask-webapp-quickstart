param containerRegistryName string
param location string = resourceGroup().location
param keyVaultResourceId string
#disable-next-line secure-secrets-in-params
param keyVaultSecreNameAdminUsername string
#disable-next-line secure-secrets-in-params
param keyVaultSecreNameAdminPassword string

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name:  containerRegistryName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

output id string = containerRegistry.id
output loginServer string = containerRegistry.properties.loginServer

resource adminCredentialsKeyVault 'Microsoft.KeyVault/vaults@2021-10-01' existing = if (!empty(keyVaultResourceId)) {
  name: last(split((!empty(keyVaultResourceId) ? keyVaultResourceId : 'dummyVault'), '/'))!
}

// create a secret to store the container registry admin username
resource secretAdminUserName 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = if (!empty(keyVaultSecreNameAdminUsername)) {
  name: !empty(keyVaultSecreNameAdminUsername) ? keyVaultSecreNameAdminUsername : 'dummySecret'
  parent: adminCredentialsKeyVault
  properties: {
    value: containerRegistry.listCredentials().username
}
}
// create a secret to store the container registry admin password 0
resource secretAdminUserPassword0 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = if (!empty(keyVaultSecreNameAdminPassword)) {
  name: !empty(keyVaultSecreNameAdminPassword) ? keyVaultSecreNameAdminPassword : 'dummySecret'
  parent: adminCredentialsKeyVault
  properties: {
    value: containerRegistry.listCredentials().passwords[0].value
}
}
// #disable-next-line outputs-should-not-contain-secrets
// var credentials = containerRegistry.listCredentials()
// #disable-next-line outputs-should-not-contain-secrets
// output adminUsername string = credentials.username
// #disable-next-line outputs-should-not-contain-secrets
// output adminPassword string = credentials.passwords[0].value
