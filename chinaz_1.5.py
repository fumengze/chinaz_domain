import requests
from lxml import etree
import pymysql
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse
from socket import gethostbyname

headers = {
     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
}
set = set()
#开启连接模块
def mysql_Connect():
    db = pymysql.connect(host='192.168.102.227', user='pyscript', password='password', port=3306, db='url_all')
    return db

#mysql插入数据模块
def mysql_insert(r,db,column,tables):
    cursor = db.cursor()
    try:
        sql = "INSERT INTO `{tables}`(`{column}`) VALUES ('{r}')".format(tables=tables,column=column,r=r)
        cursor.execute(sql)
        db.commit()  # 执行插入操作
    except:
        db.rollback()#添加事物回滚，以免插入数据时出现失败
        print('数据插入错误，已进行事务回滚')
#mysql去重模块
def mysql_repeat(db):
    cursor = db.cursor()
    try:
        sql_del = 'DELETE FROM url_tables WHERE url like "%*屏蔽的关键字*%"'  # 删除被屏蔽的url
        cursor.execute(sql_del)
        sql_repeat = "DELETE FROM url_tables WHERE id IN(SELECT id FROM(select id from url_tables where url in (select url from url_tables group by url having count(url)>1) and id not in(select min(id) from url_tables group by url having count(url)>1)) as abc)"
        cursor.execute(sql_repeat)
        db.commit()  # 执行删除操作
        print('--------数据已经去重完成------------')
    except:
        db.rollback()#添加事物回滚，以免删除数据时出现失败
        print('数据删除错误，已进行事务回滚')

#获取查询数据的返回元组,db为数据库连接，sql_count为查询数据总数，sql_all_url为获取数据时的sql语句，num_start是偏移量从0开始，tables是表名
def extract_tuple(db,sql_count,sql_all_url,num_start,tables,txt,ip_url,Counter):
    if Counter > 0:
        sum = 0
    if ip_url == 'ip':
        sum = None
    try:
        cursor = db.cursor()
        cursor.execute(sql_count)
        count_num = int(str(cursor.fetchone()).replace('(', '').replace(')', '').replace(',', ''))
        print('总共有'+str(count_num)+'条数据')
        num = count_num % 100  # 取出余数
        count_num = count_num - num  # 能够被整除的整数
        count_Divide = count_num // 100 # 可以整除的次数
        exit = 'run'
        with open(txt, 'w+') as f:
            for i in range(0, count_Divide + 1):
                if sum == Counter:
                    break
                cursor.execute(sql_all_url)
                num_start = num_start + 100
                row_all = cursor.fetchall()
                for row in row_all:
                    row = str(row).replace('(', '').replace(')', '').replace(',', '').replace("'", "")
                    f.write('http://'+row + '\n')
                    f.flush()
                    print(row)
                    sql_update = "UPDATE {tables} SET extract=1 WHERE {ip_url}='{row}'".format(tables=tables,ip_url=ip_url,row=row)
                    try:
                        cursor.execute(sql_update)
                        db.commit()
                    except:
                        db.rollback()
                        print('数据更新错误，已进行事务回滚')
                    if Counter > 0:
                        sum = sum + 1
                        print('取出第'+str(sum)+'条域名')
                        if sum == Counter:
                            print('成功提取出' + str(sum) + '条域名')
                            break
    except Exception  as e:
        print(e)
        print('查询数据时出现错误')




#从inj.txt中批量获取IP并插入到数据库中,最后进行去重，再提取出没有提取过的IP写入到ip.txt
def ip_insert(db):
    cursor = db.cursor()
    column = 'ip'#mysql_insert模块参数
    #extract_tuple模块定义参数
    ip_url = 'ip'
    Counter = 0
    txt = 'ip.txt'
    tables = 'ip_tables'
    num_start = 0
    sql_count = 'select count(ip) from ip_tables where extract = 0'
    sql_all_url = 'select ip from ip_tables where extract = 0 limit {num_start}, 100'.format(num_start=num_start)
    for line in open('inj.txt', encoding='utf-8'):
        try:
            line = urlparse(line).netloc
            host = gethostbyname(line.strip('\n'))#获取ip地址
            set.add(host.strip())#添加到set里进行去重
            print(set)
        except:
            print('没有获取到IP地址')
    for r in set:
        mysql_insert(r,db,column,tables)#把IP插入到数据库中
    set.clear()
    try:
        sql_repeat = 'DELETE FROM ip_tables WHERE id IN(SELECT id FROM(select id from ip_tables where ip in (select ip from ip_tables group by ip having count(ip)>1) and id not in(select min(id) from ip_tables group by ip having count(ip)>1)) as abc)'
        cursor.execute(sql_repeat)
        db.commit()  # 执行插入操作
        print('------IP已经去重完成------')
    except:
        db.rollback()#添加事物回滚，以免删除数据时出现失败
        print('IP删除错误，已进行事务回滚')
    extract_tuple(db, sql_count, sql_all_url, num_start, tables,txt,ip_url,Counter)#从数据库中提取没有提取过的IP，提取后把extract字段更新为1，0代表未提取，1代表提取过



