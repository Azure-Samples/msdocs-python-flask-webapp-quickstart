targetScope = 'subscription'

// ================ //
// Input Parameters //
// ================ //

// RG parameters
@description('Optional. The name of the resource group to deploy')
param resourceGroupName string = 'validation-rg'

@description('Optional. The location to deploy into')
param location string = deployment().location

// =========== //
// Deployments //
// =========== //

// Resource Group
module rg 'br/modules:resources.resource-group:1.0.0' = {
  name: 'registry-rg'
  params: {
    name: resourceGroupName
    location: location
  }
}

// Network Security Group
module nsg 'br/modules:network.network-security-group:1.0.0' = {
  name: 'registry-nsg'
  scope: resourceGroup(resourceGroupName)
  params: {
    name: 'defaultNsg'
  }
  dependsOn: [
    rg
  ]
}

// Virtual Network
module vnet 'br/modules:network.virtual-network:1.0.0' = {
  name: 'registry-vnet'
  scope: resourceGroup(resourceGroupName)
  params: {
    name: 'defaultVNET'
    addressPrefixes: [
      '10.0.0.0/16'
    ]
    subnets: [
      {
        name: 'PrimarySubnet'
        addressPrefix: '10.0.0.0/24'
        networkSecurityGroupName: nsg.name
      }
      {
        name: 'SecondarySubnet'
        addressPrefix: '10.0.1.0/24'
        networkSecurityGroupName: nsg.name
      }
    ]
  }
}