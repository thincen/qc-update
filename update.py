#!/usr/bin/env python3
# -*-coding:utf-8 -*-

import requests 
from datetime import datetime,timezone,timedelta
from lxml import etree

def fetch(key,page=1):
    url='https://www.hb-erm.com/index.php?m=goods&a=search&key='+key+'&cate=334&p='+str(page)
    header={'user-agent':'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    html = requests.get(url,headers=header).text
    content = etree.HTML(html)
   
    arr=content.xpath("//tbody//tr//td[position()<6]//text()[normalize-space()]")
    for i in range(len(arr)):
        arr[i]=arr[i].strip()
    return arr

# 检查是否已经记录过
# 未记录 添加记录 返回Flase
def isExist(id):
    list=open('list','r+',encoding='utf-8')
    for line in list.readlines():
        if id in line:
            list.close()
            return True
    list.write(id+"|")
    list.close()
    return False

# 格式化数据
def parseRes(res):
    data = []
    for i in range(0,len(res),5):
        node={}
        node['id']=res[i+1]
        if isExist(node['id']):
            continue
        node['name']=res[i].split()[1]
        node['num']=res[i+2]
        val=res[i+3].replace('/l','/L')
        val=val.replace('/ml','/mL')
        node['val']=val
        node['date']=res[i+4]
        data.append(node)
    return data

def save(data):
    #save_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    save_time=datetime.now().astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    s=""
    for node in data:
        s = s + node['name'] + '|' + node['id'] + '|' + node['num'] + '|' + node['val'] + '|' + node['date'] + '|' + save_time + '\n'
        print(node['name']+':'+node['val']+'\n')
    f = open('./zhikong.txt','a',encoding='utf-8')
    f.write(s)
    f.close()

def main():
    keys=["cu","pb","zn","cd","fe","mn","ni","k","na","ca","mg","hg","se","as","六价铬","总铬","油","ph","电导","总磷","氨氮","阴离子","挥发酚","总氮","COD","氮氧化物","硝酸盐"]
    for key in keys:
        data = parseRes(fetch(key))
        if(len(data)>0):
            save(data)

if __name__ =="__main__":
    main()
