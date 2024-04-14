import requests
import json
import time
import os
import configparser
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


flag_check = False
courses = []
cookie = ''
task = []
xqid = ''
xsxh = ''


def query():
    course_table.delete(*course_table.get_children())
    JSESSIONID = input_jsessionID.get()
    insert_cookie = input_cookie.get()
    iPlanetDirectoryPro = input_iPlanetDirectoryPro.get()

    # score = float(input('请输入每门课程评价的总分（满分100分）：') or '100.0')
    score = 100.0
    data = {}

    status = 403
    global cookie
    cookie = 'iPlanetDirectoryPro=' + iPlanetDirectoryPro +\
             ';JSESSIONID=' + JSESSIONID +\
             ';insert_cookie=' + insert_cookie + ';'
    headers = {
        'content-type': 'application/json',
        'cookie': cookie
    }
    host = 'https://ugsqs.whu.edu.cn/jslist'
    receive = requests.post(host, headers=headers, data=data)
    status = receive.status_code
    if status == 200:
        global xsxh
        xsxh = json.loads(receive.text)['list'][0]['USERID']
    elif status == 403:
        messagebox.showerror("错误", "参数错误！请重新填写参数！")
        return
    else:
        messagebox.showerror("错误", "未知错误！")
        return

    headers = {
        'content-type': 'application/json',
        'cookie': cookie
    }

    host = 'https://ugsqs.whu.edu.cn/getxnxqList'
    receive = requests.post(host, headers=headers, data=data)
    info = json.loads(receive.text)
    global xqid
    for i in info:
        if i['SFDQXQ'] == '是':
            xqid = i['ID']
            # print('评教学期：' + i['XNXQMC'])

    host = 'https://ugsqs.whu.edu.cn/getXspjrwfa'
    receive = requests.post(host, headers=headers, data=data)
    info = json.loads(receive.text)['info']

    global task
    task = info[0]

    host = 'https://ugsqs.whu.edu.cn/getStudentPjPf/' + str(task['ID']) + '/' + str(task['ORGCODE']) + '/SCHOOL_ADMIN'
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
    global courses
    courses = json.loads(receive.text)['aaData']

    for course in courses:
        if course['PJJGID'] is None:
            course_table.insert("", tk.END, text=len(course_table.get_children()) + 1, values=(course['KCMC'], course['XM'], '未评教'))
        else:
            pass
            course_table.insert("", tk.END, text=len(course_table.get_children()) + 1, values=(course['KCMC'], course['XM'], '已评教'))
    evaluate_progress['maximum'] = len(courses)
    global flag_check
    flag_check = True
    conf.read(config_path, encoding='utf-8')
    conf.set('settings', 'JSESSIONID', JSESSIONID)
    conf.set('settings', 'insert_cookie', insert_cookie)
    conf.set('settings', 'iPlanetDirectoryPro', iPlanetDirectoryPro)
    conf.write(open(config_path, 'w'))


def auto_evaluate():
    if flag_check:
        headers = {
            'Referer': 'https://ugsqs.whu.edu.cn/new/student/rank/evaluate2.jsp',
            'cookie': cookie
        }
        score_index = input_level.get()
        evaluate_progress['value'] = 0
        for course in courses:
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
                # print(id)
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
                        dxvalue.append(('dxvalue', int(i['zbfz']) * int(score_index) / 100))
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
                data.append(('zf', score_index))
                data.append(('pjjgid', ''))
                host = 'https://ugsqs.whu.edu.cn/createStudentPjpf'
                # print(data)
                re = requests.post(host, headers=headers, data=data)
                # print(re.text)

                time.sleep(int(input_delay.get()))
            else:
                time.sleep(0.1)
            evaluate_progress.step(1)
            window.update()
        messagebox.showinfo('完成', '评教已完成！')
        query()
    else:
        messagebox.showerror('错误', '请先获取数据！')


def change_evaluate():
    if flag_check:
        if len(course_table.selection()):
            level = int(5 - int(input_level2.get()) / 20)
            need_change_index = course_table.item(course_table.selection(), 'text') - 1
            global courses
            headers = {
                'Referer': 'https://ugsqs.whu.edu.cn/new/student/rank/evaluate2.jsp',
                'cookie': cookie
            }
            host = 'https://ugsqs.whu.edu.cn/getTxId'
            data = {
                'kclx': courses[need_change_index]['KCLX'],
                'zbtx': task['ZBTX']
            }
            receive = requests.post(host, headers=headers, data=data)
            # print(data)
            # print(receive.text)
            id = json.loads(receive.text)['info'][0]['ID']
            # print(id)
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
            zf = 0.0
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
                    dxvalue.append(('dxvalue', i['xxList'][level]['zbxxfz']))
                    zf += float(i['xxList'][level]['zbxxfz'])
                    # i['id']
                    # i['xxList']['zbxxfz']
            data = dxid + dxvalue + sfjft + wdid + wdvalue
            data.append(('rwid', task['ID']))
            data.append(('xqid', xqid))
            data.append(('jsgh', courses[need_change_index]['GH']))
            data.append(('kch', courses[need_change_index]['KCH']))
            data.append(('bzxh', courses[need_change_index]['BZXH']))
            data.append(('jxbdm', courses[need_change_index]['JXBDM']))
            data.append(('xsxh', xsxh))
            data.append(('zf', zf))
            data.append(('pjjgid', courses[need_change_index]['PJJGID']))
            host = 'https://ugsqs.whu.edu.cn/createStudentPjpf'
            # print(data)
            re = requests.post(host, headers=headers, data=data)
            # print(re.text)
            messagebox.showinfo('完成', '修改完成！')
        else:
            messagebox.showerror('错误', '请先选择课程！')
    else:
        messagebox.showerror('错误', '请先获取数据！')


