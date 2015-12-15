#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "litongxue"

import os
import sys
import time
import requests
import lxml
import re
import MySQLdb
from bs4 import BeautifulSoup as bsoup
from threading import Thread

class JdParser:
    def __init__(self):
        self.conn = MySQLdb.connect(host="127.0.0.1", user="user", passwd="password", db="db", charset="utf8")
        self.link = ''
        self.html_doc = ''
        self.insert_count = 0

    #启动爬虫
    def start_spider(self):
        print "start spider"
        page = 1
        is_loop = True
        
        while is_loop:
            headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}
            baseUrl = "http://list.jd.com/list.html?cat=652%2C654%2C832&ev=&page="+str(page)
            # baseUrl = baseUrl + str(page)
            try:
                r = requests.get(baseUrl, headers = headers)
            except Exception,e:
                is_loop = False
                continue;
            page = page + 1
            self._handle_doc(r.text)
            time.sleep(1)
            print page

            # is_loop = False
            # continue;
        return
    #处理爬虫爬到的数据
    def _handle_doc(self, html_doc):
        soup = bsoup(html_doc, "lxml")

        for ele in soup.find(id = "plist").ul.children:
            eleClass = ele['class'][0]
            #jd 商品
            if eleClass == "gl-item":
                aDom = ele.a
                reobj = re.compile(r'href="(.*?)".*ata-lazy-img="(.*?)"', re.IGNORECASE)
                result = reobj.findall(str(aDom))
                #商品详情页面url 
                skuUrl = result[0][0] 
                #图片 商品图片
                skuPic = result[0][1] 
                if skuUrl is not None:
                    reid = re.compile(r'/(\d+).html', re.IGNORECASE)
                    result = reid.findall(str(skuUrl))
                    # print result;
                    skuId = result[0]
                else:
                    skuId = ''

                #商品价格
                skuPrice = self.get_price(skuId)
                
                skuName = ele.find_all("div", class_="p-name")
                skuName = skuName[0]
                reName = re.compile(r'<em>(.*?)</em>(.*)')
                nameResult = reName.findall(str(skuName))
                skuName = nameResult[0][0]

                self._insert_database(skuId, skuUrl, skuName, skuPrice, skuPic)
    
    #获取商品价格:因为页面上商品价格是ajax获取的
    def get_price(self, skuId):
        if skuId is not None:
            priceUrl = 'http://p.3.cn/prices/mgets?skuIds=J_'+skuId+'&type=1'
            headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}

            try:
                r = requests.get(priceUrl, headers = headers)
                r.json()
                priceData = r.json()
                skuPrice = priceData[0]['p']
            except Exception,e:
                skuPrice = 0;
        # time.sleep(0.1)
        return skuPrice

    #入库
    def _insert_database(self, skuId, skuUrl, skuName, skuPrice, skuPic):
        cursor = self.conn.cursor()
        #TODO: REPLACE INTO  及时更新url title , pic, 
        sql = "insert into jd_sku(sku_id, sku_url, sku_title, sku_price, sku_pic, creation_date) values(%s, %s, %s, %s, %s, %s)"
        creation_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        param = (skuId, skuUrl, skuName, skuPrice, skuPic, creation_date)
        
        try:
            n = cursor.execute(sql, param)
            cursor.close()
            self.conn.commit()
            self.insert_count = self.insert_count + 1
            print 'insert', self.insert_count
        except Exception,e:
            return;
        
    #释放资源
    def __del__(self):
        print "spider end"
        self.conn.close()

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    baseUrl = [
        'http://list.jd.com/list.html?cat=652%2C654%2C831&JL=6_0_0&page=', #数码相机
        'http://list.jd.com/list.html?cat=652%2C654%2C12342&JL=6_0_0&page=', #运动相机
        'http://list.jd.com/list.html?cat=652,654,844&go=0&JL=6_0_0&page=', #微单
        # 'http://list.jd.com/list.html?cat=652%2C654%2C5012&page=2&JL=6_0_0',
        # 'http://list.jd.com/list.html?cat=652,654,834&page=2&go=0&JL=6_0_0', #镜头
        # 'http://list.jd.com/list.html?cat=652%2C654%2C832&page=2&JL=6_0_0', #单反
        # 'http://list.jd.com/list.html?cat=652,654,12343&page=2&go=0&JL=6_0_0', #户外器材
    ]

    # jdParser = JdParser()
    # # jdParser.start_spider()

    # for i in range(len(baseUrl)):
    #     print baseUrl[i];
    #     Thread(target=jdParser.start_spider(), args=(baseUrl[i])).start()

    # exit()
    jdParser = JdParser()
    jdParser.start_spider()
    exit()
