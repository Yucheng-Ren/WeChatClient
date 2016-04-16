# -*- coding:utf-8 -*-
import json
import urllib
import urllib2

from wechat_sdk import WechatConf, WechatBasic

from config import APPID, APPSECRET, ENCRYPT_MODE, TOKEN
from log import Log


# 将 access_token 缓存至本地文件
def get_access_token_function():
    with open('access_token', 'w+') as f:
        try:
            data = json.load(f)
        except Exception, e:
            url = 'https://api.weixin.qq.com/cgi-bin/token'
            param = {'grant_type': 'client_credential',
                     'appid': APPID,
                     'secret': APPSECRET
                     }
            param = urllib.urlencode(param)
            req = urllib2.Request(url, param)
            response = urllib2.urlopen(req)
            the_page = response.read()
            result = json.loads(the_page)
            return tuple([result['access_token'], result['expires_in']])
        else:
            return tuple([data.get('access_token'), data.get('expires_in')])


def set_access_token_function(access_token, access_token_expires_at):
    data = {'access_token': access_token,
            'expires_in': access_token_expires_at}
    with open('access_token', 'w+') as f:
        json.dump(data, f)


def get_conf():
    conf = WechatConf(
        token=TOKEN,
        appid=APPID,
        appsecret=APPSECRET,
        encrypt_mode=ENCRYPT_MODE,
        # encoding_aes_key=ENCODING_AES_KEY        ＃ENCRYPT_MODE 为 normal
        # 时不需要传入
        access_token_getfunc=get_access_token_function,
        access_token_setfunc=set_access_token_function,
    )
    return conf


