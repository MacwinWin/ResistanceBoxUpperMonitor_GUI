#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
self.lineEdit_list中存放所有24个lineEdit对象
self.argus中存放所有24个参数
self.argus只在导入导出参数时调用
self.button_list中存放所有控制按钮对象
'''

import sys
import traceback
import os
from json import dump, load
import time
from PyQt5.QtWidgets import QMainWindow,QApplication,QMessageBox,QFileDialog
from PyQt5.QtGui import QDoubleValidator,QIntValidator,QIcon 
from PyQt5.QtCore import QRegExp, QTimer
from module.ui import * 
import serial
#from cli_backend import *

class MyForm(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.argus = {}
        self.flag = True 
        self.cwd = os.getcwd()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.createList()
        self.create_folder()
        self.initBox()
        self.read_file()
        self.ui.open_Button.clicked.connect(self.initPort)
        self.ui.close_Button.clicked.connect(self.closePort)
        self.ui.modeOpen_radioButton.toggled.connect(self.mode_select)
        self.ui.modeOnl_radioButton.toggled.connect(self.mode_select)
        self.ui.modeShor_radioButton.toggled.connect(self.mode_select)
        self.ui.fixed_radioButton.toggled.connect(self.change_grey)
        self.ui.linear_radioButton.toggled.connect(self.change_grey)
        self.ui.nonlinear_radioButton.toggled.connect(self.change_grey)
        self.ui.ohm_checkBox.stateChanged.connect(self.change_kohm)
        self.ui.lcdNumber.setSmallDecimalPoint(True)
        self.ui.run_Button.clicked.connect(self.run)
        self.ui.stop_Button.clicked.connect(self.stop_run)
        self.ui.pause_Button.clicked.connect(self.pause_run)
        self.ui.file_Box.currentIndexChanged.connect(self.read_file)
#        self.ui.read_Button.clicked.connect(self.read_file)
        self.ui.write_Button.clicked.connect(self.write_file)
        self.ui.create_Button.clicked.connect(self.create_argus)

    def createList(self):
        self.lineEdit_list = []
        self.lineEdit_list.append(self.ui.lineEdit_0)
        self.lineEdit_list.append(self.ui.lineEdit_1)
        self.lineEdit_list.append(self.ui.lineEdit_2)
        self.lineEdit_list.append(self.ui.lineEdit_3)
        self.lineEdit_list.append(self.ui.lineEdit_4)
        self.lineEdit_list.append(self.ui.lineEdit_5)
        self.lineEdit_list.append(self.ui.lineEdit_6)
        self.lineEdit_list.append(self.ui.lineEdit_7)
        self.lineEdit_list.append(self.ui.lineEdit_8)
        self.lineEdit_list.append(self.ui.lineEdit_9)
        self.lineEdit_list.append(self.ui.lineEdit_10)
        self.lineEdit_list.append(self.ui.lineEdit_11)
        self.lineEdit_list.append(self.ui.lineEdit_12)
        self.lineEdit_list.append(self.ui.lineEdit_13)
        self.lineEdit_list.append(self.ui.lineEdit_14)
        self.lineEdit_list.append(self.ui.lineEdit_15)
        self.lineEdit_list.append(self.ui.lineEdit_16)
        self.lineEdit_list.append(self.ui.lineEdit_17)
        self.lineEdit_list.append(self.ui.lineEdit_18)
        self.lineEdit_list.append(self.ui.lineEdit_19)
        self.lineEdit_list.append(self.ui.lineEdit_20)
        self.lineEdit_list.append(self.ui.lineEdit_21)
        self.lineEdit_list.append(self.ui.lineEdit_22)
        self.lineEdit_list.append(self.ui.lineEdit_23)
        # 将lineEdit限制为仅接受浮点数输入
        for i in range(0,24):
            self.lineEdit_list[i].setValidator(QDoubleValidator())
        self.ui.lineEdit_2.setValidator(QIntValidator())
        self.button_list = []
        self.button_list.append(self.ui.open_Button)
        self.button_list.append(self.ui.close_Button)
        self.button_list.append(self.ui.modeOnl_radioButton)
        self.button_list.append(self.ui.modeOpen_radioButton)
        self.button_list.append(self.ui.modeShor_radioButton)
        self.button_list.append(self.ui.fixed_radioButton)
        self.button_list.append(self.ui.linear_radioButton)
        self.button_list.append(self.ui.nonlinear_radioButton)
        self.button_list.append(self.ui.ohm_checkBox)
#        self.button_list.append(self.ui.read_Button)
        self.button_list.append(self.ui.write_Button)
        self.button_list.append(self.ui.create_Button)
        self.button_list.append(self.ui.port_Box)
        self.button_list.append(self.ui.baudRate_Box)
        self.button_list.append(self.ui.file_Box)
    
    def initPort(self):
        self.ui.open_Button.setChecked(False)
        portName = self.ui.port_Box.currentText()  # str  "COM8"
        bandRate = int(self.ui.baudRate_Box.currentText())  # int    9600
        try:
            self.ser = serial.Serial(portName)  # 设置串口号
            self.ser.baudrate = bandRate  # 设置波特率
            if self.ser.is_open:
                self.opened = True
                self.change_grey1()
            print('port opened')
            print(self.ser)
            return 
        except:
           # traceback.print_exc()
            QMessageBox.warning(None, '串口', "串口无效或串口被占用或已开启", QMessageBox.Ok)
            return
    
    def initBox(self):
        self.ui.file_Box.clear()
        os.chdir(self.path)
        self.names = filter(os.path.isfile, os.listdir(self.path))
        self.names = [os.path.join(self.path, f) for f in self.names] # add path to each file
        self.names.sort(key=lambda x: os.path.getmtime(x))
        # [::-1]为倒序排列
        for self.name in self.names[::-1]:
            self.name = os.path.basename(self.name)
            self.ui.file_Box.addItem(self.name)

    def mode_select(self):
        if self.ui.modeOpen_radioButton.isChecked():
            try:
                self.ser.write('OUTP:STAT OPEN\n'.encode())
            except:
                if self.flag:
                    QMessageBox.information(None, '串口', '请开启串口', QMessageBox.Ok)    
                    # 由于radio按钮状态的变化一直是成对出现,因而会造成提示框出现两次的情况,通过设置flag来避免重复弹出提示框
                    self.flag = False                
                else:
                    self.flag = True 
                    return
        elif self.ui.modeOnl_radioButton.isChecked():
            try:
                self.ser.write('OUTP:STAT ONL\n'.encode())
            except:
                if self.flag:
                    QMessageBox.information(None, '串口', '请开启串口', QMessageBox.Ok)
                    self.flag = False
                else:
                    self.flag = True
                    return
        elif self.ui.modeShor_radioButton.isChecked():
            try:
                self.ser.write('OUTP:STAT SHOR\n'.encode())
            except:
                if self.flag:
                    QMessageBox.information(None, '串口', '请开启串口', QMessageBox.Ok)
                    self.flag = False
                else:
                    self.flag = True
                    return

    def change_kohm(self):
        if self.ui.ohm_checkBox.isChecked():
            self.ui.label_5.setText('初始阻值(KΩ)')
            self.ui.label_6.setText('变化数值(KΩ)')
            self.ui.ohm_label_6.setText('KΩ')
        else:
            self.ui.label_5.setText('初始阻值(Ω)')
            self.ui.label_6.setText('变化数值(Ω)')
            self.ui.ohm_label_6.setText('Ω')
            
    def run(self):
        self.count = 0
        try:
            # 非线性变化
            if self.ui.nonlinear_radioButton.isChecked():
                if not self.ui.pause_Button.isEnabled() and self.ui.stop_Button.isEnabled():
                    print('resumed')
                    self.time = QTimer()
                    self.time.setInterval(float(self.lineEdit_list[3].text())*1000)
                    self.count = self.pause_count
                    self.time.start()
                    self.time.timeout.connect(self.refresh)
                else:
                    self.time = QTimer()
                    self.time.setInterval(float(self.lineEdit_list[3].text())*1000)
                    self.time.setSingleShot(False)
                    self.time.timeout.connect(self.refresh)
                    self.time.start()
                # 设置运行过程中开始暂停停止按钮状态
                self.ui.pause_Button.setEnabled(True)
                self.ui.stop_Button.setEnabled(True)
                self.ui.run_Button.setEnabled(False)
                self.runtime_grey(True)
            else:
                self.output_res = float(self.lineEdit_list[0].text())
                try:
                    # 固定阻值
                    self.Kohm_check()
                    self.ser.write(self.output.encode())
                    self.lcdNumber()
                except:
                    QMessageBox.information(None, '串口', "请开启串口", QMessageBox.Ok)
                    return
                # 线性变化
                if self.ui.linear_radioButton.isChecked():
                    self.time = QTimer()
                    self.time.setInterval(float(self.lineEdit_list[3].text())*1000)
                    self.time.setSingleShot(False)
                    self.time.timeout.connect(self.refresh)
                    self.time.start()
                    # 设置运行过程中开始暂停停止按钮状态
                    self.ui.pause_Button.setEnabled(True)
                    self.ui.stop_Button.setEnabled(True)
                    self.ui.run_Button.setEnabled(False)
                    self.runtime_grey(True)
        except AttributeError:
            traceback.print_exc()
            QMessageBox.information(None, '串口', "请开启串口", QMessageBox.Ok)
            print('there')
        except ValueError:
            traceback.print_exc()
            QMessageBox.information(None, '参数', "参数设置不完整", QMessageBox.Ok)

    def Kohm_check(self):
        if self.ui.ohm_checkBox.isChecked():
            self.output = 'OUTP:RES {}'.format(self.output_res) + 'K' + '\n'
        else:
            self.output = 'OUTP:RES {}'.format(self.output_res) + '\n'

    def refresh(self):
        if self.ui.linear_radioButton.isChecked():
            if self.count == int(self.lineEdit_list[2].text()):
                print('stop')
                self.stop_run()
                return
            self.output_res = self.output_res + float(self.lineEdit_list[1].text())
            self.Kohm_check()
            self.ser.write(self.output.encode())
            self.lcdNumber()
            self.count += 1
        else:
            # 跳过list中的前4个参数
            if self.lineEdit_list[self.count+4].text() == '':
                print('stop')
                self.stop_run()
                return
            self.output_res = float(self.lineEdit_list[self.count+4].text())
           # print('count:{}'.format(self.count))
            self.Kohm_check()
            try:
                self.ser.write(self.output.encode())
            except:
                QMessageBox.information(None, '串口', "请开启串口", QMessageBox.Ok)
                self.stop_run()
            self.lcdNumber()
            # 动态变化过程进度
            self.lineEdit_list[self.count+3].setEnabled(False)
            self.lineEdit_list[self.count+4].setEnabled(True)
            self.count += 1
            if self.count == 20:
                print('stop')
                self.stop_run()
                return

    def stop_run(self):
        try:
            self.time.stop()
            self.time = None
            self.ui.run_Button.setEnabled(True)
            self.ui.pause_Button.setEnabled(False)
            self.ui.stop_Button.setEnabled(False)
            self.runtime_grey(False)
            self.change_grey()
        except AttributeError:
            return
    
    def pause_run(self):
        try:
            print('paused')
            self.pause_count = self.count
            self.time.stop()
            self.ui.run_Button.setEnabled(True)
            self.ui.pause_Button.setEnabled(False)
            self.ui.stop_Button.setEnabled(True)
        except AttributeError:
            return

    def lcdNumber(self):
        self.ui.lcdNumber.display(self.output_res)

    def closePort(self):
        self.stop_run()
        try:
            self.ser.close()
            #QMessageBox.warning(None, '端口', '端口已关闭', QMessageBox.Ok)
            if not self.ser.is_open:
                self.opened = False
                self.change_grey1()
            print('port closed')
        except:
            return
            
    def create_folder(self):
        self.path = self.cwd+'/电阻箱参数'
        folder = os.path.exists(self.path)
        if not folder:
            os.mkdir(self.path)
            print('folder created: {}'.format(self.path))
        else:
            print('folder existed')

    def read_file(self):
        fileName_choose = self.path + '/' + self.ui.file_Box.currentText()
        try:
            with open(fileName_choose, 'r') as infile:
                self.argus = load(infile)
        except:
            print('not existed')
            return
        try:
            for i in range(0,24):
                if self.argus[self.lineEdit_list[i].objectName()] == '':
                    self.lineEdit_list[i].setText('')
                else:
                    self.lineEdit_list[i].setText(str(self.argus[self.lineEdit_list[i].objectName()]))
        except:
            QMessageBox.information(None, '参数', "参数读取有误,请查看文件参数", QMessageBox.Ok)

    def write_file(self):
        for i in range(0,24):
            if self.lineEdit_list[i].text() != '':
                if i == 2:
                    self.argus[self.lineEdit_list[i].objectName()] = int(self.lineEdit_list[i].text())
                else:
                    self.argus[self.lineEdit_list[i].objectName()] = float(self.lineEdit_list[i].text())
            else:
                self.argus[self.lineEdit_list[i].objectName()] = self.lineEdit_list[i].text()
        fileName_choose, filetype = QFileDialog.getSaveFileName(self,  
                            "文件保存",  
                            self.path, # 起始路径 
                            "All Files (*);;json Files (*.json)")
        
        if fileName_choose == "":
            return
        else:
            with open(fileName_choose,'w') as outfile:
                dump(self.argus, outfile, ensure_ascii = False)
                outfile.write('\n')
                self.initBox()

    def create_argus(self):
        for i in range(0,24):
            self.lineEdit_list[i].setText('')

    def change_grey(self):
        if self.ui.fixed_radioButton.isChecked(): 
            self.lineEdit_list[0].setEnabled(True)
            self.lineEdit_list[1].setEnabled(False)
            self.lineEdit_list[2].setEnabled(False)
            self.lineEdit_list[3].setEnabled(False)
            for item in range(4,24):
                self.lineEdit_list[item].setEnabled(False)
        elif self.ui.linear_radioButton.isChecked():
            self.lineEdit_list[0].setEnabled(True)
            self.lineEdit_list[1].setEnabled(True)
            self.lineEdit_list[2].setEnabled(True)
            self.lineEdit_list[3].setEnabled(True)
            for item in range(4,24):
                self.lineEdit_list[item].setEnabled(False)
        elif self.ui.nonlinear_radioButton.isChecked():
            self.lineEdit_list[0].setEnabled(False)
            self.lineEdit_list[1].setEnabled(False)
            self.lineEdit_list[2].setEnabled(False)
            self.lineEdit_list[3].setEnabled(True)
            for item in range(4,24):
                self.lineEdit_list[item].setEnabled(True)

    def change_grey1(self):
        if self.opened:
            self.runtime_grey(False)
            self.ui.open_Button.setEnabled(False)
            self.ui.close_Button.setEnabled(True)
            self.change_grey()
            self.ui.run_Button.setEnabled(True)
        else:
            self.runtime_grey(True)
            self.ui.run_Button.setEnabled(False)
            self.ui.open_Button.setEnabled(True)
            self.ui.close_Button.setEnabled(False)

    def runtime_grey(self,flag):
        if flag:
            for i in range(0,14):
                self.button_list[i].setEnabled(False)
            for i in range(0,24):
                self.lineEdit_list[i].setEnabled(False)
        else:
            for i in range(0,14):
                self.button_list[i].setEnabled(True)
                self.ui.open_Button.setEnabled(False)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    w = MyForm()
    # 由于120行处更改了工作目录,因而需要返回上一级寻找
    app.setWindowIcon(QIcon("../icon/icon.jpg"))
    w.show()
    sys.exit(app.exec_())

