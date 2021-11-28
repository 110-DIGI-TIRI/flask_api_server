from bs4 import BeautifulSoup
from time import sleep
from collections import Counter
from base64 import b64encode

import pandas as pd
import requests
import re
import json
import numpy as np


def momo(headers, keyword, pages):
    try:
        urls = []
        for page in range(1, pages):
            url = 'https://m.momoshop.com.tw/search.momo?_advFirst=N&_advCp=N&curPage={}&searchType=1&cateLevel=2&ent=k&searchKeyword={}&_advThreeHours=N&_isFuzzy=0&_imgSH=fourCardType'.format(
                page, keyword)
            print(url)
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text)
                for item in soup.select('li.goodsItemLi > a'):
                    # urls.append('https://m.momoshop.com.tw'+item['href'])
                    # 修正成電腦版的網頁
                    urls.append('https://www.momoshop.com.tw' + item['href'].replace('/goods.momo?i_code=',
                                                                                     '/goods/GoodsDetail.jsp?i_code='))
            urls = list(set(urls))
        #     break

        df_momo = []
        for i, url in enumerate(urls):
            columns = []
            values = []

            resp = requests.get(url, headers=headers)
            soup = BeautifulSoup(resp.text)
            # 標題
            title = soup.find('meta', {'property': 'og:title'})['content']
            # 品牌
            brand = soup.find('meta', {'property': 'product:brand'})['content']
            # 連結
            link = soup.find('meta', {'property': 'og:url'})['content']
            # 原價
            try:
                price = re.sub(r'\r\n| ', '', soup.find('del').text)
            except:
                price = ''
            # 特價
            amount = soup.find('meta', {'property': 'product:price:amount'})['content']
            # 類型
            # 描述
            try:
                # desc = soup.find('div',{'class':'Area101'}).text
                # desc = re.sub('\r|\n| ', '', desc)
                desc = soup.find('meta', {'property': 'og:description'})['content']
            except:
                desc = ''
            # 產品圖片
            try:
                img = soup.find('meta', {'property': 'og:image'})['content']
            except:
                img = ''

            columns += ['title', 'brand', 'link', 'price', 'amount', 'desc', 'image']
            values += [title, brand, link, price, amount, desc, img]
            ndf = pd.DataFrame(data=values, index=columns).T
            df_momo.append(ndf)

        df_momo = pd.concat(df_momo, ignore_index=True)
    except:
        df_momo = ''
    # df_momo.to_csv('momo.csv',encoding='utf-8-sig',index=False)
    return df_momo