class Wechatclient(WechatBasic):
    '''
    继承了 WechatBasic 类, 扩展了 WechatBasic 类没有实现的函数, 比如群发功能.
    自动维护 access_token 等
    '''

    def __init__(self):
        super(Wechatclient, self).__init__(conf=get_conf())

    def send_message_by_group(self, group_id, message_type='text', media_id=None, content=None):
        '''
        根据分组进行消息群发
        :param media_id: 如果类型为 media 类型, 此处要传入 media_id 参数
        :param content: 如果类型为 'text' 此处要传入 内容参数
        :param group_id: 需要发送分组的 id
        :param message_type: 信息类型,包括: ('text', 'mpnews', 'voice', 'image', 'mpvideo')
        如果是 mpvideo type 需要先调用 upload_mpvideo 进行 media_id 转换
        :return: 微信服务器返回的 JSON 数据
        {
            'errcode':0,
            'errmsg':'send job submission success',
            'msg_id':34182,
            'msg_data_id': 206227730
        }
        :官方 API 文档:http://mp.weixin.qq.com/wiki/15/40b6865b893947b764e2de8e4a1fb55f.html
        '''
        if message_type == 'text':
            data = {
                'filter': {
                    'is_to_all': False,
                    'group_id': group_id
                },
                'text': {
                    'content': content
                },
                'msgtype': 'text'
            }
        elif message_type == 'mpnews' or message_type == 'voice' or message_type == 'image' or message_type == 'mpvideo':
            data = {
                'filter': {
                    'is_to_all': False,
                    'group_id': group_id
                },
                message_type: {
                    'media_id': media_id
                },
                'msgtype': message_type
            }
        else:
            Log.error('发送类型不支持!')
            raise ValueError('unknown type')
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/message/mass/sendall',
            data=data
        )

    def upload_mpvideo(self, media_id, title, description):
        '''
        :param media_id: 此处 media_id 需通过基础支持中的上传下载多媒体文件来得到, 即 .upload_media(media_type, media_file, extension='')
        详情: http://wechat-python-sdk.com/official/material/
        :param title: 标题
        :param description: 描述
        :return: 微信服务器返回的 JSON 数据
        {
            'type':'video',
            'media_id':'IhdaAQXuvJtGzwwc0abfXnzeezfO0NgPK6AQYShD8RQYMTtfzbLdBIQkQziv2XJc',
            'created_at':1398848981
        }
        此处返回的 media_id 可用于群发信息
        '''
        return self.request.post(
            url='https://file.api.weixin.qq.com/cgi-bin/media/uploadvideo',
            data={
                'media_id': media_id,
                'title': title,
                'description': description
            }
        )

    def send_message_by_openids(self, open_ids, message_type='text', media_id=None, content=None):
        '''
        根据 open_id list 进行消息群发
        :param media_id: 当类型为 media 类型时, 要传入 media_id 参数
        :param content: 当类型为 'text' 时, 要传入 content 参数
        :param open_ids: list 类型的参数, 每一项为一个 open_id
        :param message_type: 信息类型,包括: ('text', 'mpnews', 'voice', 'image', 'mpvideo')
        如果是 mpvideo type 需要先调用 upload_mpvideo 进行 media_id 转换
        :return: 微信服务器返回的 JSON 数据
        {
            'errcode':0,
            'errmsg':'send job submission success',
            'msg_id':34182,
            'msg_data_id': 206227730
        }
        '''
        if message_type == 'text':
            data = {
                'touser': open_ids,
                'text': {
                    'content': content
                },
                'msgtype': 'text'
            }
        elif message_type == 'image' or message_type == 'mpnews' or message_type == 'mpvideo' or message_type == 'voice':
            data = {
                'touser': open_ids,
                message_type: {
                    'media_id': media_id
                },
                'msgtype': message_type
            }
        else:
            Log.error('发送类型不支持!')
            raise ValueError('unknown type')
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/message/mass/send',
            data=data
        )

    def group_send_status(self, msg_id):
        '''
        群发消息状态
        :param msg_id: 群发消息后返回的消息 id
        :return: JSON 数据
        {
            "msg_id":201053012,
            "msg_status":"SEND_SUCCESS"
        }
        '''
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/message/mass/get',
            data={
                'msg_id': msg_id
            }
        )

    def move_user_by_openids(self, open_ids, to_groupid):
        '''
        批量移动用户分组
        :param open_ids: 用户的 open id list
        :param to_groupid: 要被移动到的分组 id
        :return: 微信服务器返回的 JSON 数据
        {"errcode": 0, "errmsg": "ok"}
        官方API: http://mp.weixin.qq.com/wiki/8/d6d33cf60bce2a2e4fb10a21be9591b8.html
        '''
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/groups/members/batchupdate',
            data={
                'openid_list': open_ids,
                'to_groupid': to_groupid
            }
        )

    def delete_group(self, group_id):
        '''
        删除用户分组
        :param group_id: 需要删除分组的 id
        :return: 微信服务器返回的 JSON 数据
        {"errcode": 0, "errmsg": "ok"}
        官方API: http://mp.weixin.qq.com/wiki/8/d6d33cf60bce2a2e4fb10a21be9591b8.html
        '''
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/groups/delete',
            data={
                'group': {
                    'id': group_id
                }
            }
        )

    def set_user_remark(self, open_id, remark):
        '''
        设置用户备注名
        :param open_id: 用户的 openid
        :param remark: 备注名
        :return: 微信服务器返回的 JSON 数据
        {"errcode": 0, "errmsg": "ok"}
        官方API: http://mp.weixin.qq.com/wiki/16/528098c4a6a87b05120a7665c8db0460.html
        '''
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/user/info/updateremark',
            data={
                'openid': open_id,
                'remark': remark
            }
        )

    def get_users_info(self, user_ids, lang='zh_CN'):
        '''
        批量获取用户信息
        :param user_ids: 用户 open id 列表
        :param lang: 国家地区语言版本,默认 zh_CN
        :return: 微信服务器返回的 JSON 数据
        官方API: http://mp.weixin.qq.com/wiki/1/8a5ce6257f1d3b2afb20f83e72b72ce9.html
        '''
        user_list = []
        for _id in user_ids:
            user_list.append({'openid': _id, 'lang': lang})
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/user/info/batchget',
            data={
                'user_list': user_list
            }
        )

    def get_all_templates(self):
        '''
        获取所有模版
        :return: 模版列表
        官方API: http://mp.weixin.qq.com/wiki/5/6dde9eaa909f83354e0094dc3ad99e05.html
        '''
        return self.request.get(
            url='https://api.weixin.qq.com/cgi-bin/template/get_all_private_template'
        )

    def delete_template(self, template_id):
        '''
        删除模版
        :param template_id: 公众号下模版消息 id
        :return: 微信服务器返回的 JSON 数据
        官方API: http://mp.weixin.qq.com/wiki/5/6dde9eaa909f83354e0094dc3ad99e05.html
        '''
        self.request.post(
            url='https://api,weixin.qq.com/cgi-bin/template/del_private_template',
            data={
                'template_id': template_id
            }
        )

    def convert_shorturl(self, long_url):
        '''
        将长链接转换为短链接, 响应速度更快, 扫码成功率更高
        :param long_url: 长链接
        :return: {"errcode":0,"errmsg":"ok","short_url":"http:\/\/w.url.cn\/s\/AvCo6Ih"}
        官方API: http://mp.weixin.qq.com/wiki/10/165c9b15eddcfbd8699ac12b0bd89ae6.html
        '''
        result = self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/shorturl',
            data={
                'action': 'long2short',
                'long_url': long_url
            }
        )
        if result['errcode'] == 0:
            return result['short_url']
        else:
            Log.error("error code %d, error message %s" % (result['errcode'], result['errmsg']))
            raise ValueError("error code %d, error message %s" % (result['errcode'], result['errmsg']))

    def upload_permanent_material(self, media_type, media, title=None, introduction=None):
        '''
        上传永久素材
        :param media_type: 素材类型, 支持类型包括('image', 'voice', 'video', 'thumb')
        :param media: 文件类型的素材
        如果上传的类型为 video, 需要以下额外的两个参数
        :param title: 视频标题
        :param introduction: 视频描述
        :return: 微信服务器返回的 JSON 数据
        {"type":"TYPE","media_id":"MEDIA_ID","created_at":123456789}
        官方API: http://mp.weixin.qq.com/wiki/5/963fc70b80dc75483a271298a76a8d59.html
        '''
        if media_type not in ('image', 'voice', 'video', 'thumb'):
            Log.error('upload media type not supported!')
            raise TypeError('upload media type not supported!')
        param = {
            'type': media_type
        }
        if media_type == 'video':
            # 类型为 video 需要额外的两个参数
            param.update({
                'title': title,
                'introduction': introduction
            })
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/material/add_material',
            params=param,
            files={
                'media': (media.name, media, media.name.split('.')[-1])
            }
        )

    def upload_permanent_article_img(self, img):
        '''
        上传永久性图文素材中的图片链接会被过滤掉, 需要使用本接口单独上传图片, 再将返回的链接插入图文详情中,
        图片仅支持 jpg/png 格式
        :param img: file 类型的图片
        :return: 微信服务器返回的图片 URL
        {
            "url":  "http://mmbiz.qpic.cn/mmbiz/gLO17UPS6FS2xsypf378iaNhWacZ1G1UplZYWEYfwvuU6Ont96b1roYs CNFwaRrSaKTPCUdBK9DgEHicsKwWCBRQ/0"
        }
        官方API: http://mp.weixin.qq.com/wiki/14/7e6c03263063f4813141c3e17dd4350a.html
        '''
        if isinstance(img, file) and img.name.split('.')[-1].lower() not in ('jpg','png'):
            Log.error('image type is not supported!')
            raise TypeError('image type is not supported!')
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/media/uploadimg',
            files={
                'media': (img.name, img, img.name.split('.')[-1])
            }
        )

    def upload_permanent_articles(self, articles):
        '''
        上传永久类型的图文素材
        :param articles: 图文素材列表
        其中每一个 article 为一个字典其结构如下:
        article={
            "title": TITLE,                             # 标题
            "thumb_media_id": THUMB_MEDIA_ID,           # 图文消息封面图片ID,必须是永久 media_id
            "author": AUTHOR,                           # 作者
            "digest": DIGEST,                           # 图文消息的摘要，仅有单图文消息才有摘要，多图文此处为空
            "show_cover_pic": SHOW_COVER_PIC(0 / 1),    # 是否显示封面，0为false，即不显示，1为true，即显示
            "content": CONTENT,                         # 图文消息的具体内容，支持HTML标签，必须少于2万字符，小于1M，且此处会去除JS
            "content_source_url": CONTENT_SOURCE_URL    # 图文消息的原文地址，即点击“阅读原文”后的URL
        }
        :return: 微信服务器返回的 JSON 数据
        {
            "media_id":MEDIA_ID
        }
        官方API: http://mp.weixin.qq.com/wiki/14/7e6c03263063f4813141c3e17dd4350a.html
        '''
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/material/add_news',
            data={
                'articles': articles
            }
        )

    def get_permanent_material(self, media_id):
        '''
        获取永久素材
        :param media_id: 素材 id
        :return: 根据类型不同返回的也不同,具体参见官方API。
        官方API: http://mp.weixin.qq.com/wiki/4/b3546879f07623cb30df9ca0e420a5d0.html
        '''
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/material/get_material',
            data={
                'media_id': media_id
            }
        )

    def delete_permanent_material(self, media_id):
        '''
        删除不需要的永久素材
        :param media_id: 需要删除素材的 media_id
        :return: 微信服务器返回的 JSON 数据
        {
            "errcode":ERRCODE,
            "errmsg":ERRMSG
        }
        官方API: http://mp.weixin.qq.com/wiki/5/e66f61c303db51a6c0f90f46b15af5f5.html
        '''
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/material/del_material',
            data={
                'media_id': media_id
            }
        )

    def update_permanent_material(self, media_id, index, article):
        '''
        修改永久素材
        :param media_id: 要修改的素材 media_id
        :param index: 要更新的文章在图文消息中的位置（多图文消息时，此字段才有意义），第一篇为0
        :param article: 结构请参考上传永久图文素材
        :return: 微信服务器返回的 JSON 数据
        {
            "errcode": ERRCODE,
            "errmsg": ERRMSG
        }
        官方API: http://mp.weixin.qq.com/wiki/4/19a59cba020d506e767360ca1be29450.html
        '''
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/material/update_news',
            data={
                'media_id': media_id,
                'index': index,
                'articles': article
            }
        )

    def get_material_count(self):
        '''
        获取永久素材总数
        :return:
        {
            "voice_count":COUNT,    # 语音总数
            "video_count":COUNT,    # 视频总数
            "image_count":COUNT,    # 图片总数
            "news_count":COUNT      # 图文总数
        }
        官方API: http://mp.weixin.qq.com/wiki/16/8cc64f8c189674b421bee3ed403993b8.html
        '''
        return self.request.get(
            url='https://api.weixin.qq.com/cgi-bin/material/get_materialcount'
        )

    def get_permanent_material_list(self, media_type, offset, count):
        '''
        获取素材列表
        :param media_type: 素材类型, 支持('image', 'voice', 'video', 'news')
        :param offset: 从全部素材的该偏移位置开始返回，0表示从第一个素材返回
        :param count: 返回素材的数量，取值在1到20之间
        :return: 微信服务器返回的 JSON 数据, 具体结构参见官方 API.
        官方API: http://mp.weixin.qq.com/wiki/12/2108cd7aafff7f388f41f37efa710204.html
        '''
        return self.request.post(
            url='https://api.weixin.qq.com/cgi-bin/material/batchget_material',
            data={
                'type': media_type,
                'offset': offset,
                'count': count
            }
        )
