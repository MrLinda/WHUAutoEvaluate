import requests
import json
import time
import os

# Cookie
# JSESSIONID = ''
# insert_cookie = ''
# iPlanetDirectoryPro = ''
# 每隔多久完成一门课的评价（单位：秒）
# delay_time = 10
# 每门多少分
# score = 100.0

JSESSIONID = input('请输入JESSIONID：')
insert_cookie = input('请输入insert_cookie：')
iPlanetDirectoryPro = input('请输入iPlanetDirectoryPro：')
delay_time = int(input('请输入完成一门课评价后的延时（单位：秒）：') or '10')
# score = float(input('请输入每门课程评价的总分（满分100分）：') or '100.0')
score = 100.0

data = {}

status = 403
while status == 403:
    cookie = 'iPlanetDirectoryPro=' + iPlanetDirectoryPro + ';JSESSIONID=' + JSESSIONID + ';insert_cookie=' + insert_cookie + ';'
    headers = {
        'content-type': 'application/json',
        'cookie': cookie
    }
    host = 'https://ugsqs.whu.edu.cn/jslist'
    receive = requests.post(host, headers=headers, data=data)
    status = receive.status_code
    if status == 200:
        xsxh = json.loads(receive.text)['list'][0]['USERID']
    else:
        print('Cookie错误！请重新填写Cookie！')
        JSESSIONID = input('请输入JESSIONID：')
        insert_cookie = input('请输入insert_cookie：')
        iPlanetDirectoryPro = input('请输入iPlanetDirectoryPro：')

headers = {
        'content-type': 'application/json',
        'cookie': cookie
    }
host = 'https://ugsqs.whu.edu.cn/getxnxqList'
receive = requests.post(host, headers=headers, data=data)
info = json.loads(receive.text)
xqid = ''
for i in info:
    if i['SFDQXQ'] == '是':
        xqid = i['ID']
        print('评教学期：' + i['XNXQMC'])



host = 'https://ugsqs.whu.edu.cn/getXspjrwfa'
receive = requests.post(host, headers=headers, data=data)
info = json.loads(receive.text)['info']
for task in info:
    host = 'https://ugsqs.whu.edu.cn/getStudentPjPf/55/2302000/SCHOOL_ADMIN'
    headers = {
        'Referer': 'https://ugsqs.whu.edu.cn/new/student/rank/evaluate2.jsp',
        'cookie': cookie
    }
    data = {
        'sEcho': 1,
        'iColumns': 6,
        'mDataProp_0': 'KCMC',
        'mDataProp_1': 'XM',
        'mDataProp_2': 'TJSJ',
        'mDataProp_3': 'YZ',
        'mDataProp_4': 'PJJGID',
        'iDisplayStart': 0,
        'iDisplayLength': 50,
    }
    receive = requests.post(host, headers=headers, data=data)
    info = json.loads(receive.text)['aaData']
    for course in info:
        print('课程名称：' + course['KCMC'] + '\t教师：' + course['XM'])
        if course['PJJGID'] is None:
            # print(course['KCMC'])

            # str(task['ZBTX'])
            host = 'https://ugsqs.whu.edu.cn/getTxId'
            data = {
                'kclx': course['KCLX'],
                'zbtx': task['ZBTX']
            }
            receive = requests.post(host, headers=headers, data=data)
            # print(data)
            # print(receive.text)
            id = json.loads(receive.text)['info'][0]['ID']
            print(id)
            host = 'https://ugsqs.whu.edu.cn/tixizhibiaolist'
            data = {
                'tiid': id
            }
            receive = requests.post(host, headers=headers, data=data)
            index = json.loads(receive.text)['info']['zbList']
            dxid = []
            dxvalue = []
            sfjft = []
            wdid = []
            wdvalue = []
            for i in index:
                sfjft.append(('sfjft', i['sfjft']))
                if i['zbtx'] == '问答题':
                    wdid.append(('wdid', i['id']))
                    wdvalue.append(('wdvalue', '无'))
                elif i['zbtx'] == '限制性问答题':
                    wdid.append(('wdid', i['id']))
                    wdvalue.append(('wdvalue', 0))
                elif i['zbtx'] == '单选题':
                    dxid.append(('dxid', i['id']))
                    dxvalue.append(('dxvalue', i['zbfz']))
                    # i['id']
                    # i['xxList']['zbxxfz']
            data = dxid + dxvalue + sfjft + wdid + wdvalue
            data.append(('rwid', task['ID']))
            data.append(('xqid', xqid))
            data.append(('jsgh', course['GH']))
            data.append(('kch', course['KCH']))
            data.append(('bzxh', course['BZXH']))
            data.append(('jxbdm', course['JXBDM']))
            data.append(('xsxh', xsxh))
            data.append(('zf', score))
            data.append(('pjjgjd', ''))
            host = 'https://ugsqs.whu.edu.cn/createStudentPjpf'
            # print(data)
            re = requests.post(host, headers=headers, data=data)
            # print(re.text)
            time.sleep(delay_time)
            print("评教完成！")
        else:
            print('已进行过评教，跳过！')
            time.sleep(0.1)
    print('评教完成！')

os.system("pause")