def PChome(headers, keyword, pages):
    try:
        # 蒐集產品連結清單
        prodids = []
        for page in list(range(1, pages)):
            url = 'https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={}&page={}&sort=sale/dc'.format(keyword,
                                                                                                           page)
            resp = requests.get(url, headers=headers)
            for prodid in resp.json()['prods']:
                prodids.append(prodid['Id'])
            prodids = list(set(prodids))
        # 爬取產品資料：產品資料放在兩個不同的API，這兩個API response的資料結構不一樣

        # ecapi
        df1 = []
        for i, Id in enumerate(prodids):
            columns, values = [], []
            sleep(0.7)
            ecapi = 'https://mall.pchome.com.tw/ecapi/ecshop/prodapi/v2/prod/{}&fields=Seq,Id,Stmt,Slogan,Name,Nick,Store,PreOrdDate,SpeOrdDate,Price,Discount,Pic,isCombine&_callback=jsonp_prod&1587196620'.format(
                Id)
            resp = requests.get(ecapi, headers=headers)
            data = re.sub('try{jsonp_prod\(|\}\);\}catch\(e\)\{if\(window.console\)\{console.log\(e\)\;\}', '',
                          resp.text)
            data = json.loads(data)[Id + '-000']

            for key, value in data.items():
                columns.append(key)
                values.append(value)
            ndf = pd.DataFrame(data=values, index=columns).T
            df1.append(ndf)
        df1 = pd.concat(df1, ignore_index=True)

        # cdn
        df2 = []
        for i, Id in enumerate(prodids):
            columns, values = [], []
            sleep(0.7)
            cdn = 'https://ecapi.pchome.com.tw/cdn/ecshop/prodapi/v2/prod/{}/desc&fields=Id,Stmt,Equip,Remark,Liability,Kword,Slogan,Author,Transman,Pubunit,Pubdate,Approve&_callback=jsonp_desc'.format(
                Id + '-000')
            resp = requests.get(cdn, headers=headers)
            data = re.sub('try\{jsonp_desc\(|\}\);\}catch\(e\)\{if\(window.console\)\{console.log\(e\)\;\}', '',
                          resp.text)
            data = json.loads(data)
            data = data[Id]

            for key, value in data.items():
                columns.append(key)
                values.append(value)
            ndf = pd.DataFrame(data=values, index=columns).T
            df2.append(ndf)

        df2 = pd.concat(df2, ignore_index=True)

        # 合併兩個資料表

        df1['Id'] = df1['Id'].apply(lambda x: re.sub('-000$', '', x))
        df = pd.merge(df1, df2, how='left', on='Id')
        # 資料清理
        df.drop(columns=['PreOrdDate', 'SpeOrdDate', 'Discount'], inplace=True)
        # print(df.info())

        # 處理【Price】資料
        df.loc[:, "Price"] = df.loc[:, "Price"].astype(str).str.replace(", 'Prime': ''}", '')
        df.loc[:, "Price"] = df.loc[:, "Price"].astype(str).str.replace("{'M': ", '')

        # print(df.loc[:,"Price"])
        # print(df.loc[:,"Price"].str.split(",").str.get(0))
        df.loc[:, "Price"] = df.loc[:, "Price"].astype(str).str.replace(" 'P': ", '')

        # 新增【SpePrice】資料
        df['SpePrice'] = df.loc[:, "Price"].astype(str).str.split(",").str.get(1)

        # 新增【OriPrice】資料
        df['OriPrice'] = df.loc[:, "Price"].astype(str).str.split(",").str.get(0)
        df.loc[df['OriPrice'] == '0', 'OriPrice'] = df.loc[df['OriPrice'] == '0', 'SpePrice'].values

        # 刪除【Price】資料
        df.drop(columns=['Price'], inplace=True)

        # 處理【Pic】資料
        df.loc[:, "Pic"] = df.loc[:, "Pic"].astype(str).str.replace("{'B': '", '')
        df.loc[:, "Pic"] = df.loc[:, "Pic"].astype(str).str.replace("', 'S': '", ',')
        df.loc[:, "Pic"] = df.loc[:, "Pic"].astype(str).str.replace("'}", '')

        # 新增【Image】資料
        df['image'] = ["https://d.ecimg.tw/"] + df.loc[:, "Pic"].astype(str).str.split(",").str.get(1)

        # 刪除【Pic】資料
        df.drop(columns=['Pic'], inplace=True)

        # 新增【Web】資料
        df['link'] = ["https://24h.pchome.com.tw/prod/"] + df.loc[:, "Id"]
        # 儲存資料
        # df.to_csv('PChome.csv',encoding='utf-8-sig',index=False)
    except:
        df = ''
    return df


def tidyDfandgetPrice(df):  # 整理pchome
    df_tidy = df

    df_tidy = df[{'Name', 'isCombine', 'OriPrice', 'SpePrice', 'image', 'link', 'Slogan'}]
    df_tidy = df_tidy.rename(columns={'OriPrice': 'rawprice'})
    df_tidy = df_tidy.rename(columns={'SpePrice': 'discountprice'})
    df_tidy = df_tidy.rename(columns={'Slogan': 'desc'})
    df_tidy = df_tidy.rename(columns={'Name': 'name'})
    df_tidy = df_tidy.rename(columns={'isCombine': 'iscombine'})
    df_tidy['discountpercent'] = round(
        (df_tidy['discountprice'].astype(float) / df_tidy['rawprice'].astype(float)) * 100)
    df_tidy['shop'] = 'PChome'

    return df_tidy


def momoShoptidyDfandgetPrice(df):  # 整理momo
    df.loc[:, "price"] = df.loc[:, "price"].astype(str).str.replace(",", '')
    df_tidy = df[{'title', 'price', 'amount', 'image', 'link', 'desc'}]
    # df_tidy.loc[df_tidy['price']==0,'price']=df_tidy.loc[df_tidy['price']==0,'amount'].values
    df_tidy = df_tidy.rename(columns={'title': 'name'})
    df_tidy = df_tidy.rename(columns={'price': 'rawprice'})
    df_tidy = df_tidy.rename(columns={'amount': 'discountprice'})
    # df_tidy.loc[:,'RawPrice']=df_tidy.loc[:,'RawPrice'].fillna(df_tidy.loc[:,'DiscountPrice'])
    # df_tidy=df_tidy.fillna(0)
    df_tidy.loc[df_tidy['rawprice'] == '', 'rawprice'] = df_tidy.loc[df_tidy['rawprice'] == '', 'discountprice'].values
    df_tidy['discountpercent'] = round(
        (df_tidy['discountprice'].astype(float) / df_tidy['rawprice'].astype(float)) * 100)
    df_tidy['shop'] = 'momo'

    return df_tidy


