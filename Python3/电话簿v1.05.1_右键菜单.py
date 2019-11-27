# TIPS
# 信息展示位
# 状态栏/菜单栏/标题行/气泡/右键菜单

import os
import time
import shutil
import hashlib
import subprocess
from threading import Thread

import tkinter
import tkinter.filedialog
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText

try:
    import QR
except:
    QR = False
import Image
import xpinyin

P = xpinyin.Pinyin()

DATA_FOLDER = 'user'
USER_TXT = DATA_FOLDER + '/!CUSTOMIZE.txt'

def bonus():
    if os.path.exists('.crack') and QR:
        print('Bingo!')
        qr_top = QR.myPanel()
        qr_top.mainloop()
    else:
        tkinter.messagebox.showinfo('提示', '未完成的功能')

def md5(file):
    with open(file, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def openFile(file):
    # print('Load:', file)
    if not os.path.exists(file):
        # print('None:', file)
        return ['']
    try:
        with open(file, 'r') as f:
            s = f.read().split('\n')
    except:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                s = f.read().split('\n')
        except Exception as e:
            print('Fail to read:', file, e)
            s = ['']
    return s

def ImportFiles(paths=None):
    if not paths:
        paths = tkinter.filedialog.askopenfilenames(filetypes = [('文本文档', '*.txt *.csv')],
                                                    initialdir = '/') # TODO 第二次打开改变路径
    if paths:
        for path in paths:
            root, file = os.path.split(path)
            path2 = '%s/%s'%(DATA_FOLDER, file)
            if not os.path.exists(path2):
                shutil.copyfile(path, path2)
            else:
                path2 = tkinter.filedialog.asksaveasfilename(filetypes = [('文本文档', '*.txt *.csv')],
                                                             defaultextension = '.txt',
                                                             initialdir = DATA_FOLDER,
                                                             initialfile = file)
                shutil.copyfile(path, path2)
        readContacts2()
        print('ImportFiles: \n    %s'%'\n    '.join(paths))

def UpdateFile():
    if not os.path.exists(USER_TXT):
        with open(USER_TXT, 'w') as f:
            pass

    def th():
        subprocess.call('notepad %s/%s'%(os.getcwd(), USER_TXT)) # 不显示命令行窗口但进程会阻塞(这样才能在随后更新通讯表)
        print('UpdateFile')
        readContacts2()

    t1 = Thread(target=th)
    t1.start()
    return t1

def readContacts():
    t = time.time()
    os.makedirs(DATA_FOLDER, exist_ok=True)
    ss = []
    file_list = []
    for file in os.listdir(DATA_FOLDER):
        if file[-4:] in ['.txt', '.csv']:
            ss += openFile(DATA_FOLDER+'/'+file)
            file_list.append([len(ss), file])
    ss2 = []
    for line in ss:
        ss2.append([line, line.lower()]) # 没有lower()将导致无法匹配大写英文和中文混写的关键词, 因为keys会自动转为小写, 而中英混写导致无法匹配拼音索引, readContacts2处同理
    print('readContacts:', time.time()-t)
    return ss2, file_list

def readContacts2():
    def th():
        t = time.time()
        os.makedirs(DATA_FOLDER, exist_ok=True)
        os.makedirs(DATA_FOLDER+'/tmp', exist_ok=True)
        ss2 = []
        file_list.clear()
        for file in os.listdir(DATA_FOLDER):
            if file[-4:] in ['.txt', '.csv']:
                ss2 += makeIndex('%s/%s'%(DATA_FOLDER, file), '%s/tmp/%s.pinyin'%(DATA_FOLDER, file))
                file_list.append([len(ss2), file])
        global ss
        ss = ss2
        top.onKeyRelease()
        print('makeIndex:', time.time()-t)
        return ss2

    # readContacts2函数永远在后台运行
    t1 = Thread(target=th)
    t1.start()
    return t1

def makeIndex(path1, path2):
    ss1 = openFile(path1)
    ss2 = openFile(path2)
    md5_path1 = md5(path1)
    if md5_path1 != ss2[0]:
        ss2 = []
        for line in ss1:
            ss2.append(',' + P.get_pinyin(line,'').lower() + ',' + P.get_initials(line,'').lower()) # 全拼做lower()处理是为了转换某些文本中带有大写英文的内容，如'Q太郎'
        s2 = md5_path1 + '\n' + '\n'.join(ss2)
        try:
            with open(path2, 'w', encoding='utf-8') as f: # encoding='utf-8'为了写入无法转换为拼音的字符''
                f.write(s2)
        except Exception as e:
            print('Fail to write:', path2, e)
    else:
        ss2 = ss2[1:]
    ss = []
    for i in range(len(ss1)):
        ss.append([ss1[i], ss1[i].lower() + ss2[i]]) # 没有lower()将导致无法匹配大写英文和中文混写的关键词, 如:Q太郎
    return ss

def setCenter(top):
    top.update_idletasks()
    x = (top.winfo_screenwidth()  - top.winfo_reqwidth())  / 2
    y = (top.winfo_screenheight() - top.winfo_reqheight()) / 2
    top.geometry('+%d+%d'%(x, y))

class myPanel(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self, 'lsx')
        self.withdraw() # 先withdraw隐藏再deiconify显示可使setCenter不会导致页面闪烁

        self.title('电话簿v1.05 （联系作者：QQ11313213）') # TODO 是否有用

        self.keys_var = tkinter.StringVar()
        self.tex1 = ScrolledText(self)
        ent1 = tkinter.Entry(self, textvariable=self.keys_var, width=125)
        ent1     .pack(padx=2, pady=2, fill=tkinter.constants.BOTH, side=tkinter.constants.TOP)
        self.tex1.pack(padx=2, pady=2, fill=tkinter.constants.BOTH, expand=True)

        self.menu = tkinter.Menu(self, tearoff=0)
        self.menu.add_command(label='复制', command=self.copyItem)
        self.menu.add_separator()
        self.menu.add_command(label='来源')
        self.menu.add_separator()
        self.menu.add_command(label='刷新', command=readContacts2)
        self.menu.add_command(label='前后文', command=self.location)
        self.menu.add_separator()
        self.menu.add_command(label='导入文件', command=ImportFiles)
        self.menu.add_command(label='新增和更改', command=UpdateFile)

        self.menu0 = tkinter.Menu(self, tearoff=0)
        self.menu0.add_command(label='刷新', command=readContacts2)
        self.menu0.add_separator()
        self.menu0.add_command(label='导入文件', command=ImportFiles)
        self.menu0.add_command(label='新增和更改', command=UpdateFile)
        self.menu0.add_separator()

        submenu = [tkinter.Menu(self, tearoff=0)]
        self.menu0.add_cascade(label='Designed by Lsx. ', menu=submenu[0])

        for key, value in [['Name', 'Li Shixian'], ['Mail', 'lsx7@sina.com'], ['Website', 'github.com/znsoooo/contacts'], ['Wechat', 'Xian_2'], ['Donate', 'xxxx']]:
            submenu.append(tkinter.Menu(self, tearoff=0))
            submenu.append(tkinter.Menu(self, tearoff=0))
            submenu[-1].add_command(label=value)
            submenu[ 0].add_cascade(label=key, menu=submenu[-1])
        self.img_wechat = tkinter.PhotoImage(data=Image.img1) # 没有self会导致显示图片为空白
        self.img_donate = tkinter.PhotoImage(data=Image.img2)
        submenu[8] .entryconfig(0, image=self.img_wechat)
        submenu[10].entryconfig(0, image=self.img_donate)
        submenu[0].add_separator()
        submenu[0].add_command(label='All Rights Reserved.', command=bonus)

        setCenter(self)
        self.deiconify()

        ent1.focus()
        ent1.bind('<KeyRelease>', self.onKeyRelease)
        self.tex1.bind('<ButtonRelease-3>', self.onRightClick)


    def select(self, row):
        self.tex1.mark_set('insert', '%d.0'%row)
        self.tex1.tag_remove('sel', '0.0', 'end')
        self.tex1.tag_add('sel', '%d.0'%row, '%d.0'%(row+1))        

    def location(self, row=0):
        if not row:
            row = self.current_index + 1
        self.onKeyRelease(keys='')
        self.select(row)
        self.tex1.see('%d.0'%row)

    def copyItem(self):
        text = self.tex1.selection_get()
        self.clipboard_clear()
        self.clipboard_append(text[:-1]) # 去掉文末换行符

    def onRightClick(self, evt=0):
        self.tex1.focus() # 当焦点在ent1中时
        self.current = int(self.tex1.index('current').split('.')[0])
        if len(self.index):
            self.current_index = self.index[self.current - 1]

            line_last = 0
            for line, file in file_list:
                if line > self.current_index:
                    break
                else:
                    line_last = line
            self.menu.entryconfig(2, label='来源: %s (line:%s)'%(file, self.current_index - line_last + 1))
            self.menu.entryconfig(2, command=lambda: os.popen('explorer /select, %s\\%s\\%s'%(os.getcwd(), DATA_FOLDER, file)))

            self.select(self.current)
            self.menu.post(evt.x_root, evt.y_root)
        else:
            self.menu0.post(evt.x_root, evt.y_root)

        return self.current

    def onKeyRelease(self, evt=0, keys=None):
        if keys is None:
            keys = self.keys_var.get()
        keys = keys.lower().split(' ')
        ss_new = []
        self.index = []
        for n, s in enumerate(ss):
            ok = True
            for key in keys:
                if key not in s[1]:
                    ok = False
            if ok:
                ss_new.append(s[0])
                self.index.append(n) # TODO 提出搜索部分到独立的函数

        self.tex1.config(state='normal')
        self.tex1.delete('1.0', 'end')
        self.tex1.insert('1.0', '\n'.join(ss_new))
        self.tex1.config(state='disabled') # 禁止编辑
        self.title('电话簿v1.05 （联系作者：QQ11313213） - %s结果'%len(ss_new)) # title更改耗时短可以做到'同时'更改的效果

        return ss_new


if __name__ == '__main__':
    ss = []
    ss, file_list = readContacts()

    top = myPanel()
    readContacts2() # 后台线程运行速度极快(如contact文件夹为空)时可能在top参数生成前就需要使用该参数
    top.onKeyRelease()
    top.mainloop()

