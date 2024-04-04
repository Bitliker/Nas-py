import os


os.environ['tmdb_token']='eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkOWJkMDg3M2YyOTc5NzQ1ODRjOTVkZDdhNzY4MmViMSIsInN1YiI6IjY1ZTE4ZGYzYTI4NGViMDE0YmQ0MzQxYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.f86NpcMGCTj1OM8XgvL2ifb9K3QN1qnrxZ-s1KFhSF4'



"""清理空文件夹
@param root_path 根文件夹路径
"""
# def clear_folder(root_path):
#     for root, dirs, files in os.walk(root_path, topdown=False):
#         for dir in dirs:
#             dir_path = os.path.join(root, dir)
#             if len(os.listdir(dir_path)) == 0:
#                 os.rmdir(dir_path)
#                 print("清理文件夹:", dir_path)


# clear_folder("D:\Test")


import zipfile
from cryptography.fernet import Fernet
import os

# 步骤 1：将文件压缩为 zip 存档
def compress_file(file_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(file_path, os.path.basename(file_path))

# 第 2 步：加密 zip 存档
def encrypt_zip(zip_path, encrypted_zip_path, key):
    with open(zip_path, 'rb') as f:
        data = f.read()

    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data)

    with open(encrypted_zip_path, 'wb') as f:
        f.write(encrypted_data)

# Example usage
file_to_compress = 'path_to_your_file.txt'
zip_file_path = 'compressed_file.zip'
encrypted_zip_file_path = 'encrypted_compressed_file.zip'
encryption_key = Fernet.generate_key()

# Compress the file
compress_file(file_to_compress, zip_file_path)

# Encrypt the zip archive
encrypt_zip(zip_file_path, encrypted_zip_file_path, encryption_key)