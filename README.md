## File

- create_recommend_data: Lambda関数(tf-idfによるコサイン類似度一覧データ作成)
- zappaフォルダ: レコメンドシステムのAPI機能

## Structure

- 日次でLambda関数をCloud Whachから実行し tf-idfで各videoのコサイン類似度一覧データファイル(csv)を作成しs3に保存
- APIが呼び出され際には上記のcsvファイルをs3から読み込み
- postパラメーターで渡されたvideo_idを基にコサイン類似度の数値が高い上位8本のvideoのidをクライアントに返す
