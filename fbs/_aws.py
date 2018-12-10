from os.path import relpath, join

import boto3
import os

def upload_folder_contents(dir_path, dest_path, bucket, key, secret):
    result = []
    for file_path in _iter_files_recursive(dir_path):
        file_relpath = relpath(file_path, dir_path)
        # Replace backslashes on Windows by forward slashes:
        file_relpath = file_relpath.replace(os.sep, '/')
        file_dest = dest_path + '/' + file_relpath
        upload_file(file_path, file_dest, bucket, key, secret)
        result.append(file_dest)
    return result

def upload_file(file_path, dest_path, bucket, key, secret):
    s3 = boto3.resource(
        's3', aws_access_key_id=key, aws_secret_access_key=secret
    )
    s3.Bucket(bucket).upload_file(file_path, dest_path)

def _iter_files_recursive(dir_path):
    for subdir_path, dir_names, file_names in os.walk(dir_path):
        for file_name in file_names:
            yield join(subdir_path, file_name)