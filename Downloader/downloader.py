# -*- coding: utf-8 -*-
import os
import urllib.request
import sys

sys.path.append('../')
from Common import utils

MAX_RETRY = 2

CONFIG_KEY_PROXY = "proxy"
CONFIG_KEY_REFERER = "referer"
CONFIG_KEY_UA = "ua"

DOWNLOAD_DIR = 'dir'
FILE_NAME = 'file_name'
URL = 'url'


def filter_fun(item):
    return type(item) is dict and URL in item.keys() and item[URL].startswith("http")


def download(task_list, dir_path=None, config=None):
    '''
    :param tasks: 下载任务信息[{'url': url, 'file_name': file_name}, {...}, ...]
    :param dir_path: 下载目录
    :param config: 下载配置, proxy 与 referer 等
    :return:
    '''
    print("----------- Start Download -----------")
    tasks = list(filter(filter_fun, task_list))
    total = len(tasks)
    downloaded = 0
    failed = []
    max_amount = total
    # max_amount = 1
    print("max_amount: {}".format(max_amount))

    opener = urllib.request.build_opener()
    if config is not None and CONFIG_KEY_PROXY in config.keys():
        # 添加 http 代理
        proxy_server = config[CONFIG_KEY_PROXY]
        proxy = urllib.request.ProxyHandler({'http': proxy_server})
        opener = urllib.request.build_opener(proxy)
        print("使用代理: {}".format(proxy_server))
    if config is not None and CONFIG_KEY_REFERER in config.keys():
        # 添加 referer
        referer_host = config[CONFIG_KEY_REFERER]
        opener.addheaders = [('Referer', referer_host)]
        print("使用referer: {}".format(referer_host))
    if config is not None and CONFIG_KEY_UA in config.keys():
        opener.addheaders.append(('user-agent', config[CONFIG_KEY_UA]))
        print("使用user-agent")
    print("Opener addheaders: ", opener.addheaders)
    urllib.request.install_opener(opener)

    for task in tasks:
        # 优先下载到任务配置的目录
        if DOWNLOAD_DIR in task.keys():
            dir_path = task[DOWNLOAD_DIR]
        elif dir_path == None:
            dir_path = "download_undefined"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        if downloaded >= max_amount:
            break
        file_url = task[URL]
        print("url: {}".format(file_url))

        if FILE_NAME in task.keys():
            file_name = task[FILE_NAME]
        else:
            file_name = file_url.split('/')[-1].split('?')[0]
            file_name = utils.verify_file_name(file_name)

        if os.path.exists("{}\{}".format(dir_path, file_name)):  # 检查重名
            name = file_name.split(".")[0]
            file_name = file_name.replace(name, "{}_{}".format(name, downloaded))
        print("file_name: {}".format(file_name))

        retry = 0
        while (retry <= MAX_RETRY):
            try:
                resp = urllib.request.urlretrieve(file_url, "{}\{}".format(dir_path, file_name))
                break
            except Exception as err:
                print("----\nSomething wrong happened!")
                print("file_name: {}".format(file_name))
                print("retry: ", retry)
                retry += 1
                print(type(err))
                print(err.args)
                print(err)
                print("----")
                if retry > MAX_RETRY:
                    failed.append(task)
                    print("重试无效!\n----")
                    break
                pass
        downloaded += 1
    print(u"Download finished {}/{}!\nSaved at \{}".format(downloaded, total, dir_path))
    if len(failed) > 0:
        print("{}\{} download failed!!".format(len(failed), total))
        print("failed tasks: ")
        for t in failed:
            print(t)
    return failed
