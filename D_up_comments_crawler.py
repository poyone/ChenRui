import hashlib
import threading
import time

from C_comments_crawler import Crawler
from B_config import selenium_config
from Z_libs import DriverInitialize, SessionInteractor, format_date, removeBlank

task = []
class Up_Crawler:
    def __init__(self, upid) -> None:
        self.driver = DriverInitialize(login_site=selenium_config['login_site'],
                                       profile_path=selenium_config['profile_path']).quit_browser()
        self.session = SessionInteractor(driver=self.driver).return_session()


        self.upid = upid
        self.vlist = []
    def construct_url(self, pn):
    
        wts = int(time.time())
        string = f"keyword=&mid={self.upid}&order=pubdate&order_avoided=true&platform=web&pn={pn}&ps=30&tid=0&web_location=1550101&wts={wts}"+'ea1db124af3c7062474693fa704f4ff8'
        md5_hash = hashlib.md5()
        md5_hash.update(string.encode('utf-8'))
        w_rid =  str(md5_hash.hexdigest())
        url = f'https://api.bilibili.com/x/space/wbi/arc/search?mid={self.upid}&ps=30&tid=0&pn={pn}&keyword=&order=pubdate&platform=web&web_location=1550101&order_avoided=true&w_rid={w_rid}&wts={wts}'

        return url
    
    def close(self):
        self.session.close()
        self.driver.close()

    def GetUpAllBVid(self):
        pn = 1
        while True:       
            url = self.construct_url(pn)
            pn += 1
            
            time.sleep(0.3)
            response = self.session.get(url=url).json()


            if response['data']['list']['vlist']:
                vlist = response['data']['list']['vlist']
                self.vlist.extend(vlist)
            else:
                break


def Get_Crawler(avid,bvid):
    crawler = Crawler(avid, file_name=f'{bvid}.csv')
    crawler.crawl_main_replies()
    crawler.close()
    

if __name__ == '__main__':

    #通过UP的ID爬取其所有视频的BV号
    crawler = Up_Crawler(651386960)
    crawler.GetUpAllBVid()
    crawler.close()
    
    vlist = [(item['aid'],item['bvid'])for item in crawler.vlist]
    threads = []
    for item in vlist:
        t = threading.Thread(target=Get_Crawler(item[0],item[1]))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

    print('----------------------爬取完毕-------------------------')




