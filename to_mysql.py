import mysql.connector
import os
import openpyxl

names_jp = None
rows = []
other_hospitals = []

# エクセルファイルの取り込み
wb = openpyxl.load_workbook("jrct_data_sample.xlsx")
ws = wb["Sheet1"]

for row in ws.rows:
    if row[0].row == 1:
        # １行目
        names_jp = list(map(lambda x : x.value, row))
    else:
        # ２行目以降
        row_raw = list(map(lambda x : x.value, row))
        rows.append(row_raw)

        # filter cancer records

        if (row_raw[8] == None or ("癌" not in row_raw[8] and "がん" not in row_raw[8])): continue

        if (row_raw[6] != None and row_raw[6] != ""):
            jrctid = row_raw[15]
            hospitals_list = row_raw[6].split('\n')
            for hospital in hospitals_list:
                if hospital != '':
                    table = str.maketrans({
                                '\u3000': ' ',
                                })
                    hospital = hospital.translate(table)
                    other_hospitals.append([jrctid, hospital])

print(other_hospitals[0:5])

def process_date(date):

    if (date == None or date == ""): return date

    def wrap_date(s):
        y = s.split("年")[0]
        m = s.split("年")[1].split("月")[0]
        d = s.split("年")[1].split("月")[1].split("日")[0]

        return y + "/" + m + "/" + d

    if ("令和" not in date and "平成" not in date): 
        return wrap_date(date)

    hd = date.split("年")[0]
    tl = date.split("年")[1]

    y = None

    if ("令和" in hd):
        if "元" in hd:
            y = 2019
        else:
            y = 2019 + int(hd.split("令和")[1]) - 1

    elif ("平成" in hd): 
        y = 1989 + int(hd.split("平成")[1]) - 1

    return wrap_date(str(y) + "年" + tl)

def process_research_type(research_type):
    if (research_type == None or research_type == ""): return research_type
    if (research_type == "企業治験"): return 1
    elif (research_type == "医師主導治験"): return 2
        
def process_ct_filter(ct_filter):
    if (ct_filter == None or ct_filter == ""): return ct_filter
    if (ct_filter == "主たる治験"): return 1
    elif (ct_filter == "拡大治験"): return 2
    elif (ct_filter == "主たる治験と拡大治験のいずれにも該当しない"): return 3

def process_ct_progression(ct_progression):
    if (ct_progression == None or ct_progression == ""): return ct_progression
    if ("募集前" == ct_progression): return 1
    elif ("募集中" == ct_progression): return 2
    elif ("募集中断" == ct_progression): return 3
    elif ("募集終了" == ct_progression): return 4
    elif ("研究終了" == ct_progression): return 5

def process_ct_type(ct_type):
    if (ct_type == None or ct_type == ""): return ct_type
    if (ct_type == "介入研究"): return 1
    elif (ct_type == "観察研究"): return 2

# ①日付はdate型にする *
# ②治験名は長い場合があるのでtextに、その他名前とかはｖarchar(255)にする *
# research_type ③治験のタイプはtiny intにして、１：企業治験、2：医師主導治験にする *
# ct_filter 1 主たる治験 2 拡大治験 3 主たる治験と拡大治験のいずれにも該当しない *
# email varchar (255) *
# num MediumInt *
# jrct varchar(255) *
# ct_type 1 介入研究 2 観察研究 *
# ct progression 試験進捗状況 1募集前　2募集中 3募集中断 4募集終了　5研究終了 *
# ひとつの治験に対する病院は複数になるので検索を考えて、治験　＞　病院複数でもてるテーブルを別で作る

# https://docs.google.com/spreadsheets/d/1vWqzDrA_jyHXQIi2fQTHK8J6zYC7f8cSCrtBC4Km3OI/edit?usp=sharing

# 病院名は揺らぎがあるので、現在１つになっていると思うが複数（例えば５個ぐらい持てるようにして）
# スクレイピングで存在しない病院名が発生したら、通知するようにしてその病院名を既存の病院テーブルに追加する。
# 新しい病院名は当面ＳＱＬで追加するで良いと思います

# エクセル取得は毎日新規でもよい
# 　インサートとUPDATEはJRCTのIDで判断する必要がある

# 毎回クリアするのではなく、historyは残すように

def process_rows(old_rows):
    new_rows = []

    for row in old_rows:

        # 多施設のデータはこのテーブルに挿入しない
        row.pop(6)

        # DATE
        row[0] = process_date(row[0])
        row[1] = process_date(row[1])
        row[2] = process_date(row[2])
        # research_type
        row[3] = process_research_type(row[3])
        # ct_filter
        row[4] = process_ct_filter(row[4])
        #ct_progression
        row[13] = process_ct_progression(row[13])
        # ct_type
        row[18] = process_ct_type(row[18])
        new_rows.append(row)

    return new_rows

rows = process_rows(rows)

# ['初回公表日', '最終公表日', '実施期間（終了日）', '研究の種別', '治験の区分', 
#  '責任研究者の組織名', '試験のフェーズ', '対象疾患名', '医薬品の一般名称', 
#  '販売名', '研究資金等の提供組織名称', '依頼者の名称', '他の臨床研究登録期間発行の研究番号', '試験進捗状況',
#  'JRCT_ID', '研究名称', '組入れ開始日', '試験概要の目標症例数', '試験概要の試験のタイプ', 
#  '試験問い合わせ窓口のE-mail', '試験問い合わせ窓口の担当者', 'url', '平易な研究名称']

