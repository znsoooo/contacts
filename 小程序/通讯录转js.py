# build 20200606

# 20191123(ref HTML生成工具)
# replace(' ', '-').replace(',', ' ')适配手机更容易地选中并复制号码(可以跨过'-'选中数字而不会跨过空格选中数字)

import os
import zlib
import base64

import xpinyin

template = """var s = '%s';

module.exports = {
  s: s
}
"""

def pack(s):
    s1 = zlib.compress(s.encode())
    s2 = base64.b64encode(s1).decode()
    return s2

def unpack(s):
    s1 = base64.b64decode(s)
    s2 = zlib.decompress(s1).decode()
    return s2

def makejs(s):
    s1 = template%pack(s)
    with open('data.js', 'w') as f:
        f.write(s1)

def readTXT(path):
    print('open:', path)
    res = []
    if os.path.isdir(path):
        for path2 in os.listdir(path):
            res += readTXT(path+'/'+path2)
    elif os.path.isfile(path):
        try:
            with open(path, 'r') as f:
                s = f.read()
        except:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    s = f.read()
            except Exception as e:
                s = ''
                print(e)
        res += s.split('\n')
    return res

def generate(folder):
    opendata = readTXT(folder)

    # 生成HTML
    p = xpinyin.Pinyin()
    savedata = []
    cnt = 0
    for i, line in enumerate(opendata):
        line = line.strip().replace(' ', '-').replace(',', ' ').strip() # 去除空格/合理设置空格位置方便复制/去除csv中的尾部多余逗号替换后造成的空格
        if i > cnt:
            print('progress: %s/%s'%(cnt,len(opendata)))
            cnt += 2000
        savedata.append(line + ';' + p.get_pinyin(line,'').lower() + ',' + p.get_initials(line,'').lower()) # 全拼做lower()处理是为了转换某些文本中带有大写英文的内容，如'Q太郎'

    s = '\n'.join(savedata)
    makejs(s)



print(pack('hello lsx!'))
print(unpack('eJzLSM3JyVfIKa5QBAAVTwOt'))


# makejs('hello lsx!')
generate('demo')


