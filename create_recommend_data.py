import boto3
import os
import sys
import zipfile
import module_load_function as mlf
# from pprint import pprint
s3 = boto3.resource('s3')
rds = boto3.client('rds')
sys.path.append('/tmp')
os.mkdir('/tmp/sk')
sys.path.append('/tmp/sk')
mlf.load_numpy_pandas('cooklab-recommend', s3)
mlf.load_ssl_auth('cooklab-recommend', s3)
mlf.load_pymysql('cooklab-recommend', s3)
mlf.load_sklearn('cooklab-recommend', s3)
import pymysql
import numpy
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_db_data(rds):
  host = os.environ.get('DB_HOST')
  user = os.environ.get('DB_IAM_USER')
  db_name = os.environ.get('DB_NAME')
  password = rds.generate_db_auth_token(DBHostname=host, Port=3306, DBUsername=user)
  ssl = {'ca': '/tmp/rds-ca-2015-root.pem'}
  mysql_connection = pymysql.connect(host=host, user=user, password=password, db=db_name, charset='utf8', cursorclass=pymysql.cursors.DictCursor, ssl=ssl)
  sql = "SELECT id, commentary FROM `videos` order by id"
  df = pd.read_sql(sql, mysql_connection)
  mysql_connection.close()
  return df

def make_recommend_data_csv(s3, rds):
  df = get_db_data(rds)
  tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0)
  tf_idf_vector = tf.fit_transform(df['commentary']) #各videoのcommentaryをベクトル化する
  similarities_calc_result = []
  for item_index, item in enumerate(tf_idf_vector):
    # コサイン類似度を計算 (iteam: 指定のitem_index番目のvideoのintroductionの単語ベクトル)
    similarities = cosine_similarity(item, tf_idf_vector) # 返り値は 各videoのintroductionとの類似度を0~1で示した数値ベクトル
    similarities_index = similarities.argsort()[0]
    for sim_index in similarities_index:
      similarity = similarities[0][sim_index]
      similarities_calc_result.append([int(df["id"][item_index]), int(df["id"][sim_index]), similarity])
  # 各videoとその他のvideoとのintroductionベースの類似度の一覧データをdataframe型に変換
  result = pd.DataFrame(similarities_calc_result, columns=["Source_ID", "Similar_ID", "Similarity"])
  result.to_csv("/tmp/cosine_similarity.csv") # //Lambdaでは一時的なファイルの出力先に/tmpが使える
  bucket = s3.Bucket("cooklab-recommend")
  bucket.upload_file("/tmp/cosine_similarity.csv", "cosine_similarity.csv")

def lambda_handler(event, context):
  make_recommend_data_csv(s3, rds)
