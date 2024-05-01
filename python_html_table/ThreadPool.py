import random
import os
import threading
import requests,time
import csv,easygui,re
# import chardet
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from PyQt5.QtCore import QThread,pyqtSignal
from pyqtwindow import Jsonfile

soft = 0
softname = ''
status_code = 0

meka_dict = {
    "コジマネット":1,
    "ヨドバシ.com":1,
    "Amazon.co.jp":1,
    "ビックカメラ.com":1,
    "ヤマダウェブコム":1,
    "EDIONネットショップ":1,
    "楽天ビックカメラ":1,
}

xpath_dict = {
    '楽天ブックス':'//div[@class="status-heading"]//text()',
    'ヨドバシ.com':'//span[@id="salesInfoTxt"]/text()',
    'Joshin':'//*[@id="contents_info_area"]/div/div[3]/div/div[1]/ul/li/img/@alt',
    'Amazon.co.jp':'//*[@id="availability"]/span//text()',

}

def get_Qoo10_data(banhao):
    # import requests, re
    url = f'https://www.qoo10.jp/GMKT.INC/Goods/Goods.aspx?goodscode={banhao}'
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "ja,zh-CN;q=0.9,zh;q=0.8",

    }
    htmlcode = requests.get(url, headers=hd)
    code = htmlcode.apparent_encoding
    # print('code=', code)
    htmlcode.encoding = code
    htmlcode = htmlcode.text
    redata = re.findall(r'(?<=strong data-price=").*?(?=">)',htmlcode)[0]
    print(f'Qoo10价格={redata}')
    return redata

def get_kakaku_data(url,filenumber):
    # print('getkakaku',filenumber)
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "ja,zh-CN;q=0.9,zh;q=0.8",

    }
    htmlcode = requests.get(url, headers=hd)
    global  status_code
    if htmlcode.status_code != 200:
        status_code +=1
    code = htmlcode.apparent_encoding
    # print('code=', code)
    htmlcode.encoding = code
    htmlcode = htmlcode.text
    htmlcode = htmlcode.replace("㈱", "(株)")
    htmlcode = htmlcode.replace("デンキヤ.com	", "デンキヤ.com")
    htmlcode = htmlcode.replace("&lt;", "<")
    htmlcode = htmlcode.replace("&gt;", ">")
    # writetxt(htmlcode, code)
    # ss = etree.HTML(htmlcode.encode(code))
    # ta = ss.xpath("//tr")
    ## 网页源码写入文件
    # with open(os.getcwd() + "\\htmlcode.txt", 'w', encoding='utf-8-sig') as f:
    #     f.write(htmlcode)

    # htmlcode = readtxt(path,code)
    for i in range(0, 3):
        # print('运行次数-%i' % i)
        if filenumber == '6':
            # print('==6')
            data = getxpathphone(htmlcode,code)
        else:
            data = getxpath(htmlcode, code,filenumber)
        if data != '':
            break
        time.sleep(0.5)
    # print(data)
    return data