#把url提取出domain后去重写入domains.txt
def url_domain(txt):
    for i in open(txt,encoding='utf-8'):
        try:
            if i.split('/')[0] == i:
                set.add(i.strip())
            else:
                set.add(i.split('/')[2].strip())
        except:
            continue
    with open('domains.txt', 'w+') as f:
        for o in set:
            f.write(o + '\n')
    set.clear()

#获取页数
def url_page(domain):
    s = requests.Session()  # 设置会话
    s.mount('http://', HTTPAdapter(max_retries=1))  # 设置最大重试次数
    try:
        html = s.get('http://s.tool.chinaz.com/same?s={domain}'.format(domain=domain),headers=headers,timeout=8)
        page_sutatus = html.status_code
        parseHtml = etree.HTML(html.text)
        pages = parseHtml.xpath('//span[@class="col-gray02"]/text()')#获取页数
        if len(pages) != 0:  # 判断是不是空
            page = str(pages[0].replace("共", "").replace("页，到第", ""))  # 获取页数
            print('获取到页数为'+page)
        else:
            page = 0
            print('没有获取到旁站')
    except:
        page_sutatus = 400
        page = 0
        print('获取页数出现错误')
    page = int(page)
    return page,page_sutatus

#写入数据库操作
def url_all():
    db = mysql_Connect()
    ip_insert(db)#从inj.txt中批量获取IP并插入到数据库中,最后进行去重，再提取出没有提取过的IP写入到ip.txt，最后更新extract字段为1，代表已取过
    num = 0
    column = 'url'
    tables = 'url_tables'
    for domain in open('ip.txt'):
        (page,page_sutatus) = url_page(domain)#获取页数
        if page_sutatus != requests.codes.ok:#检查获取页数时是否请求成功
            continue
            print('请求失败，状态码为：'+ page_sutatus)
        if page > 0:
            s = requests.Session()  # 设置会话
            s.mount('http://', HTTPAdapter(max_retries=1))  # 设置最大重试次数
            for i in range(1, page+1):
                p = str(i)
                try:
                    html = s.get('http://s.tool.chinaz.com/same?s=' + domain +'&page=' + p,headers=headers,timeout=8)
                    if html.status_code != requests.codes.ok:
                        continue
                        print('获取数据错误，状态码为：'+ html.status_code)
                except:
                    continue
                    print('获取旁站时出现错误')
                parseHtml = etree.HTML(html.text)
                urls = parseHtml.xpath("//a[@href='javascript:']/text()")
                list = ['同IP网站查询','查询记录','确定','SEO相关','其他工具相关']
                for l in list:#去除无关数据
                    if l in urls:
                        urls.remove(l)
                for r in urls:
                    r = str(r)
                    mysql_insert(r,db,column,tables)#插入数据到数据库
                num = num + len(urls)
                print(num)
                print(urls)
        else:
            continue
    print('----数据采集完毕，正在进行数据去重----')
    mysql_repeat(db)#数据去重
    db.close()#关闭数据库连接
    print('--------数据库连接已关闭-------------')




if __name__ == '__main__':
    run = input('请选择运行模式，A 获取旁站插入到数据库 inj.txt为需要爬取旁站的URL，B 提取数据写入文本，结果为result.txt:\n')
    if run == 'A' or run == 'a':
        txt = 'inj.txt'
        url_domain(txt)
        url_all()
    elif run == 'B' or run =='b':#获取url_tables中的未提取过的url
        Counter = input('请输入需要提取出域名的数量')
        if Counter.isdigit() == True:
            Counter = int(Counter)
            db = mysql_Connect()
            ip_url = 'url'
            txt = 'result.txt'
            tables = 'url_tables'
            num_start = 0
            sql_count = 'select count(url) from url_tables where extract = 0'
            sql_all_url = 'select url from url_tables where extract = 0 limit {num_start}, 100'.format(
                num_start=num_start)
            extract_tuple(db, sql_count, sql_all_url, num_start, tables, txt, ip_url, Counter)
            db.close()
        else:
            print('输入的值只能是整数，请重新输入')
    else:
        print('输入错误，请重新输入')