import time
import tkinter
from threading import Thread

LOG_FILE = 'string_log.txt'

def pprint(*s):
    print(*s)
    try:
        with open(LOG_FILE, 'a', encoding='u8') as f:
            ss = ' '.join(map(str, s))
            f.write(time.strftime('[%Y-%m-%d %H:%M:%S]: ', time.localtime()) + ss + '\n')
    except Exception as e:
        print('log write error:', e)


class myPanel(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self, 'lsx')

        self.id = 0
        self.last_keys = ''

        self.keys_var = tkinter.StringVar()
        ent1 = tkinter.Entry(self, textvariable=self.keys_var)
        ent1.pack(fill='both')

        ent1.focus()
        ent1.bind('<KeyRelease>', self.onKeyRelease)

    def onKeyRelease(self, evt):
        id = self.id = self.id + 1 # 保证id和self.id同时赋值，避免其他线程将self.id变更后还未赋值到id上
        keys = self.keys_var.get()
        self.after(2000, lambda: self.log(id, keys)) # 如果传入的是self.xx等会导致在2000ms内self.xx发生改变而传入错误参数

    def log(self, id, keys):
        if keys and self.last_keys != keys and id == self.id:
            pprint(keys)
            self.last_keys = keys


if __name__ == '__main__':
    top = myPanel()
    top.mainloop()