def getxpath(html,code,filenumber):

    tablecode = "//tr"
    mytree = etree.HTML(html)
    #有时去掉编码可以正确识别网页
    # mytree = etree.HTML(html.encode(code))
    tr_list = mytree.xpath(tablecode)
    # print('lentr',len(tr_list))

    meka_num = 0 #设置默认厂家位置为0，后面可以判断如果不为零表示以经添加过，不在添加。这样就是获取的第一个厂家位置
    meka_name = ''
    meka_jishu = 0

    try:
        title = mytree.xpath('//div[@id=\'titleBox\']/div[@class=\'boxL\']/h2/text()')[0]
        if title[0] == '-':
            title = "'" + title
    except:
        return ''
    try:
        date = mytree.xpath('//div[@class=\'releaseDateWrap\']/span/text()')[0].strip()

    except:
        date = ""
    try:
        pm = mytree.xpath('//div[@id=\'ovBtnBox\']//span[@class=\'num\']/text()|//ul[@class=\'clearfix\']/li[1]/span[@class=\'rankNum\']/text()')[0]
    except:
        pm = ""
    try:
        ds = mytree.xpath('//div[@class=\'subInfoObj4\']/span[1]/a/span/text()')[0]
        if int(ds) > 50:
            ds = '50'
    except:
        ds = 0

    print(title,date,pm,ds)
    a =[[title, date, pm, ds],[title, date, pm, ds]]
    zaiku_list = []
    for i, td in enumerate(tr_list):
        try:
            #xl为序列，jg为价格，zk为在库状态，sj为商品名
            xl = td.xpath('./td[1]/span[1]//text()')
            xl = ''.join(xl)
            # print(xl)
            jg = td.xpath('./td[2]/div[1]/p[1]//text()')
            jg = ''.join(jg)
            # print(jg)
            zk = td.xpath('./td[4]/p[1]//text()')
            zk = ''.join(zk)
            # if '〜' in zk:
            #     zk = zk + '営業日'
            # print(zk)
            sj = td.xpath('./td[5]/div[1]/div[1]/div[1]/p[1]/a[1]//text()')
            SL = td.xpath('./td[3]//text()')
            SL = ''.join(SL)
            SL = SL.replace('\r\n', '').replace('～','').replace('〜','').replace('¥','')
            sjurl = td.xpath('./td[5]/div[1]/div[2]/a/@href')
            sj = ''.join(sj)
            sjurl = ''.join(sjurl)
            # print(sj,SL)

            if xl:
                a.append([title,date,pm,ds,xl,jg,zk,sj])
                zaiku_list.append([xl,jg,zk,sj,sjurl])

                # 判断商家是否是前5
                xl_num = int(re.findall('\d+', xl)[0])
                if xl_num <= 5 and meka_num == 0 and zk == "○" and sj in meka_dict:
                    meka_num = xl_num
                    meka_name = sj
                if xl_num <= 5 and zk == "○" and sj in meka_dict:
                    meka_jishu +=1

        except:
            pass

    if meka_num != 0 and meka_jishu >= 2:
        a[-1].append(meka_num)
        a[-1].append(meka_name)
        a[-1].append(meka_jishu)

    js = len(a)
    if js < int(ds):
        return '重试'
    while True:
        js = js - 12
        # print('js',js)
        if js>0:
            a.append([title, date, pm, ds])
            a.append([title, date, pm, ds])
        else:
            break
    # print(a)

    return a

def getxpathphone(html,code):
    print('采集手机')
    tablecode = "//tr"
    mytree = etree.HTML(html)
    # mytree = etree.HTML(html.encode(code))
    tr_list = mytree.xpath(tablecode)
    # print(tr_list)

    meka_num = 0 #设置默认厂家位置为0，后面可以判断如果不为零表示以经添加过，不在添加。这样就是获取的第一个厂家位置
    meka_name = ''
    meka_jishu = 0

    try:
        title = mytree.xpath('//div[@id=\'titleBox\']/div[@class=\'boxL\']/h2/text()')[0]
    except:
        return ''
    try:
        date = re.findall(r'(?<=販売時期：)[\s\S]+?(?=\s)',html)[0]
        # print(f'data={date}')
    except:
        date = ""
    try:
        pm = mytree.xpath(
            '//div[@id=\'ovBtnBox\']//span[@class=\'num\']/text()|//ul[@class=\'clearfix\']/li[1]/span[@class=\'rankNum\']/text()')[
            0]
    except:
        pm = ""
    try:
        ds = mytree.xpath('//*[@id="SRanking"]/a/text()')[0]
        ds = re.findall('\d+', ds)[0]
    except:
        ds = 0
    shangjiashu = ds
    print(title, date, pm, ds)

    a = [[title, date, pm, ds]]
    for i, td in enumerate(tr_list):
        # print('i=',i)
        try:
            #xl为序列，jg为价格，zk为在库状态，sj为商品名
            xl = td.xpath('./td[1]//text()')
            xl = ''.join(xl)
            # print('xl',xl)
            jg = td.xpath('./td[2]/p[1]/a[1]//text()')
            jg = ''.join(jg)
            # print('jg',jg)
            zk = td.xpath('./td[4]//text()')
            zk = ''.join(zk)
            # print('zk',zk)
            sj = td.xpath('./td[6]//a[1]//text()')
            SL = td.xpath('./td[3]//text()')
            SL = ''.join(SL)
            SL = SL.replace('\r\n', '').replace('～','').replace('〜','').replace('¥','')
            sjurl = td.xpath('./td[7]/a/@href')
            try:
                sjurl = sjurl[0]
            except:
                pass
            # sjurl = sjurl.replace('%3A', ':').replace('%2F', '/').replace('%3F', '?').replace('%26', '&').replace('%3D',
            #                                                                                                   '=').replace(
            #     '%2B%5B', ' [').replace('%5D', ']').replace('%2E', '.')
            sj = ''.join(sj)
            # print('sj',sj,sjurl)


            if xl and '位' in xl:
                a.append([title, date, pm, ds, xl,jg, '',zk, sj])

                # 判断商家是否是前5
                xl_num = int(re.findall('\d+', xl)[0])
                if xl_num <= 5 and meka_num == 0 and zk == "有" and sj in meka_dict:
                    meka_num = xl_num
                    meka_name = sj
                if xl_num <= 5 and zk == "有" and sj in meka_dict:
                    meka_jishu +=1
        except:
            # print('序列出错')
            pass

    if meka_num != 0 and meka_jishu >= 2:
        a[-1].append(meka_num)
        a[-1].append(meka_name)
        a[-1].append(meka_jishu)

    js = len(a) - 2
    if int(ds) - js >= 2:
        return ''

    # print(a)
    return a

