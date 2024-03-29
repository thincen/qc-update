#!/usr/bin/env python3
# -*-coding:utf-8 -*-

import requests
import time
import os,json
#import sys
from datetime import datetime,timezone,timedelta
from lxml import etree

def fetch(key,page=1):
    url='https://www.hb-erm.com/index.php?m=goods&a=search&key='+key+'&cate=334&p='+str(page)
    header={'user-agent':'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    html = requests.get(url,headers=header).text
    res=[]
    content = etree.HTML(html)
    arr=content.xpath("//tbody//tr//td[position()<6]")#//text()[normalize-space()]")
    for node in arr:
        nodestr=node.xpath("string(.)")
        if "促" in nodestr:
            nodestr=nodestr.replace("促","")
        nodestr=nodestr.strip()
        res.append(nodestr)
    return res

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
        namearr=res[i].split()
        if len(namearr)==1:
            name=namearr[0]
        else:
            name=namearr[1]
            if name=="水质":
                name=namearr[2]
        node['name']=name
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

def pushDB(data):
    url=os.getenv("APIURL")
    if(url==None):
        #print('getenv("APIURL") err:',file=sys.stderr,flush=True)
        pushPlus("getenv('APIURL') err")
        return
    header={'Content-Type':'application/json'}
    err=[]
    #print(data)
    for node in data:
        dbData={}
        dbData['id']=node['id']
        dbData['c']=node['val']
        dbData['name']=node['name']
        dbData['num']=node['num']
        if(node['date']!=''):
            dbData['expiration']=int(datetime.strptime(node['date'],'%Y-%m-%d').timestamp())
        else:
            dbData['expiration']=-1
        dbData['update']=int(datetime.now().astimezone(timezone(timedelta(hours=8))).timestamp())
        body=json.dumps(dbData).encode(encoding='utf-8')
        res=requests.post(url,headers=header,data=body)
        res.encoding = 'utf-8'
        #print(res.text)
        if(res.status_code!=200):
            err.append(json.loads(res.text).msg)
        time.sleep(1)
        res.close()
    if(len(err)>0):
        pushPlus(err)

def pushPlus(msg):
    token = os.getenv("PUSHPLUSHTOKEN") #在pushpush网站中可以找到
    if(token==None):
        #print('getenv("PUSHPLUSHTOKEN") err:',file=sys.stderr,flush=True)
        pushPlus("getenv('PUSHPLUSHTOKEN') err")
        return
    title= '质控样更新' #改成你要的标题内容
    #content ='内容' #改成你要的正文内容
    url = 'http://www.pushplus.plus/send'
    data = {
        "token":token,
        "title":title,
        "content":msg,
        "template":"json",
        "channel":"cp",
        "webhook":"thincen"
    }
    body=json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type':'application/json'}
    requests.post(url,data=body,headers=headers)

def main():
    keys=["cu","pb","zn","cd","fe","mn","ni","k","na","ca","mg","hg","se","as","六价铬","总铬","油","ph","电导","总磷","氨","阴离子","挥发酚","总氮","COD","氮氧化物","硝酸盐","硫","硬度","BOD","醛","苯"]
    msg=[]
    for key in keys:
        data = parseRes(fetch(key))
        time.sleep(2)
        if(len(data)>0):
            save(data)
            try:
                pushDB(data)
            except Exception as e:
                pushPlus({'msg':str(e)})
                pass
            msg.extend(data)
    pushPlus(msg)

if __name__ =="__main__":
    main()
