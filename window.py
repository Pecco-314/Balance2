#coding=gbk
'''
@author: Pecco
'''

import wx
import random
import balance

def dialog(string):
    box=wx.Dialog(None,title="错误",size=(200,75))
    wx.StaticText(box,label=string)
    box.Show(True)
class Frame(wx.Frame):
    def __init__(self,*args,**kw):
        super().__init__(*args,**kw)
        self.initUI()
    def initUI(self):
        self.SetTitle("化学方程式配平器V1.22 - Creadted by Pecco")
        self.SetSize(564,100)
        self.panel=wx.Panel(self)
        self.textctrl=wx.TextCtrl(self.panel,size=(400,25),pos=(12,19),value=random.choice(balance.EXAMPLES))
        self.button=wx.Button(self.panel,label="配平",size=(60,30),pos=(417,16))
        self.button.Bind(wx.EVT_BUTTON,self.balance)
        self.button2=wx.Button(self.panel,label="示例",size=(60,30),pos=(480,16))
        self.button2.Bind(wx.EVT_BUTTON,self.newExample)
    def balance(self,event):
        string=balance.balance(self.textctrl.GetValue())
        if string[0]=="错":dialog(string)
        else:
            self.textctrl.SetValue(string)
            event.Skip()
    def newExample(self,event):
        self.textctrl.SetValue(random.choice(balance.EXAMPLES))
        
app = wx.App()
frame=Frame(None).Show(True)
app.MainLoop()