import boto3
import os
import sys
import zipfile
sys.path.append('/tmp')
s3 = boto3.resource('s3')
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello():
  return "Hello World!"

@app.route('/recommend', methods=['POST'])
def get_recommend():
  input_id = request.get_json()['id']
  # s3からvideo同士のコサイン類似度を算出したcsvデータを取得
  download_file("cooklab-recommend")
  df = pd.read_csv('/tmp/dl_cosine_similarity.csv')
  # 指定のvideoとその他videoとの類似度一覧データをdataframeから抽出
  recommend_df = df.ix[(df["Source_ID"] == input_id) & (df["Similar_ID"] != input_id)]
  # 抽出したデータから類似度の降順に並び替えし それらのvideoのIDの配列を生成
  recommend_id_list = recommend_df.sort_values('Similarity', ascending=False)['Similar_ID'].values.tolist()
  # recommend_id_list = [2,1,3,5,7]
  recommend_id_list_str = [str(n) for n in recommend_id_list[:8]]
  # 生成した配列をjsonデータとして返す
  return ','.join(recommend_id_list_str)

def download_file(bucket_name):
  s3 = boto3.resource('s3')      # ③S3オブジェクトを取得
  bucket = s3.Bucket(bucket_name)
  bucket.download_file('cosine_similarity.csv', '/tmp/dl_cosine_similarity.csv')

def zip_download_open(bucket, download_file, local_download_path, local_download_dir):
  bucket.download_file(download_file, local_download_path)
  zip_ref = zipfile.ZipFile(local_download_path, 'r')
  zip_ref.extractall(local_download_dir)
  zip_ref.close()
  os.remove(local_download_path)

def load_numpy_pandas(bucket_name, s3):
  bucket = s3.Bucket(bucket_name)
  zip_download_open(bucket, 'numpy-pandas-packages.zip', '/tmp/numpy-pandas-packages.zip', '/tmp')

load_numpy_pandas('cooklab-recommend', s3)
import pandas as pd

if __name__ == '__main__':
  app.run()

