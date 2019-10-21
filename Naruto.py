from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import jieba
import jieba.analyse
from pyecharts import options as opts
from pyecharts.globals import SymbolType, ThemeType
from pyecharts.charts import WordCloud
from collections import Counter

'''
author: BW
vision: 1.0
'''

def get_danmu(cid):
    '''
    爬取弹幕
    :param cid 视频cid编号
    :return df
    '''
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}  
    url = 'http://comment.bilibili.com/{}.xml'.format(cid)
    response = requests.get(url, headers = headers)
    response.encoding='utf-8-sig'

    soup = BeautifulSoup(response.text, 'html.parser')    # 或用 'lxml'
    info_list = soup.find_all('d')
    danmu_list = [info.text for info in info_list]
    danmu_dict = {'弹幕': danmu_list}     # 格式：{'弹幕': ['弹幕0', '弹幕1', ... , '弹幕2999']}  共3000条

    df = pd.DataFrame(danmu_dict)    
    return df


def analyse(cid_list):
    '''
    分词
    :param cid_list 
    :return lst
    '''
    str_list = []
    for cid in cid_list:
        df = get_danmu(cid)
        s = ' '.join(df['弹幕'])
        str_list.append(s)

    string = ' '.join(str_list)
    jieba.analyse.set_stop_words(stop_words_file_path)    # 清洗数据
    words_count_list_TR = jieba.analyse.textrank(string, topK=50, withWeight=True)   # TextRank算法
    words_count_list_TI = jieba.analyse.extract_tags(string, topK=50, withWeight=True)   # TF-IDF算法
    # print(words_count_list_TR, words_count_list_TI)
    return [words_count_list_TR, words_count_list_TI]


def draw_word_cloud(cid_list, name):
    '''
    绘制词云
    :param cid 视频cid编号
    :param name 人物名
    '''
    lst = analyse(cid_list)
    words_count_list_TR = lst[0]
    words_count_list_TI = lst[1]

    word_cloud_TR = (
        WordCloud(init_opts=opts.InitOpts(theme=ThemeType.ROMA))
            .add("", words_count_list_TR, word_size_range=[20, 50], shape=SymbolType.RECT)
            .set_global_opts(title_opts=opts.TitleOpts(title="{}词云TOP50".format(name), subtitle="基于TextRank算法的关键词抽取"))   
            .render('{}_WordCloud_TR.html'.format(name))
    )

    word_cloud_TI = (
        WordCloud(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add("", words_count_list_TI, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
            .set_global_opts(title_opts=opts.TitleOpts(title="{}词云TOP50".format(name), subtitle="基于TF-IDF算法的关键词抽取"))
            .render('{}_WordCloud_TI.html'.format(name))
    )
    print('====={}词云绘制完毕====='.format(name))


def top3_danmu(total_lst):
    '''
    最热弹幕
    :param total_lst
    '''
    dic = {}
    for lst in total_lst:
        for cid in lst[0]:
            df = get_danmu(cid)
            danmu_lst = df['弹幕'].tolist()
            danmu_dic = Counter(danmu_lst)    # 频数，返回的值是字典格式  {'xx':8,'xxx':9}
            result = danmu_dic.most_common(3)  # Counter(words_list).most_common(n)  返回[('xxx', 8), ('xxx', 5),...]  前n个
            dic[lst[1]] = result
    print(dic)

if __name__ == '__main__':
    stop_words_file_path = 'stop_words.txt'    

    total_lst = [
        [['67757064', '35855294'], '宇智波鼬'], 
        [['38817442'], '迈特凯'], 
        [['46083068', '34686150', '34149045'], '旗木卡卡西'],
        [['37945746'], '自来也'], 
        [['31162823', '31593203'], '我爱罗'], 
        [['114917496', '32131385'], '日向宁次'], 
        [['49314074', '50377208', '51722213'], '大蛇丸'], 
        [['43157701', '44147773'], '波风水门'], 
        [['78464279'], '奈良鹿丸'],
        [['99090096', '96770475'], '志村团藏'], 
        [['105021605', '108043433'], '宇智波带土'], 
        [['59302531'], '干柿鬼鲛'],
        [['61470968'], '千手扉间'], 
        [['62643245'], '小南'], 
        [['83188095'], '千手柱间'], 
        [['90654563'], '角都'],
        [['119446517'], '手鞠'], 
        [['111482714'], '日向雏田'], 
        [['102705777', '40848048'], '赤砂之蝎'], 
        [['92910756'], '黑绝'], 
        [['56577705'], '迪达拉']
        ]     # cid 手动寻找, 没有很好的办法解决
    
    for lst in total_lst:
        draw_word_cloud(lst[0], lst[1])  

    top3_danmu(total_lst)