import os
from typing import Tuple
from azure.storage.blob import BlobServiceClient



def get_account_credentials()-> Tuple[str, str]:
    """
    Return the storage account name
    and the storage account url.
    Both are used by the BlobServiceClient class interact with azure datalake and 
    among other thing authenticate, ...

    Documentation:
    -------------
        https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient?view=azure-python

    Return:
    ------
        STORAGE_ACCOUNT_KEY: The storage account key
        ACCOUNT_URL: the storage account url
    """
    try:
        STORAGE_ACCOUNT_NAME = os.environ["STORAGE_ACCOUNT_NAME"]
        STORAGE_ACCOUNT_KEY = os.environ["STORAGE_ACCOUNT_KEY"]
        ACCOUNT_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        return STORAGE_ACCOUNT_KEY, ACCOUNT_URL
    except KeyError:
        print("Missing account key or/and account name")
        return None, None
    

async def download_blob_to_file(blob_service_client: BlobServiceClient, container_name: str):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob="sample-blob.txt")
    with open(file=os.path.join(r'filepath', 'filename'), mode="wb") as sample_blob:
        download_stream = await blob_client.download_blob()
        data = await download_stream.readall()
        sample_blob.write(data)


def download_file_from_data_lake_container(container_name:str, save_to_path:str)->None:
    """
    Uploads a file to an azure datalake container.

    Arguments:
    ----------
        container_name: the container to upload the file to
        save_to_path: the path to save the downloaded files to

    Returns:
    --------
        None

    Usage
    -----
    container_name = "raw6"
    #file_to_upload = "Data_Engineer_Test.pdf"
    save_to_path = "data"
    account_name, account_key = get_account_credentials()
   
    download_file_from_data_lake_container(container_name, save_to_path)
    """
    account_key, account_url = get_account_credentials()
    if account_key is None or account_url is None:
        raise Exception("Account Key or account name is invalide")
    try:
        blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)
        container_client = blob_service_client.get_container_client(container_name)
        if container_client.exists():
            container_content = container_client.list_blobs()
            for blob in container_content:
                file_in_container = blob.get("name")
                if file_in_container is not None:
                    local_file_path = os.path.join(save_to_path, file_in_container)
                    blob_client = container_client.get_blob_client(file_in_container)
                    with open(local_file_path, "wb") as fp:
                        downloaded_object = blob_client.download_blob()
                        fp.write(downloaded_object.readall())
                    print(f"Downloaded {local_file_path} succeeded")
        else:
            print(f"Container {container_name} does not exists.")
            
    except Exception as e:
        print(e)



if __name__ =="__main__":
    container_name = "raw"
    #file_to_upload = "Data_Engineer_Test.pdf"
    save_to_path = "data"
    account_name, account_key = get_account_credentials()
   
    download_file_from_data_lake_container(container_name, save_to_path)