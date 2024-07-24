import streamlit as st
import hashlib
import os
from datetime import datetime


class FileUtil:

    def get_file_hash(self, file, hash_algorithm='md5'):
        hasher = hashlib.md5() if hash_algorithm == 'md5' else hashlib.sha256()
        file.seek(0)
        while chunk := file.read(8192):
            hasher.update(chunk)
        file.seek(0)
        return hasher.hexdigest()

    def save_file(self, file, upload_dir, suffix):
        # Generate unique identifier (MD5 or SHA256)
        file_hash = self.get_file_hash(file)
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
        # Create new file name
        new_file_name = f"{file_hash}_{timestamp}"
        # Save file
        file_path = os.path.join(upload_dir, new_file_name+suffix)
        with open(file_path, 'wb') as f:
            f.write(file.getbuffer())
        return file_path


fileUtil = FileUtil()
