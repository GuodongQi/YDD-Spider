# -- coding: utf-8 --
import requests
import json
import MySQLdb
import time


def main():

    r = my_session.post(url_search, headers=header, data=json.dumps(search_token))
    res = json.loads(r.text)['result']["entry"]

    # create table all_post (
    #         id     int auto_increment,
    #         time  datetime,
    #         sns_id  char(30),
    #         nickname char(50),
    #         content  text,
    #         image text,
    #         primary key (id)) character set = utf8mb4;
    post_cursor = ydd_post.cursor()
    user_cursor = ydd_user.cursor()

    for i in res[::-1]:
        timestamp = i['timestamp']
        sns_id = i['sns_id']
        # insert into ydd_post
        content = i['content']
        nickname = i['nickname']
        images = [j['big_url'] for j in i['content_extra']['image']]

        sql = "select sns_id from all_post order by id desc limit 20 "
        post_cursor.execute(sql)
        top20 = post_cursor.fetchall()
        top20 = [j[0] for j in top20]
        if sns_id not in top20:
            # insert
            sql = "insert into all_post(time,sns_id,nickname,content,image) values " \
                  "(FROM_UNIXTIME({}),'{}','{}','{}','{}')".format(timestamp, sns_id, nickname, content,
                                                                   ' '.join(images))
            post_cursor.execute(sql)
            ydd_post.commit()
            print(sql)

        # insert into ydd_user
        # id to nickname
        # create table id2name(
        #         id     int auto_increment,
        #         nickname char(50),
        #         primary key (id)) character set = utf8mb4;

        comments = i["comments"]
        for comment in comments:
            nickname = comment["nickname"].lower()
            timestamp = comment['time']
            sns_id = comment['sns_id']
            comment_id = comment['comment_id']
            # insert into ydd_post
            content = comment['content']
            # 1. first we check whether exist nicknamed in id2name table
            sql = "select * from id2name where nickname='{}';".format(nickname)
            user_cursor.execute(sql)
            res = user_cursor.fetchall()
            if not len(res):  # nickname is not existed
                sql = "insert into id2name(nickname)values('{}');".format(nickname)
                user_cursor.execute(sql)
                ydd_user.commit()
                sql = "select id from id2name where id=(select last_insert_id());"
                user_cursor.execute(sql)
                name_id = user_cursor.fetchall()[0][0]
                # create name_id table
                sql = "create table `n{:0>7}` (" \
                      "id  int auto_increment," \
                      "nickname  char(50)," \
                      "time  datetime," \
                      "comment_id  char(30), " \
                      "sns_id  char(30), " \
                      "content  text, " \
                      "image text, " \
                      "primary key (id)) character set = utf8mb4;".format(name_id)
                user_cursor.execute(sql)
                ydd_user.commit()
            else:
                name_id = res[0][0]

            # 2 insert into name_table
            # 2.1 check whether comment has been existed
            sql = "select comment_id from `n{:0>7}` order by id desc limit 100 ".format(name_id)
            user_cursor.execute(sql)
            com_ids = [j[0] for j in user_cursor.fetchall()]
            if comment_id not in com_ids:
                # 2.2 not existed, insert comments
                sql = "insert into `n{:0>7}`(nickname,time,comment_id,sns_id,content,image) values (" \
                      "'{}',FROM_UNIXTIME({}),'{}','{}','{}','{}')".format(name_id, nickname, timestamp, comment_id,
                                                                           sns_id, content, ' '.join(images))
                user_cursor.execute(sql)
                ydd_user.commit()


if __name__ == '__main__':
    my_session = requests.Session()
    header = {
        "Host": "wxapp.uboxs.com",
        "Connection": "keep-alive",
        "Content-Length": "272",
        "charset": "utf-8",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; MIX 2S Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.62 XWEB/2571 MMWEBSDK/200601 Mobile Safari/537.36 MMWEBID/6234 MicroMessenger/7.0.16.1700(0x27001035) Process/appbrand0 WeChat/arm64 NetType/WIFI Language/zh_CN ABI/arm64",
        "content-type": "application/json",
        "Accept-Encoding": "gzip, compress, br, deflate",
        "Referer": "https://servicewechat.com/wxfff13bde6d027458/239/page-frame.html"
    }
    url_search = "https://wxapp.uboxs.com/timeline/search"

    search_token = {
        "duo_session": "",  # your duo_session
        "group_id": 4,
        "keyword": "",
        "require_tag": False,
        "limit": 20,
        "page": 1,
        "seed": '',  # your seed
        "duo_token": ""  # your duo_token
    }
    ydd_post = MySQLdb.connect("localhost", "root", "123456", "ydd_post", charset='utf8mb4')
    ydd_user = MySQLdb.connect("localhost", "root", "123456", "ydd_users", charset='utf8mb4')

    while True:
        main()
        time.sleep(60)
