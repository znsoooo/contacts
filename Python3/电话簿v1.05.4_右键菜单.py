# TIPS
# 信息展示位
# 状态栏/菜单栏/标题行/气泡/右键菜单

# DONE
# 读取子文件夹
# 允许匹配字符串中存在空格 (比如"李 世 先")
# 弹窗提示'新增和更改'的相关说明要求
# 大小写后缀名通配
# 用户自定义文件为user.ini (ini格式避免触发自动标密软件的自动重命名)
# 彩蛋: 作者信息和启动另一个软件
# log.txt记录操作日志，输入框2秒无变化记录log
# 提出version到全局变量

# TODO
# 表格显示
# ent输入默认提示
# 输入框下拉搜索记录(并记录频率和最后时间)
# 多音字识别
# 高亮匹配部分(汉字或字母皆可)

# 恢复热点时刷新
# 更新时的变量逐步变化的问题(file_list)
# 更新时逐步更新ss而不是一次全部赋值的问题(提高多数据时的逐步运行效果)
# 更好的关键词检索机制(而不是穷举)

# 当直接复制的内容中含有\n时

# 更新说明文件txt


# PASS
# 匹配文件名中的关键词
# 直接读取xls(x)和docx
# 右键去除重复
# 命令行启动(窗口或命令行界面/初始启动带参数(关键词/搜索文件/文件夹))
# 导入文件时的文件读取错误提示(见操作日志)



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

__ver__ = 'v1.05.4'

DATA_FOLDER = 'contacts'
TEMP_FOLDER = DATA_FOLDER + '\\tmp\\'
USER_TXT = DATA_FOLDER + '\\user.ini'
HINT_TXT = '''为保证原始通讯录文件的一致性，限制不允许在原表格上更改，请在用户自定义文件中编辑更改后保存关闭，如果需要更改源文件请右键点击查看来源后手动更改。'''
HINT_TXT = '''为保证源文件一致性，请在用户自定义文件上更改。\n如需更改源文件请右键点击查看来源。'''

LOG_FILE = 'log.txt'

P = xpinyin.Pinyin()

os.makedirs(DATA_FOLDER, exist_ok=True)

def pprint(*s):
    print(*s)
    try:
        with open(LOG_FILE, 'a', encoding='u8') as f:
            ss = ' '.join(map(str, s))
            f.write(time.strftime('[%Y-%m-%d %H:%M:%S]: ', time.localtime()) + ss + '\n')
    except Exception as e:
        print('log write error:', e)

def bonus():
    if os.path.exists('.crack') and QR:
        pprint('Bingo!')
        qr_top = QR.myPanel()
        qr_top.mainloop()
    else:
        pprint('Oops!')
        tkinter.messagebox.showinfo('提示', '未完成的功能')

