#coding=utf-8
'''
Created on 2017-4-7

@author: chowpeng
'''

import os 
import urllib3
from bs4 import BeautifulSoup
import cPickle as pickle
import os
import traceback
http = urllib3.PoolManager(100)
site="http://www.dbestwatches.com/"
url="http://www.dbestwatches.com/index.php?main_page=index&cPath=70_321"
dir=r"H:\smt\products\Replicawatches"


def getTopCate(url):
    try:
        f1=open("temp.pk1","rb+")
        top_cate_url__dict=pickle.load(f1)
    except IOError,e:
        top_cate_url__dict={}
    except EOFError,e:
        top_cate_url__dict={}


    if not top_cate_url__dict:
    
        r=http.request("GET", url)
        if r.status==200:
            html_doc=r.data
            
            soup=BeautifulSoup(html_doc,'html.parser')
            html_cate_obj=soup.find("ul",class_="v-left-category")
            
            top_cate_obj_lst = html_cate_obj.find_all("li",class_="category-top")
            
            
            top_cate_url__dict ={}
            
            
            for i in top_cate_obj_lst:
    
                top_cate_name=i.find("a").get_text()
                top_cate_url__dict[top_cate_name]=i.find("a").get("href")
            
            pickle.dump(top_cate_url__dict, f1)
        else:
            print "response status %s" % r.status
        print "get topcate url is ok"
    if f1:
        f1.close()
    
    return top_cate_url__dict


def getSubCate(top_cate_url_d):
    try:
        f2=open("temp.pk2","rb+")
        sub_cate_url__dict=pickle.load(f2)
    except IOError,e:
        sub_cate_url__dict={}
    except EOFError,e:
        sub_cate_url__dict={}

        
    if not sub_cate_url__dict:
        sub_cate_url__dict={}
        
        for k,v in top_cate_url_d.iteritems():
            r=http.request("GET",v)
            if r.status==200:
                subcate_soup=BeautifulSoup(r.data,'html.parser')
                html_subcate_obj=subcate_soup.find("ul",class_="productsTable")
                subcate_obj_lst=html_subcate_obj.find_all("div",class_="name")
                temp_sub_cate={}
                
                for i in subcate_obj_lst:
                    subcate_name=i.get_text()
                    subcate_url=i.find("a").get("href")
                    temp_sub_cate[subcate_name]=subcate_url
                
                sub_cate_url__dict[k]=temp_sub_cate
                print sub_cate_url__dict[k]
                print "get %s from %s is ok" % (k,v)
            else:
                print "%s response %s " % (v,r.status)

        pickle.dump(sub_cate_url__dict, f2)
        print "get subcate url is ok"
    if f2:
        f2.close()
        
    return sub_cate_url__dict


def getProductsUrl(sub_cate_url__dict):
    
    for topcatename,subcate in sub_cate_url__dict.iteritems():
        
        for subcatename,subcateurl in subcate.iteritems():
            subcate_prodcuct_urls=[]
            
            if "Watch Boxes"==topcatename:
                print subcateurl
                subcate_prodcuct_urls.append(subcateurl)
                subcate[subcatename]=subcate_prodcuct_urls
                continue
            
            r=http.request("GET",subcateurl,redirect=False)
            if r.status==302:
                subcate_prodcuct_urls.append(r.headers.get("Location")) 
            elif r.status==200:
                p_soup=BeautifulSoup(r.data,'html.parser')
                html_p_obj=p_soup.find("ul",class_="productsTable")
                p_obj_lst=html_p_obj.find_all("div",class_="name")
                for i in p_obj_lst:
                    p_url=i.find("a").get("href")
                    subcate_prodcuct_urls.append(p_url)
                
                    
                print "get first page ok from %s" % subcateurl
                #检查是否有分页，得到每一页的数据
                html_page_obj=p_soup.find("div",class_="page")
                p_page_url_lst=[i.get("href") for i in html_page_obj.find_all("a")]
                
                for p_page_url in p_page_url_lst:
                    r=http.request("GET",p_page_url,redirect=False)
                    if r.status==200:
                        p_soup=BeautifulSoup(r.data,'html.parser')
                        html_p_obj=p_soup.find("ul",class_="productsTable")
                        p_obj_lst=html_p_obj.find_all("div",class_="name")
                        for i in p_obj_lst:
                            p_url=i.find("a").get("href")
                            subcate_prodcuct_urls.append(p_url)
                        print "get page ok from %s" % p_page_url
                    else:
                        print "%s response %s" % (subcateurl,r.status)
                    continue
                
            else:
                print "%s response %s" % (subcateurl,r.status)
                continue
            
            print "get p_urls ok from %s" % subcateurl
            subcate[subcatename]=subcate_prodcuct_urls
        
    try:
        f=open("temp.pk3","wb+")
        pickle.dump(sub_cate_url__dict, f)
        print "get all p_urls ok!"
    except Exception,e:
        pass
    finally:
        if f:
            f.close()




