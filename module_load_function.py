import boto3
import os
import sys
import zipfile

def load_pymysql(bucket_name, s3):
  bucket = s3.Bucket(bucket_name)
  zip_download_open(bucket, 'pymysql-packages.zip', '/tmp/pymysql-packages.zip', '/tmp')

def load_sklearn(bucket_name, s3):
  bucket = s3.Bucket(bucket_name)
  zip_download_open(bucket, 'sklearn-packages.zip', '/tmp/sk/sklearn-packages.zip', '/tmp/sk')

def load_numpy_pandas(bucket_name, s3):
  bucket = s3.Bucket(bucket_name)
  zip_download_open(bucket, 'numpy-pandas-packages.zip', '/tmp/numpy-pandas-packages.zip', '/tmp')

def load_ssl_auth(bucket_name, s3):
  bucket = s3.Bucket(bucket_name)
  bucket.download_file("rds-ca-2015-root.pem", '/tmp/rds-ca-2015-root.pem')

def zip_download_open(bucket, download_file, local_download_path, local_download_dir):
  bucket.download_file(download_file, local_download_path)
  zip_ref = zipfile.ZipFile(local_download_path, 'r')
  zip_ref.extractall(local_download_dir)
  zip_ref.close()
  os.remove(local_download_path)