def md5(file):
    with open(file, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def pinyin(s): # 全拼做lower()处理是为了转换某些文本中带有大写英文的内容，如'Q太郎'
    return P.get_pinyin(s, '').lower(), P.get_initials(s, '').lower()

def openFile(file):
    # pprint('Load:', file)
    if not os.path.exists(file):
        # pprint('None:', file)
        return ['']

    with open(file, 'rb') as f:
        s = f.read()
    try:
        ss = s.decode()
    except:
        try:
            ss = s.decode('gbk')
        except Exception as e:
            pprint('Fail to read:', file, e)
            ss = ''
            # ss = re.sub(rb'[\0-\10\13\14\16-\37]+', b' ', s).decode(errors='ignore') # 去除不可见字符
            # ss = s.decode(encoding='gbk', errors='ignore')
            # ss = re.sub(r'[^\U00000000-\U0000FFFF]', '', ss) # 替换 Non-BMP character
    return ss.split('\r\n')

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
        pprint('ImportFiles: \n    %s'%'\n    '.join(paths))

def UpdateFile():
    if not os.path.exists(USER_TXT):
        with open(USER_TXT, 'w') as f:
            pass

    def th():
        pprint('Edit user file.')
        # tkinter.messagebox.showinfo('提示', '\n'.join([HINT_TXT[i:i+25] for i in range(0, len(HINT_TXT), 25)]))
        tkinter.messagebox.showinfo('提示', HINT_TXT)
        subprocess.call('notepad %s/%s'%(os.getcwd(), USER_TXT)) # 不显示命令行窗口但进程会阻塞(这样才能在随后更新通讯表)
        readContacts2()

    t1 = Thread(target=th)
    t1.start()
    return t1

def myWalk():
    for path, folders, files in os.walk(DATA_FOLDER):
        for file in files:
            fullpath = path+'\\'+file
            if not fullpath.startswith(TEMP_FOLDER):
                if file[-4:].lower() in ['.txt', '.csv', '.ini']:
                    yield fullpath

def readContacts():
    t = time.time()
    ss = []
    file_list = []
    for fullpath in myWalk():
        for line in openFile(fullpath):
            ss.append([line, line.replace(' ','').lower()]) # 没有lower()将导致无法匹配大写英文和中文混写的关键词, 因为keys会自动转为小写, 而中英混写导致无法匹配拼音索引, readContacts2处同理
        file_list.append([len(ss), fullpath.split('\\', 1)[-1]])
    pprint('Initial:', time.time()-t)
    return ss, file_list

def readContacts2():
    def th():
        t = time.time()
        ss2 = []
        file_list.clear()
        for fullpath in myWalk():
            fullpath2 = '%s%s.pinyin'%(TEMP_FOLDER, fullpath.split('\\', 1)[-1])
            ss2 += makeIndex(fullpath, fullpath2)
            file_list.append([len(ss2), fullpath.split('\\', 1)[-1]])
        global ss
        ss = ss2
        top.onKeyRelease()
        pprint('Refresh:', time.time()-t)
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
            ss2.append(',%s,%s'%pinyin(line.replace(' ','')))
        s2 = md5_path1 + '\n' + '\n'.join(ss2)
        try:
            os.makedirs(os.path.dirname(path2), exist_ok=True)
            with open(path2, 'w', encoding='utf-8') as f: # encoding='utf-8'为了写入无法转换为拼音的字符''
                f.write(s2)
        except Exception as e:
            pprint('Fail to write:', path2, e)
    else:
        ss2 = ss2[1:]
    ss = []
    title_pinyin = ',%s,%s'%pinyin(path1.split('\\', 1)[-1])
    for i in range(len(ss1)):
        ss.append([ss1[i], ss1[i].replace(' ','').lower() + ss2[i]]) # 没有lower()将导致无法匹配大写英文和中文混写的关键词, 如:Q太郎
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

        # about log
        self.id = 0
        self.last_keys = ''

        self.title('电话簿%s （联系作者：QQ11313213）'%__ver__) # TODO 是否有用

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
        self.onKeyRelease(keys_s='')
        self.select(row)
        self.tex1.see('%d.0'%row)
        pprint('location: "%s"'%self.tex1.selection_get()[:-2])

    def copyItem(self):
        text = self.tex1.selection_get()[:-2] # 去掉文末回车换行符
        self.clipboard_clear()
        self.clipboard_append(text)
        pprint('copyItem: "%s"'%text)

    def openPath(self, path):
        pprint('Open path: "%s"'%path)
        os.popen('explorer /select, %s'%path)

    def onRightClick(self, evt=0):
        self.tex1.focus() # 当焦点在ent1中时
        self.current = int(self.tex1.index('current').split('.')[0])
        if len(self.index):
            pprint('Open menu: key="%s", index=%s'%(self.keys_var.get(), self.current))
            self.current_index = self.index[self.current - 1]

            line_last = 0
            for line, file in file_list:
                if line > self.current_index:
                    break
                else:
                    line_last = line
            fullpath = '%s\\%s\\%s'%(os.getcwd(), DATA_FOLDER, file)
            self.menu.entryconfig(2, label='来源: %s (line:%s)'%(file, self.current_index - line_last + 1))
            self.menu.entryconfig(2, command=lambda: self.openPath(fullpath))

            self.select(self.current)
            self.menu.post(evt.x_root, evt.y_root)
        else:
            pprint('Open special menu: key="%s"'%self.keys_var.get())
            self.menu0.post(evt.x_root, evt.y_root)

        return self.current

    def onKeyRelease(self, evt=0, keys_s=None):
        id = self.id = self.id + 1 # 保证id和self.id同时赋值，避免其他线程将self.id变更后还未赋值到id上

        if keys_s is None:
            keys_s = self.keys_var.get()
        self.after(2000, lambda: self.log(id, keys_s)) # 如果传入的是self.xx等会导致在2000ms内self.xx发生改变而传入错误参数

        keys = keys_s.replace('\n', '').lower().split(' ')
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
        self.title('电话簿%s （联系作者：QQ11313213） - %s结果'%(__ver__, len(ss_new))) # title更改耗时短可以做到'同时'更改的效果

        return ss_new

    def log(self, id, keys):
        if keys and self.last_keys != keys and id == self.id:
            pprint('Search: "%s"'%keys)
            self.last_keys = keys


if __name__ == '__main__':
    pprint('Start running: %s'%__ver__)
    time.clock()

    ss = []
    ss, file_list = readContacts()

    top = myPanel()
    readContacts2() # 后台线程运行速度极快(如contact文件夹为空)时可能在top参数生成前就需要使用该参数
    top.onKeyRelease()
    top.mainloop()

    pprint('Finish running: %s'%time.clock())
