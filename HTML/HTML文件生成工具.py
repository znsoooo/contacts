import os
import xpinyin

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

def generate(demofile, openfile, savefile):
    # 处理模板
    with open(demofile, 'r', encoding='utf-8') as f:
        s = f.read()
    template = [s.split('...')[0]+'...\n',
                '</p>'+s.split('</p>')[-1]]

    # 处理数据
    opendata = readTXT(openfile)

    # 生成HTML
    p = xpinyin.Pinyin()
    savedata = [template[0]]
    cnt = 0
    for i, line in enumerate(opendata):
        if i > cnt:
            print('progress: %s/%s'%(cnt,len(opendata)))
            cnt += 1000
        savedata.append(line + ';' + p.get_pinyin(line,'').lower() + ',' + p.get_initials(line,'').lower()) # 全拼做lower()处理是为了转换某些文本中带有大写英文的内容，如'Q太郎'
    savedata.append(template[1])
    with open(savefile, 'w', encoding='utf-8') as f: # utf-8为避免某些无法转换为拼音的字符可以顺利写入文件
        f.write('\n'.join(savedata))

if __name__ == '__main__':
    demofile = 'template.html'

    openfile = 'contact'     # folder or file is ok.
    savefile = 'HTML通讯录.html'
    generate(demofile, openfile, savefile)

    openfile = 'contact.txt' # folder or file is ok.
    savefile = 'HTML通讯录test.html'
    generate(demofile, openfile, savefile)

