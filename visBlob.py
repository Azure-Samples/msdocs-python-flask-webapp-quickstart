from azure.storage.blob import ContainerClient, __version__
from azure.storage.blob import BlobServiceClient

connect_str = "BlobEndpoint=https://minkonto.blob.core.windows.net/;QueueEndpoint=https://minkonto.queue.core.windows.net/;FileEndpoint=https://minkonto.file.core.windows.net/;TableEndpoint=https://minkonto.table.core.windows.net/;SharedAccessSignature=sv=2021-12-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2023-05-03T13:59:56Z&st=2023-04-29T05:59:56Z&spr=https&sig=xvoKm%2BQlfKkk%2B%2BVeCk5%2FTLDe9yGs3YYpbaq3J0qXfBs%3D"
container_name = "photos" # container name in which images will be store in the storage account
blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str) # create a blob service client to interact with the storage account
container_client = blob_service_client.get_container_client(container=container_name) # get container client to interact with the container in which images will be stored


def listBlob():
    blob_list = [] 
    blob_items = container_client.list_blobs()
    
    for blob in blob_items:
        blob_client = container_client.get_blob_client(blob=blob.name)
        blob_list.append(blob_client.url)  

    for x in blob_list:
        print(x.name)

def main():
    listBlob()


if __name__ == '__main__':
   main()