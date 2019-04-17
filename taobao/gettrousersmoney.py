#coding=utf-8

#导入路径
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from base import webbase
from common import conf,logoutput,getxml,mysql

class Trousers():

    def __init__(self):
        setup = webbase.SetUp()
        dr = setup.web_setup()
        self.driver = webbase.Web(dr)
        self.cf = conf.Conf()
        self.driver.get_url(self.cf.get_conf_data("taobao")["trousersurl"])
        self.lg = logoutput.Logger()
        self.gx = getxml.XmlOperation()
        self.db = mysql.Mysql()
        self.db.connect_mysql()
        self.cur = self.db.cur
        self.selectData="Product"

    def create_tables(self):
        '''
        创建表
        :return:
        '''
        stime = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
        sql_1 = """create table product_info{nowtime} (id int(5) NOT NULL auto_increment,biaoti varchar(500),price char (10),pic_src varchar (500),store_url varchar (5000),PRIMARY KEY (`id`))""".format(
            nowtime=stime)
        self.cur.execute(sql_1)
        self.tableName="product_info"+str(stime)

    def get_data(self):
        self.scroll_page()
        time.sleep(3)
        t=self.gx.get_xml_data("trousers","product_picture")
        tFather=self.gx.get_xml_data("trousers","procuct_pic_father")
        elements=self.driver.get_elements(t)
        elementsFather=self.driver.get_elements(tFather)
        for i in range(0,len(elements)):
            biaoti=elements[i].get_attribute("alt")
            pic_src=elements[i].get_attribute("data-src")
            store_url=elementsFather[i].get_attribute("href")
            price=elementsFather[i].get_attribute("trace-price")
            self.insert_table(biaoti,price,pic_src,store_url)

    def insert_table(self,biaoti,price,pic_src,store_url):
        if biaoti.find("\'")==-1:
            pass
        else:
            biaoti=biaoti.replace("\'"," ")
        self.lg.info(biaoti)
        self.lg.info(price)
        self.lg.info(pic_src)
        self.lg.info(store_url)

        sql="insert into {tablename}(biaoti,price,pic_src,store_url) values (\'{biaoti}\',\'{price}\',\'{pic_src}\',\'{store_url}\');".format(tablename=self.tableName,biaoti=biaoti,price=price,pic_src=pic_src,store_url=store_url)
        self.cur.execute(sql)
        self.db.db.commit()

    def click_next(self):
        n=self.gx.get_xml_data("trousers","next_btn")
        self.driver.click(n)

    def is_next_click(self):
        # n = self.gx.get_xml_data("trousers", "next_btn_isnoclick")
        n = self.gx.get_xml_data("trousers", "next_btn")
        f=self.driver.is_exist(n)
        if f:
            return True
        else:
            return False

    def close_driver(self):
        self.driver.driver.quit()
        self.db.close_connect()

    def scroll_page(self):
        self.driver.scroll_page(pagesize="1000")

    def enter_taobao(self,selectData):
        self.selectData=selectData
        i=self.gx.get_xml_data("trousers","index_input")
        b=self.gx.get_xml_data("trousers","index_search")
        self.driver.send_keys(i,selectData)
        self.driver.click(b)

    def insert_tablelist(self):
        t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "insert into product_table_list(product_table_name,product,run_time) values (\'{tablename}\',\'{product}\',\'{runtime}\');".format(
            tablename=self.tableName,product=self.selectData,runtime=t)
        self.cur.execute(sql)
        self.db.db.commit()
    # 访问验证是否存在
    def fwyz_isexist(self):

        e=self.gx.get_xml_data("trousers","product_fxyz")
        flag=self.driver.is_exist(e,2)
        return flag




if __name__=="__main__":
    trousers=Trousers()
    trousers.create_tables()
    if len(sys.argv)==2:
        trousers.enter_taobao(sys.argv[1])
    else:
        trousers.enter_taobao("显示器")

    page=1

    try:
        while (1):
            trousers.get_data()
            trousers.lg.info("已获取{p}页数据".format(p=page))
            page+=1
            flag=trousers.is_next_click()
            if flag:
                pass
            else:
                break
            trousers.click_next()
            f = trousers.fwyz_isexist()
            if f:
                break
            else:
                pass

        trousers.insert_tablelist()
    except Exception as e:
        trousers.lg.error(e)
    finally:
        trousers.close_driver()
