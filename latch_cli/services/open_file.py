import webbrowser

import requests

from latch_cli.config.latch import LatchConfig
from latch_cli.utils import _normalize_remote_path, retrieve_or_login

config = LatchConfig()
endpoints = config.sdk_endpoints


def open_file(remote_file: str):
    """Opens a console URL in the browser corresponding to a remote path

    Args:
        remote_file:   A valid path to a remote destination, of the form

                                [latch://] [/] dir_1/dir_2/.../dir_n/filename,

                       where filename is the name of a file.

    This function will open the specified file in console on the user's browser.
    It will error if the path is invalid, the file doesn't exist, or if the path
    points to a directory.

    Example: ::

        open("sample.txt") # sample.txt exists

            Opens the file sample.txt in the user's browser.

        open("latch:///dir1/doesnt_exist/sample.txt") # doesnt_exist does not exist

            Will throw an error, as we cannot open a file that does not exist.

        open("/dir1/dir2") # dir1/dir2 is a directory

            Will throw an error, as this operation tries to open a directory
    """
    token = retrieve_or_login()
    remote_file = _normalize_remote_path(remote_file)

    url = endpoints["id"]
    headers = {"Authorization": f"Bearer {token}"}
    data = {"filename": remote_file}

    response = requests.post(url, headers=headers, json=data)

    try:
        json_data = response.json()
        node_id = json_data["id"]
        open_url = f"{config.console_url}/data/{node_id}"
        webbrowser.open(open_url)
    except:
        raise ValueError(
            "Either specified file does not exist or you are trying to open a"
            " directory."
        )
