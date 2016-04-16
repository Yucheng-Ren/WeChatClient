# -*- coding:utf-8 -*-

import json

from wechatclient.WeChatClient import Wechatclient
from wechatclient.log import Log


body_text = """
<xml>
<ToUserName><![CDATA[touser]]></ToUserName>
<FromUserName><![CDATA[fromuser]]></FromUserName>
<CreateTime>1405994593</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[wechat]]></Content>
<MsgId>6038700799783131222</MsgId>
</xml>
"""

my_test_open_id = 'ovkM0wsqSIPHKUmlwIcEZ1FZA0No'
princess_id = 'ovkM0wuHilqqVdXfOPtanayI3CSk'

open_ids=[my_test_open_id,princess_id]
my_open_id = 'oiqcauL3fancglKjGkjhWOsrg0MQ'
image_id = 'BYV6dv4-NwbUV68HsObRYL7irDEF_UO8EQPZ-MjEo0a4p4_b13JXYVrGjQjZIaaY'
wechat = Wechatclient()


def parse_data_test():
    wechat.parse_data(body_text)
    message = wechat.get_message()
    response = None
    if message.type == 'text':
        if message.content == 'wechat':
            response = wechat.response_text(u'^_^')
        else:
            response = wechat.response_text(u'文字')
    elif message.type == 'image':
        response = wechat.response_text(u'图片')
    else:
        response = wechat.response_text(u'未知')

    # 现在直接将 response 变量内容直接作为 HTTP Response 响应微信服务器即可，此处为了演示返回内容，直接将响应进行输出
    print response


def get_user_info(open_id):
    return wechat.get_user_info(open_id)


def get_feng():
    with open('open_ids') as f:
        res = json.load(f)
        ids = res['data']['openid']
        for _id in ids:
            data = get_user_info(_id)
            if data['nickname'] == u'峰':
                return data


def send_text_message(open_id, content):
    return wechat.send_text_message(open_id, content)


def send_image_message(open_id, image_id):
    return wechat.send_image_message(open_id, image_id)


def upload_media_test():
    with open('/Users/Mr_ren/Pictures/kenting.jpg') as f:
        return wechat.upload_media('image', f)


def send_other_material():
    with open('/Users/Mr_ren/Pictures/kenting.jpg') as f:
        return wechat.upload_permanent_material('image', f)


def get_followers():
    with open('open_ids','w+') as f:
        result = wechat.get_followers()
        json.dump(result, f)


def send_template_message(open_id):
    template_data={
        'first': {
            'value': '您好, 欢迎关注测试账号',
            'color': '#173177'
        },
        'key1': {
            'value': 'biu~ biu~',
            'color': '#173177'
        },
        'key2': {
            'value': '吐槽',
            'color': '#173177'
        },
        'remark': {
            'value': '欢迎留言, 概不回复~',
            'color': '#173177'
        }
    }
    return wechat.send_template_message(open_id, 'd6DrGW2A4pDWs0jTLBOb2zTFmLfjxBbTwLWuJE1RH6s', template_data, url='http://sogou.com')


def create_menu():
    menu_data = {
        'button': [
            {
                'type': 'click',
                'name': '今日歌曲',
                'key': 'V1001_TODAY_MUSIC'
            },
            {
                'type': 'click',
                'name': '歌手简介',
                'key': 'V1001_TODAY_SINGER'
            },
            {
                'name': '菜单',
                'sub_button': [
                    {
                        'type': 'view',
                        'name': '搜索',
                        'url': 'http://www.soso.com/'
                    },
                    {
                        'type': 'view',
                        'name': '视频',
                        'url': 'http://v.qq.com/'
                    },
                    {
                        'type': 'click',
                        'name': '赞一下我们',
                        'key': 'V1001_GOOD'
                    }
                ]
            }
        ]}
    return wechat.create_menu(menu_data)


def main():
    response = send_text_message('oiqcauAjqYb4PogBxn-MEPyPH4os', 'hello')
    # response = get_user_info(my_open_id)
    # response = get_feng()
    # print upload_media_test()
    # response = send_image_message(my_test_open_id, '8Lj7SePZAQ9ku2QMGAbkE0y40S0nu7ww8CglJoZIX1U')
    # print wechat.send_message_by_group(0, message_type='image', media_id=image_id)
    # response = get_feng()
    # print wechat.send_message_by_openids(open_ids, message_type='image', media_id=image_id)
    # print wechat.move_user_by_openids(open_ids, '1')
    # response = wechat.delete_group('100')
    # response = wechat.create_group('new_group')
    # response = wechat.set_user_remark(my_test_open_id, 'cool guy')
    # response = create_menu()
    # response = send_template_message(my_test_open_id)
    # response = wechat.convert_shorturl('http://sogou.com')
    # response = send_other_material()
    # response = wechat.get_permanent_material_list('image', 0, 2)
    Log.info(response)
    # Log.info(wechat.get_users_info(open_ids))


if __name__ == '__main__':
    main()
