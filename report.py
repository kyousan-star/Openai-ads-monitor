import json, urllib.request, urllib.parse, datetime, re

today = datetime.date.today().strftime('%Y-%m-%d')
WEBHOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/a8d82c68-6dfa-4431-85fc-34ad85c19a70'


def search(query):
    """DuckDuckGo HTML search - no API key required"""
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Accept': 'text/html',
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read().decode('utf-8', errors='ignore')
        # Extract result snippets from DDG HTML
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.S)
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.S)
        urls = re.findall(r'class="result__url"[^>]*>\s*(.*?)\s*</a>', html, re.S)
        results = []
        for i in range(min(5, len(snippets))):
            title = re.sub(r'<[^>]+>', '', titles[i] if i < len(titles) else '').strip()
            snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            url_text = urls[i].strip() if i < len(urls) else ''
            if title and snip:
                results.append(f'{title} — {snip[:100]} ({url_text})')
        return results
    except Exception as e:
        print(f'search error: {e}')
        return []


def fmt_section(title, points):
    lines = [f'【{title}】']
    for p in (points or ['本周暂无新动态']):
        lines.append(f'• {p[:120]}')
    return '\n'.join(lines)


print('搜索主题1: OpenAI ChatGPT 广告平台动态...')
p1 = search('ChatGPT ads platform update ecommerce 2026 site:digiday.com OR site:axios.com')

print('搜索主题2: 亚马逊卖家实战案例...')
p2 = search('Amazon sellers ChatGPT ads ROI results case study 2026')

print('搜索主题3: Prime Day + OpenAI 广告...')
p3 = search('Amazon Prime Day 2026 ChatGPT OpenAI ads strategy sellers')

print(f'找到: {len(p1)} / {len(p2)} / {len(p3)} 条')

summary = p1[0].split('—')[0].strip() if p1 else '本周暂无重要动态'

report = f"""📊 OpenAI Ads 周报 · {today}
{'='*30}

{fmt_section('① 平台动态', p1[:3])}

{fmt_section('② 卖家实战', p2[:3])}

{fmt_section('③ Prime Day / 大促信号', p3[:3])}

🔑 本周关注重点：{summary}
{'='*30}"""

print('周报内容:')
print(report)

payload = {'msg_type': 'text', 'content': {'text': report}}
data = json.dumps(payload, ensure_ascii=False).encode()
req = urllib.request.Request(WEBHOOK, data=data,
                             headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as r:
    result = r.read().decode()
    print('飞书推送结果:', result)

print('完成')