def get_html(url):
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
        # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
        # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    ]

    hd = {
        "User-Agent": random.choice(user_agent_list),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "ja,zh-CN;q=0.9,zh;q=0.8",
        
    }
    # print(hd)
    htmlcode = requests.get(url, headers=hd)
    global status_code
    if htmlcode.status_code != 200:
        status_code += 1
    code = htmlcode.apparent_encoding
    # print('code=', code)
    htmlcode.encoding = code
    htmlcode = htmlcode.text
    print(htmlcode)
    # try:
    #     mytree = etree.HTML(htmlcode)
    # except:
    #     mytree = etree.HTML(htmlcode.encode(code))
    # # print(mytree)
    # global xpath_dict
    # xpath = xpath_dict[name]
    #
    # zaiku = mytree.xpath(xpath)
    # # print(zaiku)
    # zaiku = ''.join(zaiku)
    # # print(zaiku)
    # zaiku.replace('\n','')
    # print('以开始运行\{}\四家函数,结果= {}，公式={},\n url={}'.format(name,zaiku  , xpath, url))
    # # print('去回车符后zaiku',zaiku)
    # try:
    #     if re.findall('\d+',zaiku)[0] in zaiku:
    #         # print('if', zaiku,re.findall('\d+',zaiku)[0])
    #         return '',''
    # except:
    #     if '在庫あり' in zaiku:
    #         # print('elif',zaiku)
    #         return '在庫あり',name
    #     elif '翌日出荷' in zaiku:
    #         # print('elif', zaiku)
    #         return '在庫あり', name
    #     elif '明日お届け' in zaiku:
    #         # print('elif', zaiku)
    #         return '在庫あり', name
    return '',''

# url = r'https://www.amazon.co.jp/dp/B01N12HJHQ'
# ss = get_four(url,'Amazon.co.jp')
# print(ss)

def openfileurl(sheet_name,col_name,filesname = None):
    if filesname == None:
        filesname = easygui.fileopenbox(default="C:\bazhuayu\采集\*.xlsm", title="選取掃描文件")
    print(filesname)
    try:
        urls = pd.read_excel(filesname, sheet_name=sheet_name, usecols=col_name,  header=None)
    except:
        print('设置的表名或列名不正确，退出后重新添写')
        return 'error'
    print('去重前',len(urls))
    count = urls.columns.values
    try:
        count = count[0]
        # print('列值',count)
    except:
        return 'error'
    #以下去重
    newlist = []
    newdick = {}
    for i,item in urls.iterrows():
        if item.notnull().all() :
            # print(urls.iloc[i][21])
            try:
                temp = re.findall(r'(?<=item/).\d+',urls.iloc[i][count])[0]
                # print(temp)
                if temp not in newdick:
                    newdick[temp] = 'OK'
                    newlist.append(urls.iloc[i][count])
            except:
                print('URL处理失败\n',urls.iloc[i][count])
                # return 'error'
    # newlist.reverse()  #数组倒序
    print('去重后',len(newlist))
    return newlist,len(urls)

