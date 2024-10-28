# jrct_index_scraping
存在するidを取得するためのファイル
jrctで検索し，一覧を表示し，jrct idの一覧を取得
jrct_index_data.csvを作成
## selenium
seleniumを使用
# main.py
jrct_index_data.csv　（idデータ）からスクレイピング
contact for public queryとcontact for scientific queryと付く項目を試験問い合わせ先と責任研究者問い合わせ先としてスクレイピングしている
excelに記録，既存のidの場合はスキップ
# jrct_update_scraping.py
上位の数ページをスクレイピングし，jrct idを取得，さらに，そのidをもとに各詳細ページをスクレイピングし，excelファイルに追記
# 基本的な利用方法
はじめはjrct_index_scraping.pyを実行し，idを取得，idのcsvを作成，次にそれをもとにmain.pyを実行する．これによって各詳細ページもスクレイピングする．そしてexcelファイルが生成される．
新しいデータのみ追記したい場合は，jrct_updata_scrapingを実行するのみで良い．
#　どのデータを取っているか
まず，tabledata.txtのようにデータが得られている．
あとはここから実際に得たいデータを選んでいる．どのデータを使うかは，main.pyでcombined_listpairsとして定義している．これを変更すれば良い．