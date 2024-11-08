import mysql.connector
import os
import openpyxl

fieldnames = None
rows = []

# エクセルファイルの取り込み
wb = openpyxl.load_workbook("jrct_data_sample.xlsx")
ws = wb["Sheet1"]

for row in ws.rows:
    if row[0].row == 1:
        # １行目
        fieldnames = list(map(lambda x : x.value, row))
    else:
        # ２行目以降
        rows.append(tuple(list(map(lambda x : x.value, row))))

# print(rows)
print(fieldnames)

# ['初回公表日', '最終公表日', '実施期間（終了日）', '研究の種別', 
# '治験の区分', '責任研究者の組織名', '他施設の責任研究者の組織名', 
# '試験のフェーズ', '対象疾患名', '医薬品の一般名称', '販売名', 
# '研究資金等の提供組織名称', '依頼者の名称', 
# '他の臨床研究登録期間発行の研究番号', '試験進捗状況', 'JRCT_ID', 
# '研究名称', '組入れ開始日', '試験概要の目標症例数', 
# '試験概要の試験のタイプ', '試験問い合わせ窓口のE-mail', 
# '試験問い合わせ窓口の担当者', 'url', '平易な研究名称']

name_en = ['date_public_first', 'date_public_final', 'date_end', 'research_type', 'ct_filter',
           'researcher_org', 'other_researcher_org', 'ct_phase', 'disease_name', 'medicine_name_general', 'medicine_name_sale',
           'funding_org', 'dependence_name', 'research_num', 'ct_progression', 'jrctid',
           'research_name', 'date_arrangement_start', 'num_target_disease', 'abstract_ct_type', 'inquiry_email',
           'inquiry_window', 'url', 'research_name_simple']

row_new = []

for k, v in zip (fieldnames, name_en):
    row_new.append(k + ':' + v)

fieldnames = row_new

print(fieldnames)

len_rows = len(rows)
print(f"There are {len_rows} lines to be inserted")

t_name = "t_oncolo_jrct"

connection = mysql.connector.connect(
    user=os.environ['USER'], password=os.environ['PASS'], 
    host=os.environ['HOST'], port=os.environ['PORT'], 
    database=os.environ['DB'])
print("DB connected")

cursor = connection.cursor()

cursor.execute('DROP TABLE IF EXISTS ' + t_name)
fields_string = ", ".join(list(map(lambda e: e.split(":")[1] + " TEXT COMMENT \'" + e.split(":")[0] + "\'", fieldnames)))
create_query = "CREATE Table " + t_name + "(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, " + fields_string + ")DEFAULT CHARACTER SET=utf8"
cursor.execute(create_query)

fields_title_string = ", ".join(list(map(lambda e: e.split(":")[1], fieldnames)))

query = 'INSERT INTO ' + t_name + '(' + fields_title_string + ') VALUES '+ "(" + '%s, ' * (len(fieldnames) - 1) + '%s' + ")"                                                         

cursor.executemany(query, rows)

connection.commit()
connection.close()

# cursor = connection.cursor()

# cursor.execute('DROP TABLE IF EXISTS ' + t_name)
# fields_string = ", ".join(list(map(lambda e: e.split(":")[1] + " TEXT COMMENT \'" + e.split(":")[0] + "\'", fieldnames)))
# create_query = "CREATE Table " + t_name + "(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, " + fields_string + ")DEFAULT CHARACTER SET=utf8"
# cursor.execute(create_query)

# fields_title_string = ", ".join(list(map(lambda e: e.split(":")[1], fieldnames)))

# query = 'INSERT INTO ' + t_name + '(' + fields_title_string + ') VALUES '+ "(" + '%s, ' * (len(fieldnames) - 1) + '%s' + ")"                                                         

# cursor.executemany(query, rows)

# connection.commit()
# connection.close()