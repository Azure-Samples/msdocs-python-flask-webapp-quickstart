param name string
param location string
param kind string
param serverFarmResourceId string
param siteConfig object
param appSettingsKeyValuePairs object

resource webApp 'Microsoft.Web/sites@2022-09-01' = {
  name: name
  location: location
  kind: kind
  properties: {
    serverFarmId: serverFarmResourceId
    siteConfig: siteConfig
  }
}

resource webAppSettings 'Microsoft.Web/sites/config@2022-09-01' = {
  parent: webApp
  name: 'appsettings'
  properties: appSettingsKeyValuePairs
}