def new_thread(target):
    if threading.active_count() == 1:
        add_thread = threading.Thread(target=target)
        add_thread.start()
    else:
        messagebox.showerror('错误', '请先等待当前任务完成！')


def query_button_callback():
    new_thread(query)


def auto_evaluate_button_callback():
    new_thread(auto_evaluate)


def change_evaluate_button_callback():
    new_thread(change_evaluate)


if __name__ =='__main__':
    window = tk.Tk()
    window.title('WHU自动评教')
    window_width = 800
    window_height = 600
    window.geometry('%dx%d+%d+%d' % (window_width, window_height,
                                     (window.winfo_screenwidth() - window_width) / 2,
                                     (window.winfo_screenheight() - window_height) / 2))

    label_jsessionID = tk.Label(window, text='JSEESIONID:', width=24)
    label_jsessionID.grid(row=0, column=0)
    input_jsessionID = tk.Entry(window, width=60)
    input_jsessionID.grid(row=0, column=1)

    label_cookie = tk.Label(window, text='insert_cookie:')
    label_cookie.grid(row=1, column=0)
    input_cookie = tk.Entry(window, width=60)
    input_cookie.grid(row=1, column=1)

    label_iPlanetDirectoryPro = tk.Label(window, text='iPlanetDirectoryPro:')
    label_iPlanetDirectoryPro.grid(row=2, column=0)
    input_iPlanetDirectoryPro = tk.Entry(window, width=60)
    input_iPlanetDirectoryPro.grid(row=2, column=1)

    button_check = tk.Button(window, text='查询', width=20, height=3, command=query_button_callback)
    button_check.grid(row=0, column=2, rowspan=3, padx=30, columnspan=2)

    course_table = ttk.Treeview(window, height=24, selectmode='browse')
    course_table.grid(row=3, column=0, columnspan=2, rowspan=24)
    course_table["columns"] = ("Course", "Teacher", "State")
    course_table.heading("#0", text="序号")
    course_table.column("#0", width=60)
    course_table.heading("Course", text="课程")
    course_table.column("Course", width=280)
    course_table.heading("Teacher", text="教师")
    course_table.column("Teacher", width=160)
    course_table.heading("State", text="状态")
    course_table.column("State", width=80)

    label_level = tk.Label(window, text='得分百分比:')
    label_level.grid(row=9, column=2)
    input_level = tk.Spinbox(window, from_=0, to=100, increment=20, width=12)
    input_level.grid(row=9, column=3)

    label_delay = tk.Label(window, text='每门课程完成时间（秒）:')
    label_delay.grid(row=10, column=2, columnspan=2)
    input_delay = tk.Entry(window, width=5)
    input_delay.insert(0, 10)
    input_delay.grid(row=11, column=3)

    button_auto = tk.Button(window, text='自动评教', width=20, height=3, command=auto_evaluate_button_callback)
    button_auto.grid(row=12, column=2, rowspan=3, padx=30, columnspan=2)

    evaluate_progress = ttk.Progressbar(window, length=180)
    evaluate_progress.grid(row=15, column=2, columnspan=2)
    evaluate_progress['maximum'] = 100

    label_level2 = tk.Label(window, text='得分百分比:')
    label_level2.grid(row=22, column=2)
    input_level2 = tk.Spinbox(window, value=(20, 40, 60, 80, 100), width=12)
    input_level2.grid(row=22, column=3)

    button_auto = tk.Button(window, text='修改评价', width=20, height=3, command=change_evaluate_button_callback)
    button_auto.grid(row=24, column=2, rowspan=3, padx=30, columnspan=2)

    conf = configparser.ConfigParser()
    config_path = './config.ini'
    if os.path.exists(config_path):
        conf.read(config_path, encoding='utf-8')
        input_jsessionID.insert(0, conf['settings']['JSESSIONID'])
        input_cookie.insert(0, conf['settings']['insert_cookie'])
        input_iPlanetDirectoryPro.insert(0, conf['settings']['iPlanetDirectoryPro'])
    else:
        conf.add_section('settings')
        conf.add_section('WARNING')
        conf.set('WARNING', 'WARNING', 'Don\'t disclose the contents of this document!')
        conf.set('settings', 'JSESSIONID', '')
        conf.set('settings', 'insert_cookie', '')
        conf.set('settings', 'iPlanetDirectoryPro', '')
        conf.write(open(config_path, 'w'))

    window.resizable(width=False, height=False)
    window.mainloop()
