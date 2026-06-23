import json, urllib.request, urllib.parse, datetime, re, time
import xml.etree.ElementTree as ET

today = datetime.date.today().strftime('%Y-%m-%d')
WEBHOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/a8d82c68-6dfa-4431-85fc-34ad85c19a70'


def search_news(query, max_results=3):
    q = urllib.parse.quote(query)
    url = f'https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            root = ET.fromstring(r.read())
        results = []
        for item in root.findall('.//item')[:max_results]:
            raw = re.sub(r'&[a-zA-Z]+;', '', item.findtext('title', '')).strip()
            m = re.match(r'^(.+?)\s+-\s+([^-]+)$', raw)
            en_title = m.group(1).strip() if m else raw
            source = m.group(2).strip() if m else ''
            if en_title:
                results.append({'en_title': en_title, 'source': source})
        return results
    except Exception as e:
        print(f'search error: {e}')
        return []


def translate(text):
    url = ('https://api.mymemory.translated.net/get?q='
           + urllib.parse.quote(text) + '&langpair=en|zh')
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        t = data.get('responseData', {}).get('translatedText', '')
        return t if t and t.upper() != text.upper() else text
    except Exception as e:
        print(f'translate error: {e}')
        return text


def fmt_section(title, items):
    lines = [title]
    if not items:
        lines.append('• 本周暂无新动态')
    else:
        for it in items:
            src = f'（{it["source"]}）' if it['source'] else ''
            lines.append(f'• {it["zh_title"]}{src}')
    return '\n'.join(lines)


print('搜索中...')
r1 = search_news('ChatGPT ads platform OpenAI advertising ecommerce 2026')
r2 = search_news('Amazon sellers ChatGPT ads ROI results 2026')
r3 = search_news('Amazon Prime Day 2026 ChatGPT OpenAI advertising sellers')
print(f'找到: {len(r1)}/{len(r2)}/{len(r3)} 条，翻译中...')

for it in r1 + r2 + r3:
    it['zh_title'] = translate(it['en_title'])
    time.sleep(0.3)

top = (r1 + r2 + r3)
summary = top[0]['zh_title'] if top else '本周暂无重要动态'

report = f"""📊 OpenAI Ads 周报 · {today}
{'='*30}

{fmt_section('【① 平台动态】', r1)}

{fmt_section('【② 卖家实战】', r2)}

{fmt_section('【③ Prime Day / 大促信号】', r3)}

🔑 本周关注重点：{summary}
{'='*30}"""

print(report)

payload = {'msg_type': 'text', 'content': {'text': report}}
data = json.dumps(payload, ensure_ascii=False).encode()
req = urllib.request.Request(WEBHOOK, data=data,
                             headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as r:
    print('推送结果:', r.read().decode())