# 算四分位數
def measureIQR(list):
    q1 = np.quantile(list, 0.25)  # 美國的四分位數
    q3 = np.quantile(list, 0.75)
    return q1, q3


def getSameProductName(name_list):
    same_product = []
    dict_result = Counter(name_list)
    for key, value in dict_result.items():
        if value >= 2:
            same_product.append(key)
    return same_product


def getLowerPriceinSameProduct(df_type, product_name):
    minprice_message = ''
    for i in range(len(product_name)):
        price_list = df_type[df_type['name'] == product_name[i]]['discountprice']
        if len(set(price_list)) == 1:
            minprice_message = minprice_message + product_name[i] + ': Same Prize' + '\n'
        if len(set(price_list)) != 1:
            minprice_message = minprice_message + product_name[i] + ': ' + min(price_list) + '\n'
    return minprice_message


# keyboard name整理(排除組合價)
def getnotCombineProduct(df):
    df['iscombine'] = df['iscombine'].fillna(0)  # momo的isCombine是空值，給予其值
    df['discountprice'] = df['discountprice'].astype(float)
    df['rawprice'] = df['rawprice'].astype(float)
    df['discountpercent'] = df['discountpercent'].astype(float)
    df_noCombine = df[df['iscombine'] == 0]
    return df_noCombine


# 算四分位,刪除outlier的產品
def deleteExcludeOutlierPrice(df):
    discountprice = df['discountprice'].astype(float)
    q1, q3 = measureIQR(discountprice)
    iqr = q3 - q1
    lowest_bound = q1 - 1.5 * iqr  # 最小值
    highest_bound = q3 + 1.5 * iqr  # 最大值
    df_excludeOutlier = df[(df['discountprice'] <= highest_bound) & (df['discountprice'] >= lowest_bound)]
    return q1, q3, df_excludeOutlier


def sortNormalProductbyPrice(df, q1, q3):  # 售價排序 並只return需要顯示之欄位
    df_normalprice = df[(df['discountprice'] <= q3) & (df['discountprice'] >= q1)]
    df_normalprice_increase = df_normalprice.sort_values(['discountprice'], ascending=True)
    df_normalprice_increase = df_normalprice_increase[
        {'name', 'rawprice', 'discountprice', 'discountpercent', 'shop', 'image', 'link'}]
    df_normalprice_decrease = df_normalprice.sort_values(['discountprice'], ascending=False)
    df_normalprice_decrease = df_normalprice_increase[
        {'name', 'rawprice', 'discountprice', 'discountpercent', 'shop', 'image', 'link'}]
    return df_normalprice_increase, df_normalprice_decrease


def sortNormalProductbyDiscountpercent(df, q1, q3):  # 折扣比例排序 #目前沒用到
    df_normalprice = df[(df['discountprice'] <= q3) & (df['discountprice'] >= q1)]
    df_normalprice_increase = df_normalprice.sort_values(['discountpercent'], ascending=True)
    df_normalprice_decrease = df_normalprice.sort_values(['discountpercent'], ascending=False)
    return df_normalprice_increase, df_normalprice_decrease


# 取價格最低的 並只return需要顯示之欄位
def getLowestPrice(df):
    df_price_min = df[df['discountprice'] == df['discountprice'].min()]
    df_price_min = df_price_min[{'name', 'rawprice', 'discountprice', 'discountpercent', 'shop', 'image', 'link'}]
    return df_price_min


# 取折數最低的 並只return需要顯示之欄位
def getLowestDiscountpercent(df):
    df_discountpercent_min = df[df['discountpercent'] == df['discountpercent'].min()]
    df_discountpercent_min = df_discountpercent_min[
        {'name', 'rawprice', 'discountprice', 'discountpercent', 'shop', 'image', 'link'}]

    return df_discountpercent_min


# dataframe轉成json
def dataframeTransfertoJson(df):
    # df_price_decrease=pd.read_csv(df)
    js = df.to_json(orient='records', force_ascii=False)

    return js
