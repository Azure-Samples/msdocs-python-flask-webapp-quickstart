from azure.storage.blob import ContainerClient

connect_str = "BlobEndpoint=https://minkonto.blob.core.windows.net/;QueueEndpoint=https://minkonto.queue.core.windows.net/;FileEndpoint=https://minkonto.file.core.windows.net/;TableEndpoint=https://minkonto.table.core.windows.net/;SharedAccessSignature=sv=2021-12-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2023-05-03T13:59:56Z&st=2023-04-29T05:59:56Z&spr=https&sig=xvoKm%2BQlfKkk%2B%2BVeCk5%2FTLDe9yGs3YYpbaq3J0qXfBs%3D"
container_name = "photos" # container name in which images will be store in the storage account

container = ContainerClient.from_connection_string(conn_str=connect_str, container_name=container_name)

blob_list = container.list_blobs()
for blob in blob_list:
    print(blob.name)