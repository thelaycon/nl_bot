import requests
import random
from bs4 import BeautifulSoup
import re
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler



db_url = os.environ.get("DATABASE_URL")



scheduler = BackgroundScheduler({
    'apscheduler.jobstores.default': {
        'type': 'sqlalchemy',
        'url': db_url
    },
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '3',
    'apscheduler.timezone': 'UTC',
})


class ThreadReplyJob_():
    def __init__(self, login_details,  thread_title, topic_code, reply):
        self.reply = {'title':thread_title, 'topic':str(topic_code), 'body':reply, 'max_post':'35',}
        self.body = reply
        self.login_details = login_details
        self.session = requests.Session()
        self.session_id = ''
        self.logged_in = False
        self.login()



    def login(self):
        while True:
            r = self.session.post("https://www.nairaland.com/do_login", self.login_details)
            if not 'Set-Cookie' in r.headers:
                print("logged-in")
                self.session_id = self.session.cookies.get('session')
                self.reply['session'] = self.session_id
                self.logged_in = True
                break



    
    def spam_thread(self):
        '''Post reply'''
        self.reply["body"] = self.body + " "*random.randint(0,99)
        r = self.session.post("https://www.nairaland.com/do_newpost", self.reply)
        print(f" ......  {self.reply}")
        print(r.text)
            






class BoardReplyJob_():
    def __init__(self, login_details,  board_uri, reply):
        self.board_uri = board_uri
        self.reply = {'title':'Trump MAGA 2020', 'max_post':'39', 'body':reply}
        self.body = reply
        self.login_details = login_details
        self.session = requests.Session()
        self.session_id = ''
        self.topics = []
        self.logged_in = False
        self.login()
        self.get_topics()



    def login(self):
        while True:
            r = self.session.post("https://www.nairaland.com/do_login", self.login_details)
            if not 'Set-Cookie' in r.headers:
                print("logged-in")
                self.session_id = self.session.cookies.get('session')
                self.reply['session'] = self.session_id
                self.logged_in = True
                break



    def get_topics(self):
        '''A function to get all topic IDs on page'''
        r = self.session.get(self.board_uri)
        soup = BeautifulSoup(r.text, 'html.parser')
        links=soup.findAll('a', {'href':re.compile(r'\/\d\d\d\d\d\d\d\/[a-z-]')})

        for link in links:
            x = re.search('\d\d\d\d\d\d\d+',link.get('href'))
            if type(x) != re.Match:
                continue
            if not x.group() in self.topics:
                self.topics.append(x.group())
        self.topics = iter(self.topics)




    def spam_board(self):
        '''Post reply'''
        self.reply["body"] = self.body + " "*random.randint(0,99)  
        try:
            topic = next(self.topics)
            self.reply['topic'] = topic
            print(topic)
            print(self.reply)
            r = self.session.post("https://www.nairaland.com/do_newpost", self.reply)
            print(f" ......  {topic}")
            print(r.text)
            self.reply['body'] += '  '
        except StopIteration:
            self.topics = self.get_topics()
            topic = next(self.topics)
            self.reply['topic']
            r = self.session.post(self.board_uri, self.reply)
            print(r.text)
            print(f" ......  {topic}")

    


class FrontPageMonitorJob_():
    def __init__(self, login_details, reply):
        self.board_uri = 'https://www.nairaland.com/'
        self.reply = {'title':'Trump MAGA 2020', 'max_post':'39', 'body':reply}
        self.body = reply
        self.login_details = login_details
        self.session = requests.Session()
        self.session_id = ''
        self.topics = []
        self.done_topics = []
        self.logged_in = False
        self.login()
        self.get_topics()



    def login(self):
        while True:
            r = self.session.post("https://www.nairaland.com/do_login", self.login_details)
            if not 'Set-Cookie' in r.headers:
                print("logged-in")
                self.session_id = self.session.cookies.get('session')
                self.reply['session'] = self.session_id
                self.logged_in = True
                break



    def get_topics(self):
        '''A function to get all topic IDs on page'''
        r = self.session.get(self.board_uri)
        soup = BeautifulSoup(r.text, 'html.parser')
        links=soup.findAll('a', {'href':re.compile(r'\/\d\d\d\d\d\d\d\/[a-z-]')})

        for link in links:
            x = re.search('\d\d\d\d\d\d\d+',link.get('href'))
            if type(x) != re.Match:
                continue
            if not x.group() in self.topics:
                self.topics.append(x.group())
        del self.topics[0]


    def spam_frontpage(self):
        '''Post reply'''
        self.reply["body"] = self.body + " "*random.randint(0,99)     
        if not self.topics[0] in self.done_topics:
            topic = self.topics[0]
            self.reply['topic'] = topic
            print(self.reply)
            print(self.session.cookies)
            r = self.session.post("https://www.nairaland.com/do_newpost", self.reply)
            print(f" ......  {topic}")
            print(r.text)
            self.reply['body'] += '  '
            self.done_topics.append(topic)
        self.topics = []
        self.get_topics()




scheduler.start()
print('Scheduler started')
