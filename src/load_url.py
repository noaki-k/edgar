import os
import re
import csv
import pandas as pd
import datetime
import urllib.request
import requests
from bs4 import BeautifulSoup
import db_util


def get_xbrl_idx(file):
    """xbrl.idxの内容を取得"""
    labels = []
    data = []

    # 区切り文字
    delimiter = '|'

    # ハイフン行を表す正規表現
    re_line_match = re.compile('^-+$').match

    with open(file, 'r', encoding='utf-8', newline='') as f:
        # ヘッダ行
        for row in csv.reader(f, delimiter=delimiter):
            if len(row) == 5:
                # ラベル行を取得
                # CIK|Company Name|Form Type|Date Filed|Filename
                labels = [value.replace(' ', '_') for value in row]
            if re_line_match(row[0]):
                # ハイフン行に達したのでブレーク
                break

        # データ行
        for row in csv.reader(f, delimiter=delimiter):
            data.append(row)

    return labels, data


def create_disclosed_info_df(data, year, term):
    """ファイルのぱすを特定するためのdfを作るメソッド"""
    CIK = []
    Company_Name = []
    Form_Type = []
    Date_Filed = []
    Filename = []
    for datum in data:
        CIK += [datum[0]]
        Company_Name += [datum[1]]
        Form_Type += [datum[2]]
        Date_Filed += [datum[3]]
        Filename += [datum[4]]

    disclosed_info_df = pd.DataFrame(
        data={'cik': CIK, 'company_name': Company_Name, 'form_type': Form_Type, 'date_filed': Date_Filed, 'file_name': Filename})
    disclosed_info_df = disclosed_info_df.sort_values('company_name')
    disclosed_info_df['file_path'] = disclosed_info_df['file_name'].str.replace('-', '').replace('.txt', '.json')
    disclosed_info_df['base_url'] = '/Archives/' + disclosed_info_df['file_path'].str.replace('.txt', '')
    disclosed_info_df['year'] = year
    disclosed_info_df['QT'] = term
    disclosed_info_df.drop(['file_path', 'file_name'], axis=1, inplace=True)

    return disclosed_info_df

def download_full_index():
    """
    form typeとそのファイルのパスを示すデータをダウンロードしてを作成して、
    それをcsvにするメソッド。将来的にはcsvではなくdbに格納するようにする
    """
    base_url = 'https://www.sec.gov/Archives/edgar/full-index/'
    dt_now = datetime.datetime.now()
    this_year = dt_now.year
    # TODO 2019までしか取れていない
    for year in range(2010, this_year):
        for term in range(1, 5):
            term = 'QTR' + str(term)
            url = base_url + '/' + str(year) + '/' + term + '/xbrl.idx'
            download_path = f'./{year}_{term}_xbrl.idx'
            urllib.request.urlretrieve(url, download_path)
            columns, data = get_xbrl_idx(download_path)
            disclosed_info_df = create_disclosed_info_df(data, year, term)
            db_util.DBUtil.insertDf(disclosed_info_df, 'base_info')
            os.remove(download_path)


if __name__ == '__main__':
    download_full_index()