# '他施設の責任研究者の組織名'は含めていないです

names_en = ['date_public_first', 'date_public_final', 'date_end', 'research_type', 'ct_filter',
           'researcher_org', 'ct_phase', 'disease_name', 'medicine_general_name', 
           'medicine_brand_name','funding_org', 'dependence_name', 'research_num', 'ct_progression', 
           'jrctid','research_name', 'enrollment_start_date', 'num_target_disease', 'ct_type', 
           'inquiry_window_email', 'inquiry_window_person', 'url', 'research_simple_name']

types = ["DATE", "DATE", "DATE", "TEXT", "VARCHAR(255)",
         "VARCHAR(255)", "VARCHAR(255)", "TEXT", "TEXT",
         "TEXT", "VARCHAR(255)", "VARCHAR(255)", "VARCHAR(255)", "TEXT",
         "VARCHAR(255)", "TEXT", "VARCHAR(255)", "MEDIUMINT", "TEXT",
         "VARCHAR(255)", "VARCHAR(255)", "VARCHAR(255)", "TEXT"]

# 多施設のデータはこのテーブルに挿入しない
names_jp.pop(6)

row_new = []

for a, b, c in zip (names_jp, names_en, types):
    row_new.append(a + ':' + b + ':' + c)

fieldnames = row_new

# print(fieldnames)

len_rows = len(rows)
print(f"There are {len_rows} lines to be inserted")

#insert into t_oncolo_jrct

t_name = "t_oncolo_jrct"

connection = mysql.connector.connect(
    user=os.environ['USER'], password=os.environ['PASS'], 
    host=os.environ['HOST'], port=os.environ['PORT'], 
    database=os.environ['DB'])
print("DB connected")

cursor = connection.cursor()

# cursor.execute('DROP TABLE IF EXISTS ' + t_name)
fields_string = ", ".join(list(map(lambda e: e.split(":")[1] + " " + e.split(":")[2] + " COMMENT \'" + e.split(":")[0] + "\'", fieldnames)))
create_query = "CREATE TABLE IF NOT EXISTS " + t_name + "(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, " + fields_string + ", UNIQUE KEY (jrctid))DEFAULT CHARACTER SET=utf8"
cursor.execute(create_query)

fields_title_string = ", ".join(list(map(lambda e: e.split(":")[1], fieldnames)))

update_string = ", ".join(list(map(lambda e: e + "=ins." + e, names_en)))
# print(update_string)

query = 'INSERT INTO ' + t_name + '(' + fields_title_string + ') VALUES '+ "(" + '%s, ' * (len(fieldnames) - 1) + '%s' + ")" + " AS ins ON DUPLICATE KEY UPDATE " + update_string                                                         

cursor.executemany(query, rows)

connection.commit()
connection.close()

#insert into jrctid_hospital_mapping

fieldnames_mapping = ["jrctid:jrctid:VARCHAR(255)", "hospital_id:hospital_id:VARCHAR(255)"]

t_name_mapping = "jrctid_hospital_mapping"

connection = mysql.connector.connect(
    user=os.environ['USER'], password=os.environ['PASS'], 
    host=os.environ['HOST'], port=os.environ['PORT'], 
    database=os.environ['DB'])
print("DB connected")

# Handle unread result error without buffered=True
cursor = connection.cursor(buffered=True)

cursor.execute('DROP TABLE IF EXISTS ' + t_name_mapping)
fields_string = ", ".join(list(map(lambda e: e.split(":")[1] + " " + e.split(":")[2] + " COMMENT \'" + e.split(":")[0] + "\'", fieldnames_mapping)))
create_query = "CREATE TABLE IF NOT EXISTS " + t_name_mapping + "(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, " + fields_string + ")DEFAULT CHARACTER SET=utf8"
cursor.execute(create_query)

# find and replace hospital name to id

inserted_hospitals = []
unknown_hospitals = []

for item in other_hospitals:
    query = "SELECT id FROM hospitals where %s LIKE CONCAT('%', name, '%')"
    # print(query)
    cursor.execute(query, [item[1]])
    result = cursor.fetchone()
    if result != None and result != "":
        inserted_hospitals.append([item[0], result[0]])
    else:
        unknown_hospitals.append(item[1])

print("Length of other_hospitals: ", len(other_hospitals))

print("Length of inserted_hospitals: ", len(inserted_hospitals))

unknown_hospitals = sorted(list(set(unknown_hospitals)))
print("Length of unknown_hospitals: ", len(unknown_hospitals))

with open("/root/opt/unknown_hospitals.txt", "w") as output:
    for item in unknown_hospitals:
        output.write("%s\n" % item)

#insert into jrctid_hospital_mapping

fields_title_string = ", ".join(list(map(lambda e: e.split(":")[1], fieldnames_mapping)))

query = 'INSERT INTO ' + t_name_mapping + '(' + fields_title_string + ') VALUES '+ "(" + '%s, ' * (len(fieldnames_mapping) - 1) + '%s' + ")"                                                         

print(query)

cursor.executemany(query, inserted_hospitals)

connection.commit()
connection.close()