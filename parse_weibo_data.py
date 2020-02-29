import json
import re
from bs4 import BeautifulSoup as bs
import traceback
import requests
import time


class Parsedata(object):

    def getcontent(self):
        with open('./data.json', 'r') as f:
            text = f.read()
            res = json.loads(text)
        return res

    def getLocation(self, addr):
        try:
            url = 'http://restapi.amap.com/v3/geocode/geo?key=389880a06e3f893ea46036f030c94700&s=rsv3&city=35&address=' + addr
            r = requests.get(url)
            rsp = json.loads(r.text)
            if rsp['count'] == 0:
                return None, None
            else:
                return rsp['geocodes'][0]['formatted_address'], rsp['geocodes'][0]['location']
        except Exception:
            traceback.print_exc()
            return None, None

    def parse(self, item):
        person_data = {}
        try:
            soup = bs(item['text'], 'html.parser')
            a_tag = soup.find_all('a')
            if a_tag[-1]['href'].startswith('/status/'):
                link = 'https://m.weibo.cn' + a_tag[-1]['href']
            else:
                return None
        except Exception as e:
            print(traceback.print_exc())
            return None

        person_data['link'] = link
        rr = re.findall('>【(.*?)<', item['text'], re.S)
        for v in rr:
            value = v.split('】')
            if value[0] == '姓名':
                if value[1] == '':
                    return None
                else:
                    person_data['name'] = value[1]
            elif value[0] == '年龄':
                person_data['age'] = value[1]
            elif value[0] == '所在小区、社区':
                if value[1] == '':
                    return None
                else:
                    addr, localtion = self.getLocation(value[1])
                    if addr is not None:
                        person_data['community'] = addr
                        person_data['Latitude'] = localtion.split(',')[0]
                        person_data['longitude'] = localtion.split(',')[1]
                    else:
                        return None
            elif value[0] == '患病时间':
                person_data['timeOfIllness'] = value[1]
            elif value[0] == '联系方式':
                text = re.search('([0-9]+)', value[1], re.S)
                if text:
                    person_data['contact'] = text.group(1)
            elif value[0] == '其他紧急联系人':
                text = re.search('([0-9]+)', value[1], re.S)
                if text:
                    person_data['otherContact'] = text.group(1)
            elif value[0] == '病情描述':
                person_data['desc'] = value[1]
        if person_data.get('name', None):
            return person_data
        else:
            return None

    def run(self):
        final_data = []
        content = self.getcontent()
        for i in content:
            res = self.parse(content[i])
            if res is not None:
                final_data.append(res)
            time.sleep(0.5)
        time_str = str(int(time.time() * 1000))
        with open('./illness' + time_str + '.json', 'w') as f2:
            f2.write(json.dumps(final_data, ensure_ascii=False))


if __name__ == '__main__':
    d = Parsedata()
    d.run()
