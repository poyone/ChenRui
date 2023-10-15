import csv
import hashlib
import os
import time
from dataclasses import dataclass

from attr import dataclass

from B_config import selenium_config
from Z_libs import DriverInitialize, SessionInteractor, format_date


@dataclass
class Comment:
    UserName : str
    Date : str
    Likes : int
    Content : str
    
class Crawler:
    
    def __init__(self, oid, file_name) -> None:
        
        self.driver = DriverInitialize(login_site=selenium_config['login_site'],
                                       profile_path=selenium_config['profile_path']).quit_browser()
        self.session = SessionInteractor(driver=self.driver).return_session()
        
        self.oid = oid
        self.file_path = f'Comments/{file_name}'
        
        if os.path.exists('Comments'):
            pass
        else:
            os.makedirs('Comments')

        
    def yield_comment(self, data):

        comment = Comment(
            data['member']['uname'],
            format_date(data['ctime']),
            data['like'],
            data['content']['message'],
        )
        
        with open(self.file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if os.path.getsize(self.file_path) == 0:
                writer.writerow([key for key in vars(comment).keys()])
                
            writer.writerow([getattr(comment, key) for key in vars(comment).keys()])

    def construct_url(self, m_pn):
        
            wts = int(time.time())
            string = f"mode=3&oid={self.oid}&pagination_str=%7B%22offset%22%3A%22%7B%5C%22type%5C%22%3A1%2C%5C%22direction%5C%22%3A1%2C%5C%22data%5C%22%3A%7B%5C%22pn%5C%22%3A{m_pn}%7D%7D%22%7D&plat=1&type=1&web_location=1315875&wts={wts}"+'ea1db124af3c7062474693fa704f4ff8'
            md5_hash = hashlib.md5()
            md5_hash.update(string.encode('utf-8'))
            w_rid =  str(md5_hash.hexdigest())
            url = f'https://api.bilibili.com/x/v2/reply/wbi/main?oid={self.oid}&&type=1&mode=3&pagination_str=%7B%22offset%22:%22%7B%5C%22type%5C%22:1,%5C%22direction%5C%22:1,%5C%22data%5C%22:%7B%5C%22pn%5C%22:{m_pn}%7D%7D%22%7D&plat=1&web_location=1315875&w_rid={w_rid}&wts={wts}'

            return url
        
    def crawl_inner_replies(self, root):
        pn = 1
        # exhaust replies
        while True:

            url = f'https://api.bilibili.com/x/v2/reply/reply?oid={self.oid}&type=1&root={root}&ps=20&pn={pn}&web_location=333.788'
            pn += 1
            response = self.session.get(url).json()
            
            if response['data']['replies']:
                for reply in response['data']['replies']:
                    self.yield_comment(reply)
            else:
                break

            
    def crawl_main_replies(self):
        m_pn = 1
        #  for topped replies
        top = True

        # exhaust replies
        while True:
            url = self.construct_url(m_pn=m_pn)
            response = self.session.get(url).json()
            
            # top part
            if top:
                top = False
                
                if response['data']['top_replies']:
                    # top layer
                    for top_reply in response['data']['top_replies']:
                        self.yield_comment(top_reply)

                        # inner layer
                        if top_reply['replies']:
                            for reply in top_reply['replies']:
                                rpid = reply['rpid']
                                self.crawl_inner_replies(root=rpid)
            
            # normal part
            if response['data']['replies']:
                for normal_reply in response['data']['replies']:
                    self.yield_comment(reply)
                    
                    if normal_reply['replies']:
                        for reply in normal_reply['replies']:
                            rpid = reply['rpid']
                            self.crawl_inner_replies(root=rpid)    
            else:
                break
            
            m_pn = m_pn+1
            
            
if __name__ == '__main__':
    crawler = Crawler(oid=961191813, file_name='test.csv')
    crawler.crawl_main_replies()
