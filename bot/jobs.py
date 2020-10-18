import requests
import random
from bs4 import BeautifulSoup
import re
import time
import os
from . import models
from apscheduler.schedulers.background import BackgroundScheduler



db_url = os.environ.get("DATABASE_URL")



scheduler = BackgroundScheduler({
    'apscheduler.jobstores.default': {
        'type': 'sqlalchemy',
        'url': db_url
    },
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '1',
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
        if self.session.cookies.get("session") == None:
            while len(self.session.cookies.get("session", "")) < 5:
                r = self.session.post("https://www.nairaland.com/do_login", self.login_details)
                self.session.get(r.url)
                self.session_id = self.session.cookies.get('session')
                print(self.session.cookies.get('session'))
                print(self.session.cookies)
                self.reply['session'] = self.session_id







    
    def spam_thread(self):
        '''Post reply'''
        self.reply["body"] = self.body + " "*random.randint(0,99)
        r = self.session.post("https://www.nairaland.com/do_newpost", self.reply)
        print(f" ......  {self.reply}")
        print(r.text)
            






class BoardReplyJob_():
    def __init__(self, login_details,  board_uri, reply, minutes):
        self.board_uri = board_uri
        self.reply = {'title':'Trump MAGA 2020', 'max_post':'39', 'body':reply}
        self.body = reply
        self.login_details = login_details
        self.session = requests.Session()
        self.session_id = ''
        self.logged_in = False
        self.login()
        self.minutes = minutes



    def login(self):
        if self.session.cookies.get("session") == None:
            while len(self.session.cookies.get("session", "")) < 5:
                r = self.session.post("https://www.nairaland.com/do_login", self.login_details)
                self.session.get(r.url)
                self.session_id = self.session.cookies.get('session')
                self.reply['session'] = self.session_id



    def get_topics(self):
        '''A function to get all topic IDs on page'''
        topics = []
        r = self.session.get(self.board_uri)
        soup = BeautifulSoup(r.text, 'html.parser')
        links=soup.findAll('a', {'href':re.compile(r'\/\d\d\d\d\d\d\d\/[a-z-]')})

        for link in links:
            x = re.search('\d\d\d\d\d\d\d+',link.get('href'))
            if type(x) != re.Match:
                continue
            if not x.group() in topics:
                topics.append(x.group())
        return topics




    def spam_board(self):
        '''Post reply'''
        self.reply["body"] = self.body + " "*random.randint(0,99)
        topics = self.get_topics()
        for topic in topics:
            queryset = models.DoneBJTopics.objects.filter(topic = topic)
            if len(queryset) == 0:
                self.reply['topic'] = topic
                print(topic)
                r = self.session.post("https://www.nairaland.com/do_newpost", self.reply)
                print(f" ......  {topic}")
                print("Done")
                self.reply['body'] += '  '
                d = models.DoneBJTopics.objects.create(
                    topic = topic
                    )
                d.save()
                time.sleep(self.minutes * 60)
        models.DoneBJTopics.objects.all().delete()

    


class FrontPageMonitorJob_():
    def __init__(self, login_details, reply):
        self.board_uri = 'https://www.nairaland.com/'
        self.reply = {'title':'Trump MAGA 2020', 'max_post':'39', 'body':reply}
        self.body = reply
        self.login_details = login_details
        self.session = requests.Session()
        self.session_id = ''
        self.logged_in = False
        self.login()




    def login(self):
        if self.session.cookies.get("session") == None:
            while len(self.session.cookies.get("session", "")) < 5:
                r = self.session.post("https://www.nairaland.com/do_login", self.login_details)
                self.session.get(r.url)
                self.session_id = self.session.cookies.get('session')
                print(self.session.cookies.get('session'))
                print(self.session.cookies)
                self.reply['session'] = self.session_id





    def get_topics(self):
        '''A function to get all topic IDs on page'''
        topics = []
        r = self.session.get(self.board_uri)
        soup = BeautifulSoup(r.text, 'html.parser')
        links=soup.findAll('a', {'href':re.compile(r'\/\d\d\d\d\d\d\d\/[a-z-]')})

        for link in links:
            x = re.search('\d\d\d\d\d\d\d+',link.get('href'))
            if type(x) != re.Match:
                continue
            if not x.group() in topics:
                topics.append(x.group())
        del topics[0]
        return topics[0]


    def spam_frontpage(self):
        '''Post reply'''
        self.reply["body"] = self.body + " "*random.randint(0,99)
        topic = self.get_topics()
        queryset = models.DoneFPTopics.objects.filter(topic = topic)
        if len(queryset) == 0:
            self.reply['topic'] = topic
            print(self.reply)
            print(self.session.cookies)
            r = self.session.post("https://www.nairaland.com/do_newpost", self.reply)
            print(f" ......  {topic}")
            print(r.text)
            self.reply['body'] += '  '
            done = models.DoneFPTopics.objects.create(
                    topic = topic
                    )
            done.save()




scheduler.start()
print('Scheduler started')
