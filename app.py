import os
import xlrd
from flask import Flask,request,url_for,redirect,render_template,session
from flask_paginate import Pagination, get_page_parameter
from xlutils.copy import copy
import random
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(30)

@app.route('/', methods=['GET', 'POST'])
def index():
    session.permanent = True
    session.modified = True
    if request.method == 'POST':
        session['examtype'] = request.form['examtype']
        session['order'] = int(request.form['order'])
        if request.form['startnum'] == u'全部' :
            session['startnum'] = 10000
        else:
            session['startnum'] = int(request.form['startnum'])
            session['endnum'] = int(request.form['endnum'])

        return redirect(url_for('exam'))
    return render_template('index.html')

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    examtype = int(session['examtype'])
    page = int(request.args.get('page', 1))
    value: str = request.args.get('value', '')
    order = session['order']
    data_list = []
    if order == 3:
        data_list = getdatafromexcel(examtype, session['startnum'], session['endnum'], order, 2)
        writedataexcel(examtype, data_list[page - 2][0], 4, value)
    if order == 4:
        data_list = getdatafromexcel(examtype, session['startnum'], session['endnum'], 3, 3)
        writedataexcel(examtype, data_list[page - 2][0], 4, value)

    if order < 3:
        data_list = getdatafromexcel(examtype, session['startnum'], session['endnum'],order, 1)
        session.modified = True
        order = 3
        session['order'] = order
    flag = 0
    resultstr = ''
    if value == '':
        flag = 0
    else:
        if data_list[page - 2][2] != value:
            flag = 1
            if 'A' in data_list[page - 2][2]:
                resultstr += data_list[page - 2][6]
            if 'B' in data_list[page - 2][2]:
                resultstr += data_list[page - 2][7]
            if 'C' in data_list[page - 2][2]:
                resultstr += data_list[page - 2][8]
            if 'D' in data_list[page - 2][2]:
                resultstr += data_list[page - 2][9]

    paginate = Pagination(bs_version=6, page=page, per_page=1, total=len(data_list), error_out=False)
    return render_template('exam.html',pagination=paginate, data=data_list[page-1], flag=flag, result=data_list[page - 2][2], resultstr=resultstr)

@app.route('/result')
def result():
    total = len(getdatafromexcel(int(session['examtype']), session['startnum'], session['endnum'], 3, 2))
    result = len(getdatafromexcel(int(session['examtype']), session['startnum'], session['endnum'], 3, 3))
    session.modified = True
    order = 4
    session['order'] = order
    return render_template('result.html',total=total, result=total-result)

#读取excel文件
def getdatafromexcel(examtype, num, endnum, order, flag):
    data = []
    excelname = 'static/dangous_oil.xls'
    sheetid = 0
    if examtype == 1:
        excelname = 'static/dangous_oil.xls'
        sheetid = 0
    if examtype == 2:
        excelname = 'static/new_oil_data.xls'
        sheetid = 0
    if examtype == 3:
        excelname = 'static/new_oil_data.xls'
        sheetid = 1
    if examtype == 4:
        excelname = 'static/new_oil_data.xls'
        sheetid = 2
    if examtype == 5:
        excelname = 'static/new_oil_data.xls'
        sheetid = 3

    if flag == 1:
        wb = xlrd.open_workbook(excelname)
        sheet = wb.sheet_by_index(sheetid)
        wbcopy = copy(wb)
        sheetcopy = wbcopy.get_sheet(sheetid)
        # 从第1行开始遍历循环所有行，获取每行的数据
        nrows = sheet.nrows
        for i in range(1, nrows):
            row_data = sheet.row_values(i)
            # 组建每一行数据的字典
            sheetcopy.write(i,3, '')
            sheetcopy.write(i,4, '')
            sheetcopy.write(i,5, '')
            # 遍历行数据的每一项，赋值进行数据字典
            data.append(row_data)
        if num > len(data):
            num = 0
        if endnum > len(data):
            endnum = len(data)
        if order == 2:
            data = random.sample(data,endnum - num)
            data.sort(key=lambda x:x[0])
        else:
            data = data[num:endnum]
        for i in range(0, endnum - num):
            sheetcopy.write(data[i][0],3, 'Z')
        wbcopy.save(excelname)
        return data
    if flag == 2:
        wb = xlrd.open_workbook(excelname)
        sheet = wb.sheet_by_index(sheetid)
        # 从第1行开始遍历循环所有行，获取每行的数据
        nrows = sheet.nrows
        for i in range(1, nrows):
            if sheet.cell_value(i, 3) != 'Z':
                continue
            row_data = sheet.row_values(i)
            # 组建每一行数据的字典
            data.append(row_data)
           
        return data
    if flag == 3:
        wb = xlrd.open_workbook(excelname)
        sheet = wb.sheet_by_index(sheetid)
        # 从第1行开始遍历循环所有行，获取每行的数据
        nrows = sheet.nrows
        for i in range(1, nrows):
            if sheet.cell_value(i, 3) != 'Z':
                continue
            if sheet.cell_value(i, 2) == sheet.cell_value(i, 4):
                continue
            row_data = sheet.row_values(i)
            data.append(row_data)
        return data
#读取excel文件
def writedataexcel(examtype, row, col, value):
    if examtype == 1:
        wb = xlrd.open_workbook(r'static/dangous_oil.xls')
        wbcopy = copy(wb)
        sheetcopy = wbcopy.get_sheet(0)
        sheetcopy.write(row, col, value)
        wbcopy.save(r'static/dangous_oil.xls')
    if examtype == 2:
        wb = xlrd.open_workbook(r'static/new_oil_data.xls')
        wbcopy = copy(wb)
        sheetcopy = wbcopy.get_sheet(0)
        sheetcopy.write(row, col, value)
        wbcopy.save(r'static/new_oil_data.xls')
    if examtype == 3:
        wb = xlrd.open_workbook(r'static/new_oil_data.xls')
        wbcopy = copy(wb)
        sheetcopy = wbcopy.get_sheet(1)
        sheetcopy.write(row, col, value)
        wbcopy.save(r'static/new_oil_data.xls')
    if examtype == 4:
        wb = xlrd.open_workbook(r'static/new_oil_data.xls')
        wbcopy = copy(wb)
        sheetcopy = wbcopy.get_sheet(2)
        sheetcopy.write(row, col, value)
        wbcopy.save(r'static/new_oil_data.xls')
    if examtype == 5:
        wb = xlrd.open_workbook(r'static/new_oil_data.xls')
        wbcopy = copy(wb)
        sheetcopy = wbcopy.get_sheet(3)
        sheetcopy.write(row, col, value)
        wbcopy.save(r'static/new_oil_data.xls')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
