import urllib.request
import re

try:
    response = urllib.request.urlopen('http://127.0.0.1:8000/pozos/3/daily-report/16/excel/')
    print('OK:', response.getcode())
except Exception as e:
    if hasattr(e, 'read'):
        html = e.read().decode('utf-8', errors='ignore')
        m = re.search(r'<textarea id=\"traceback_area\".*?>(.*?)</textarea>', html, re.DOTALL)
        if m:
            print(m.group(1).strip())
        else:
            print('No textarea found. Snippet:', html[:500])
    else:
        print('Error:', e)
