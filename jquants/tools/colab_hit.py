import time
import datetime
import webbrowser

# 1時間毎に任意のノートブックを開く
for i in range(12):
    browse = webbrowser.get('chrome')
    browse.open('https://colab.research.google.com/drive/1BI896XcWTg7OD5KfrPejsRyK8h-hRgcZ')
    print(i, datetime.datetime.today())
    time.sleep(60*60)
