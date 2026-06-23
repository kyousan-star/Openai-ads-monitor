import json, urllib.request, urllib.parse, datetime, re, xml.etree.ElementTree as ET

today = datetime.date.today().strftime('%Y-%m-%d')
WEBHOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/a8d82c68-6dfa-4431-85fc-34ad85c19a70'


def search_news(query, max_results=4):
    """Google News RSS - free, no auth, reliable in CI"""
    q = urllib.parse.quote(query)
    url = f'https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            xml_data = r.read()
        root = ET.fromstring(xml_data)
        results = []
        for item in root.findall('.//item')[:max_results]:
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            pub = item.findtext('pubDate', '')[:16]
            desc = re.sub(r'<[^>]+>', '', item.findtext('description', '')).strip()[:80]
            if title:
                results.append({'title': title, 'link': link, 'date': pub, 'desc': desc})
        return results
    except Exception as e:
        print(f'search error [{query[:30]}]: {e}')
        return []


def fmt_section(emoji_title, items):
    lines = [f'{emoji_title}']
    if not items:
        lines.append('• 本周暂无新动态')
    else:
        for it in items:
            lines.append(f'• {it["title"]}')
            if it.get('desc'):
                lines.append(f'  {it["desc"]}')
            if it.get('link'):
                lines.append(f'  🔗 {it["link"]}')
    return '\n'.join(lines)


print('搜索主题1: OpenAI ChatGPT 广告平台动态...')
r1 = search_news('ChatGPT ads platform OpenAI advertising ecommerce 2026')

print('搜索主题2: 亚马逊卖家实战...')
r2 = search_news('Amazon sellers ChatGPT ads ROI advertising results 2026')

print('搜索主题3: Prime Day + OpenAI 广告...')
r3 = search_news('Amazon Prime Day 2026 ChatGPT OpenAI advertising')

print(f'找到: {len(r1)} / {len(r2)} / {len(r3)} 条')

summary = r1[0]['title'] if r1 else (r2[0]['title'] if r2 else '本周暂无重要动态')

report = f"""📊 OpenAI Ads 周报 · {today}
{'='*32}

{fmt_section('【① 平台动态】', r1)}

{fmt_section('【② 卖家实战】', r2)}

{fmt_section('【③ Prime Day / 大促信号】', r3)}

🔑 本周关注重点：{summary[:100]}
{'='*32}"""

print(report)

payload = {'msg_type': 'text', 'content': {'text': report}}
data = json.dumps(payload, ensure_ascii=False).encode()
req = urllib.request.Request(WEBHOOK, data=data,
                             headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as r:
    print('推送结果:', r.read().decode())
