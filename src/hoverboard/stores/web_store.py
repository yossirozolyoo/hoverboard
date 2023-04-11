import shutil
from urllib3 import PoolManager, Retry
from urllib3.exceptions import HTTPError
from typing import Union
from .store import BinaryStore


http = PoolManager(retries=Retry(connect=5, read=2, redirect=5))


class WebStore:
    """
    Downloads files into `BinaryStore`s.
    """
    @staticmethod
    def get(url: str, file_name: str = None, download_store: BinaryStore = None) -> Union[str, None]:
        """
        Download a file into the web store.

        :param url: The URL to download
        :param file_name: The name to give to the downloaded file. `None` for name extraction from the URL
        :param download_store: The store to download the file in. `None` for temporary store.
        :return: The downloaded file path
        """
        if file_name is None:
            _, file_name = url.rsplit('/', 1)
            file_name, _ = file_name.split('?', 1)

        if download_store is None:
            download_store = BinaryStore()

        # Check if file was downloaded previously
        if download_store.isfile(file_name):
            return download_store.get_path(file_name)

        # Download the file
        try:
            with http.request('GET', url, preload_content=False) as response:
                if response.status != 200:
                    # Server couldn't return the file
                    return None

                with download_store.open(file_name, 'wb') as file_obj:
                    shutil.copyfileobj(response, file_obj)

        except HTTPError:
            return None

        # Download finished, return the file path
        return download_store.get_path(file_name)
