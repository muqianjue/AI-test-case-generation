import base64
import uuid
import os

class DownloadLink:
    def get_file_base64(self, bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()