class ThreadPool(QThread):
    shangpinshu_signal = pyqtSignal(int,int,int)
    jishu_signal = pyqtSignal(int,int,int)
    runover_signal = pyqtSignal(int)
    haoshi_signal = pyqtSignal(int,int)
    error_signal = pyqtSignal(str)
    def __init__(self,max_workers,filename,sheet,count,index,path):
        super(ThreadPool, self).__init__()
        self.starttime = self.newtime()
        self.max_workers = max_workers
        self.filename = filename
        self.sheet = sheet
        self.count = count
        self.index = index
        self.RUNING = True
        time_now = time.strftime('%Y-%m-%d', time.localtime())
        self.path = path + '\\' + time_now
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.jishu = 0
        self.data = []
        # print('初使化完成',self.max_workers,self.filename,self.sheet,self.count)
    def run(self):
        # print('RUN',self.max_workers,self.filename,self.sheet,self.count)
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            global status_code,soft,softname
            DB = Jsonfile().jsonreader()
            soft = DB['soft']
            softname = DB['softname']
            softname = re.findall('\d+',softname)
            # print(softname,type(softname))
            if '/' in self.filename:
                file = re.findall(r'[^/]+(?!.*/).+?(?=\.)', self.filename)[0]
            else:
                file = re.findall(r'[^\\]+(?!.*\\).+?(?=\.)', self.filename)[0]
            try:
                filenumber = re.findall(r'\d+',file)[0]
            except:
                filenumber = 1
            # print(file)

            status_code = 0
            self.jishu = 0
            self.data  = []
            self.work_list = []
            start,urls = openfileurl(self.sheet,self.count,self.filename)
            if start == 'error':
                self.stop()
                self.error_signal.emit('出错')
            self.shangpinshu_signal.emit(self.index,len(start),urls)
            # print(self.index,len(start))
            for i,url in enumerate(start):
                # print('status_code',status_code)
                if self.RUNING == False:
                    print('点击停止，不在添加线程')
                    break
                # print('i,usrl',i,url)
                work = pool.submit(get_kakaku_data,url,filenumber)
                if status_code >= 10:
                    self.stop()
                work.add_done_callback(self.appdata)
                self.work_list.append(work)
                # if i % 8 == 0:
                #     s = random.randint(2, 5)
                #     print('i={}%8={},延时{}秒'.format(i,i%8,s))
                #     time.sleep(s)
            pool.shutdown()
            # print(self.data)
            try:
                with open (self.path + "\\" + file + ".csv","w",newline="",encoding="cp932",errors="ignore") as f:
                    writer = csv.writer(f)
                    writer.writerows(self.data )
                    f.close()
            except:
                with open(os.getcwd() + "\\" + file + ".csv", "w", newline="", encoding="cp932", errors="ignore") as f:
                    writer = csv.writer(f)
                    writer.writerows(self.data)
                    f.close()
                print('保存路径写入失败，以临时存贮在{}'.format(os.getcwd() + "\\" + file + ".csv"))
            self.runover_signal.emit(self.index)
            endtime = self.newtime()
            time = endtime-self.starttime
            self.haoshi_signal.emit(self.index,int(time))
            print(time)
    def stop(self):
        self.RUNING = False
        # self.work_list.reverse()
        for work in reversed(self.work_list):
            work.cancel()
        print('线程以停止')
    def newtime(self):
        a = time.time()
        return a

    def upjishu(self):
        # global jishu
        self.jishu_signal.emit(self.index,self.jishu,self.rows)

    def appdata(self,a):
        # global data, jishu
        a = a.result()
        for item in a:
            self.data .append(item)
        self.jishu += 1
        self.rows = len(self.data)
        self.jishu_signal.emit(self.index,self.jishu,self.rows)
        print('以完成{}个任务，表格现有{}行。'.format(self.jishu, len(self.data )))