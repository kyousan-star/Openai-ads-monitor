import json, urllib.request, datetime

today = datetime.date.today().strftime('%Y-%m-%d')
WEBHOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/a8d82c68-6dfa-4431-85fc-34ad85c19a70'


def search(query):
    url = 'https://s.jina.ai/' + query.replace(' ', '+')
    req = urllib.request.Request(url, headers={
        'Accept': 'text/plain',
        'X-Retain-Images': 'none',
        'User-Agent': 'Mozilla/5.0'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode('utf-8', errors='ignore')[:4000]
    except Exception as e:
        print(f'search error: {e}')
        return ''


def pts(text):
    skip = ('http', '[', '#', '---', '===', 'Source', '!', '*')
    lines = [l.strip() for l in text.split('\n')
             if l.strip() and len(l.strip()) > 30
             and not any(l.strip().startswith(s) for s in skip)]
    return [l[:120] for l in lines[:3]] or ['本周暂无新动态']


def rows(points):
    return [[{'tag': 'text', 'text': '• ' + p}] for p in points]


print('搜索主题1: OpenAI ChatGPT 广告平台动态...')
r1 = search('ChatGPT ads platform update ecommerce 2026')

print('搜索主题2: 亚马逊卖家实战案例...')
r2 = search('Amazon sellers ChatGPT ads ROI case study 2026')

print('搜索主题3: Prime Day + OpenAI 广告...')
r3 = search('Amazon Prime Day 2026 ChatGPT OpenAI ads strategy')

p1, p2, p3 = pts(r1), pts(r2), pts(r3)
print('p1:', p1)
print('p2:', p2)
print('p3:', p3)

content = [
    [{'tag': 'text', 'text': '① 平台动态', 'style': ['bold']}],
    *rows(p1),
    [{'tag': 'text', 'text': ''}],
    [{'tag': 'text', 'text': '② 卖家实战', 'style': ['bold']}],
    *rows(p2),
    [{'tag': 'text', 'text': ''}],
    [{'tag': 'text', 'text': '③ Prime Day / 大促信号', 'style': ['bold']}],
    *rows(p3),
    [{'tag': 'text', 'text': ''}],
    [{'tag': 'text', 'text': '\U0001f511 本周关注重点：', 'style': ['bold']},
     {'tag': 'text', 'text': p1[0] if p1[0] != '本周暂无新动态' else '本周暂无重要新动态'}],
]

payload = {
    'msg_type': 'post',
    'content': {'post': {'zh_cn': {
        'title': f'\U0001f4ca OpenAI Ads 周报 · {today}',
        'content': content
    }}}
}

data = json.dumps(payload, ensure_ascii=False).encode()
req = urllib.request.Request(WEBHOOK, data=data,
                             headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as r:
    print('飞书推送结果:', r.read().decode())

print('完成')
