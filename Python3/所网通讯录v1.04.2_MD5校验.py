# TODO
# 表格显示
# 双击复制
# 气泡提示来源
# 双击打开引用文件
# 滑块
# 状态栏/菜单栏/标题行/气泡/右键菜单

import os
import time
import hashlib
import tkinter
import xpinyin
from threading import Thread

def md5(file):
    with open(file, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def openFile(file):
    # print('Load:', file)
    if not os.path.exists(file):
        # print('None:', file)
        return ''
    try:
        with open(file, 'r') as f:
            s = f.read()
    except:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                s = f.read()
        except Exception as e:
            print('Fail to read:', file, e)
            s = ''
    return s

def readContacts(path):
    t = time.time()
    os.makedirs(path, exist_ok=True)
    files = os.listdir(path)
    ss = []
    for file in files:
        if file[-4:] == '.txt' or file[-4:] == '.csv':
            ss += openFile(path+'/'+file).split('\n')
    ss2 = []
    for line in ss:
        ss2.append([line, line])
    print('readContacts:', time.time()-t)
    return ss2

def readContacts2(path):
    t = time.time()
    os.makedirs(path, exist_ok=True)
    os.makedirs(path+'/tmp', exist_ok=True)
    p = xpinyin.Pinyin()
    files = os.listdir(path)
    ss2 = []
    for file in files:
        if file[-4:] == '.txt' or file[-4:] == '.csv':
            ss2 += makeIndex(p, path+'/'+file, path+'/tmp/'+file+'.pinyin')
    global ss
    ss = ss2
    top.onKeyRelease(-1)
    print('makeIndex:', time.time()-t)
    return ss2

def makeIndex(p, path1, path2):
    s1 = openFile(path1)
    s2 = openFile(path2)
    ss1 = s1.split('\n')
    ss2 = s2.split('\n')
    md5_path1 = md5(path1)
    if md5_path1 != ss2[0]:
        ss2 = []
        for line in ss1:
            ss2.append(',' + p.get_pinyin(line,'').lower() + ',' + p.get_initials(line,'').lower()) # 全拼做lower()处理是为了转换某些文本中带有大写英文的内容，如'Q太郎'
        s2 = md5_path1 + '\n' + '\n'.join(ss2)
        try:
            with open(path2,'w', encoding='utf-8') as f: # encoding='utf-8'为了写入无法转换为拼音的字符''
                f.write(s2)
        except Exception as e:
            print('Fail to write:', path2, e)
    else:
        ss2 = ss2[1:]
    ss = []
    for i in range(len(ss1)):
        ss.append([ss1[i], ss1[i] + ss2[i]])
    return ss

def setCenter(top):
    top.update_idletasks()
    x = (top.winfo_screenwidth()  - top.winfo_reqwidth())/2
    y = (top.winfo_screenheight() - top.winfo_reqheight())/2
    top.geometry('+%d+%d'%(x,y))

class myPanel(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self, 'lsx')
        self.withdraw() # 先withdraw隐藏再deiconify显示可使setCenter不会导致页面闪烁

        self.title('电话簿v1.04 （联系作者：QQ11313213）')

        self.file1 = tkinter.StringVar()
        self.tex1 = tkinter.Text(self)
        ent1 = tkinter.Entry(self, textvariable=self.file1, width=120)
        ent1     .pack(padx=2, pady=2, fill=tkinter.constants.BOTH, side=tkinter.constants.TOP)
        self.tex1.pack(padx=2, pady=2, fill=tkinter.constants.BOTH, expand=True)

        setCenter(self)
        self.deiconify()

        ent1.focus()
        ent1.bind('<KeyRelease>', self.onKeyRelease)

    def onKeyRelease(self, evt):
        keys = self.file1.get().lower().split(' ')
        ss_new = []
        for s in ss:
            ok = True
            for key in keys:
                if key not in s[1]:
                    ok = False
            if ok:
                ss_new.append(s[0])

        res = '\n'.join(ss_new)
        self.title('电话簿v1.04 （联系作者：QQ11313213） - %s结果'%len(ss_new))
        self.tex1.delete(1.0, 'end')
        self.tex1.insert(1.0, res)

if __name__ == '__main__':
    ss = []
    ss = readContacts('contact')
    t1 = Thread(target=readContacts2, args=('contact',))
    t1.start()

    top = myPanel()
    top.onKeyRelease(-1)
    top.mainloop()


# 20190215 创建
# 抬键刷新
# 窗口居中

# 20190218 更新
# 缩放窗口适配
# 光标热点
# 简化数据表
# 20190219 更新
# 全拼和拼音字头检索(不支持多音字和全拼字头混输)

# 20190318 更新
# 将联系人资源文件移动到统一文件夹
# 支持多通讯录资源文件(文件名筛选格式为txt/csv)
# 多线程后台转换拼音不占用程序启动时间
# 安全创建文件夹和临时文件
# 20190322 更新
# 兼容读取默认格式和utf-8格式的文本文件

# 20190325
# 不影响程序功能的异常抛出
# 20190326
# 合并一个函数
# 拼音索引建立完成后自动再次查找检索结果
# 增加'!!README.txt'
# 20190327
# 程序启动后查找检索结果可使启动后可以看到操作说明README
# 先隐藏再显示窗体避免窗口闪烁
# 增加'!EXAMPLE.txt'
# 转换某些文本中带有大写英文的内容为小写全拼，如'Q太郎'
# 更改通过MD5值确定文件索引是否已建立
# 软件窗口标题

# TODO
# 增加滚动条(REJECT:需要用滚动条才能定位的检索结果条目数目也没有参考的意义)
# 常驻关键词和常不驻关键词(拟为>>/--/..)(REJECT:视觉效果一般)
