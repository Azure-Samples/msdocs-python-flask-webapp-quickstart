param location string
param acrName string
param appServicePlanName string
param webAppName string
param containerRegistryImageName string
param containerRegistryImageVersion string

// Deploy ACR
module acr './modules/acr.bicep' = {
  name: 'acrDeploy'
  params: {
    name: acrName
    location: location
    acrAdminUserEnabled: true
  }
}

// Deploy App Service Plan
module appServicePlan './modules/app-service-plan.bicep' = {
  name: 'appServicePlanDeploy'
  params: {
    name: appServicePlanName
    location: location
    sku: {
      capacity: 1
      family: 'B'
      name: 'B1'
      size: 'B1'
      tier: 'Basic'
    }
  }
}

// Deploy Web App
module webApp './modules/web-app.bicep' = {
  name: 'webAppDeploy'
  params: {
    name: webAppName
    location: location
    kind: 'app'
    serverFarmResourceId: appServicePlan.outputs.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${acr.outputs.loginServer}/${containerRegistryImageName}:${containerRegistryImageVersion}'
      appCommandLine: ''
    }
    appSettingsKeyValuePairs: {
      WEBSITES_ENABLE_APP_SERVICE_STORAGE: 'false'
      DOCKER_REGISTRY_SERVER_URL: 'https://${acr.outputs.loginServer}'
      DOCKER_REGISTRY_SERVER_USERNAME: acr.outputs.adminUsername
      DOCKER_REGISTRY_SERVER_PASSWORD: acr.outputs.adminPassword
    }
  }
}
