import requests
import json
import time

# Cookie
JSESSIONID = ''
insert_cookie = ''
iPlanetDirectoryPro = ''
# 每隔多久完成一门课的评价（单位：秒）
delay_time = 10
# 每门多少分
score = 100.0

cookie = 'iPlanetDirectoryPro=' + iPlanetDirectoryPro + ';JSESSIONID=' + JSESSIONID + ';insert_cookie=' + insert_cookie + ';'
host = 'https://ugsqs.whu.edu.cn/getxnxqList'
headers = {
    'content-type': 'application/json',
    'cookie': cookie
}
data = {}
receive = requests.post(host, headers=headers, data=data)
info = json.loads(receive.text)
xqid = ''
for i in info:
    if i['SFDQXQ'] == '是':
        xqid = i['ID']

host = 'https://ugsqs.whu.edu.cn/jslist'
receive = requests.post(host, headers=headers, data=data)
xsxh = json.loads(receive.text)['list'][0]['USERID']

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
        if course['PJJGID'] is None:
            print(course['KCMC'])

            str(task['ZBTX'])
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
            print("OK")
