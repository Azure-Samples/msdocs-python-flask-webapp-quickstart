using './main.bicep'

param location = 'North Europe'
param containerRegistryName = 'annacr'
param containerRegistryImageName = 'annaimage'
param containerRegistryImageVersion = 'main-latest'
param appServicePlanName = 'annaasp'
param webAppName = 'annawebapp'
param keyVaultName = 'annakv'
param keyVaultSku = 'standard'
param enableSoftDelete = true
param keyVaultRoleAssignments = [
  {
    principalId: '25d8d697-c4a2-479f-96e0-15593a830ae5' // BCSAI2024-DEVOPS-STUDENTS-A-SP
    roleDefinitionIdOrName: 'Key Vault Secrets User'
    principalType: 'ServicePrincipal'
    }
    {
      principalId: 'a03130df-486f-46ea-9d5c-70522fe056de' // BCSAI2024-DEVOPS-STUDENTS-A
      roleDefinitionIdOrName: 'Key Vault Administrator'
      principalType: 'Group'
      }
]



  