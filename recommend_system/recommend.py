import os
import pandas as pd
import numpy as np
import pymysql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/recommend', methods=['POST'])
def get_recommend():
  input_id = request.get_json()['id']
  df = get_db_data()
  tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0)
  tf_idf_vector = tf.fit_transform(df['introduction']) #各videoのintroductionをベクトル化する
  similarities_calc_result = []
  for item_index, item in enumerate(tf_idf_vector):
    # コサイン類似度を計算 (item: 指定のitem_index番目のvideoのintroductionの単語ベクトル)
    similarities = cosine_similarity(item, tf_idf_vector) # 返り値は 各videoのintroductionとの類似度を0~1で示した数値ベクトル
    similarities_index = similarities.argsort()[0]
    for sim_index in similarities_index:
      similarity = similarities[0][sim_index]
      similarities_calc_result.append([int(df["id"][item_index]), int(df["id"][sim_index]), similarity])
  # 各videoとその他のvideoとのintroductionベースの類似度の一覧データをdataframe型に変換
  result = pd.DataFrame(similarities_calc_result, columns=["Source_ID", "Similar_ID", "Similarity"])
  # 指定のvideoとその他videoとの類似度一覧データをdataframeから抽出
  recommend_df = result.ix[(result["Source_ID"] == input_id) & (result["Similar_ID"] != input_id)]
  # 抽出したデータから類似度の降順に並び替えし それらのvideoのIDの配列を生成
  recommend_id_list = recommend_df.sort_values('Similarity', ascending=False)['Similar_ID'].values.tolist()
  # 生成した配列をjsonデータとして返す
  return jsonify(recommend_id_list[:5])

def get_db_data():
  host = os.environ.get('DB_HOST')
  user = os.environ.get('DB_USER')
  password = os.environ.get('DB_PASSWORD')
  db_name = os.environ.get('DB_NAME')
  mysql_connection = pymysql.connect(host='localhost',user='root',password='',db='cooklab_development',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
  sql = "SELECT id,introduction FROM `videos` order by id"
  df = pd.read_sql(sql, mysql_connection)
  return df

if __name__ == '__main__':
    app.run()
