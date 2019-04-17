#coding=utf-8
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from base import webbase
from common import conf,logoutput,getxml,mysql
class GetRank():
    def __init__(self):
        setup=webbase.SetUp()
        dr=setup.web_setup()
        self.driver=webbase.Web(dr)
        self.cf=conf.Conf()
        self.driver.get_url(self.cf.get_conf_data("taobao")["url"])
        self.lg=logoutput.Logger()
        self.gx=getxml.XmlOperation()
        self.db=mysql.Mysql()
        self.db.connect_mysql()
        self.cur=self.db.cur

    def click_ljpj(self):
        self.driver.scroll_page()
        ljpj=self.gx.get_xml_data("tb_product","product_ljpl_link")
        self.driver.click(ljpj)


    def close_driver(self):
        self.driver.driver.quit()

    def get_pl(self,tName):
        pl=self.gx.get_xml_data("tb_product","product_pl_text")
        plText=self.driver.get_elements(pl)
        for p in plText:
            try:
                sql='''insert into {t} (pinglun) values(\"{pl}\") '''.format(t=tName,pl=str(p.text))
                self.cur.execute(sql)
                self.db.db.commit()
                self.lg.info(p.text)
            except Exception as e:
                self.lg.error(e)
                continue

    def get_color(self,tNanem):
        c=self.gx.get_xml_data("tb_product","product_color_text")
        colorText=self.driver.get_elements(c)
        for p in colorText:
            try:
                data=p.text
                data=data.split("\n")
                color=data[0].split("：")[-1]
                jinghanliang=data[-1].split("：")[-1]
                sql='''insert into {t} (daxiao,yanse)values (\"{yanse}\",\"{daxiao}\")'''.format(t=tNanem,yanse=color,daxiao=jinghanliang,)
                self.cur.execute(sql)
                self.db.db.commit()
                self.lg.info(color)
                self.lg.info(jinghanliang)
            except Exception as  e:
                self.lg.error(e)
                continue

    def click_next(self):
        n=self.gx.get_xml_data("tb_product","product_next_link")
        self.driver.click(n)

    def is_next_click(self):
        n = self.gx.get_xml_data("tb_product", "product_next_isnotclick")
        f=self.driver.is_exist(n)
        if f:
            return False
        else:
            return True

    def create_table(self):
        stime=str(int(time.time()))
        sql_1="""create table taobao_pl{nowtime} (id int(5) NOT NULL auto_increment,pinglun varchar(500),PRIMARY KEY (`id`))""".format(nowtime=stime)
        sql_2='''create table taobao_color{nowtime} (id int(5) NOT NULL auto_increment,daxiao varchar(20),yanse varchar (20),PRIMARY KEY (`id`))'''.format(nowtime=stime)

        self.cur.execute(sql_1)
        self.cur.execute(sql_2)
        tableName={}
        tableName["taobao_pl"]="taobao_pl"+stime
        tableName["taobao_color"]="taobao_color"+stime
        return tableName

gf=GetRank()
try:
    gf.click_ljpj()
    name = gf.create_table()
    i=1
    while (1):
        gf.get_pl(name["taobao_pl"])
        gf.get_color(name["taobao_color"])
        flag = gf.is_next_click()
        if flag:
            pass
        else:
            break
        gf.click_next()
        gf.lg.info("第{i}页".format(i=i))
        i+=1


except Exception as e:
    gf.lg.error(e)
finally:
    gf.close_driver()
    gf.db.close_connect()