def storeProductPic(dir):
    try:
        p_urls_dict=None
        f=open("temp.pk3","rb+")
        p_urls_dict=pickle.load(f)
    except Exception,e:
        pass
    finally:
        if f:
            f.close()
            
    for topcatename,subcate in p_urls_dict.iteritems():
        if topcatename in ["Watch Tables","Audemars Piguet","Bell and Ross","Hublot","IWC","Panerai",
                           "Rolex","Patek Philippe","Cartier","Watch Boxes","Tag Heuer","Vacheron Constantin","Franck Muller"]:
            print "topcatename",topcatename
            continue
#        if topcatename not in ["IWC"]:
#            print "topcatename",topcatename
#            continue
        
        topcatenamedir=os.path.join(dir,topcatename)
        if not os.path.exists(topcatenamedir):
            os.mkdir(topcatenamedir)
        for subcatename,p_url_lst in subcate.iteritems():
            if subcatename in ["De Ville","Speedmaster","Seamaster","Planet Ocean",]:
                print "subcatename",subcatename
                continue
            
            subcatenamedir = os.path.join(topcatenamedir,subcatename)
            if not os.path.exists(subcatenamedir):
                os.mkdir(subcatenamedir)
            for p_url in p_url_lst:
                try:
                    r=http.request("GET",p_url)
                    if r.status==200:
                        p_soup=BeautifulSoup(r.data,'html.parser')
                        need_text=""
                        #产品名字
                        p_name=p_soup.find("h2",class_="productName").get_text()
                        need_text+=(p_name+"\n\n")
                        #产品价格
                        p_price_soup=p_soup.find("div",class_="productPrice")
                        p_price_0=p_price_soup.find("div",class_="was").get_text()
                        need_text+=(p_price_0+"\n\n")
                        p_price_1=p_price_soup.find("div",class_="now").get_text()
                        need_text+=(p_price_1+"\n\n\n")
                        
                        #属性信息
                        p_attr_html=p_soup.find("div",class_="attrtable").prettify()
                        need_text+=p_attr_html
                        
                        #创建产品目录
                        p_id=p_url.split("=")[-1]
                        p_dir=os.path.join(subcatenamedir,str(p_id))
                        if not os.path.exists(p_dir):
                            os.mkdir(p_dir)
                            
                        #存储文本信息
                        with open(os.path.join(p_dir,"inform.txt"),"w") as fw:
                            fw.write(need_text)
                        
                        #图片元素
                        html_pic_obj=p_soup.find("div",class_="products_description_images")
                        html_pic_obj_lst=html_pic_obj.find_all("img")
                        pic_url_lst=["".join((site,i.get("src")))for i in html_pic_obj_lst]
                        
                        #下载图片
                        for img_url in pic_url_lst:
                            img_name=img_url.split('/')[-1]
                            res_img=http.request("GET",img_url)
                            with open(os.path.join(p_dir,img_name),"wb") as fg:
                                fg.write(res_img.data)
                            print "Download the pic ok from %s" % img_url
                        
                    else:
                        print "%s response %s" % (p_url,r.status)
                    
                    print "download product ok from %s" % p_url
                except Exception,e:
                    print traceback.format_exc()
                    print "download product error from %s : %s" % (p_url,e.message)
                    continue
        print "%s Finish OK" % topcatename
            

if __name__=="__main__":
#    top_cate_url_d = getTopCate(url)
#    sub_cate_url__dict=getSubCate(top_cate_url_d)
#    getProductsUrl(sub_cate_url__dict)
#    r=http.request("GET","http://www.dbestwatches.com/index.php?main_page=index&cPath=190_360",redirect=False)
#    print r.headers.get("Location")
    storeProductPic(dir)

    
    
    