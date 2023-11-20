import pytz
from datetime import datetime, timedelta
	
def get_datetime_now():
    jst = pytz.timezone('Asia/Tokyo')
    return datetime.now(jst)

today = get_datetime_now()
yesterday = today - timedelta(days=1)

_watch_pdf_tags = [
	{
		"tag": "決算短信",
		"condition": lambda title: "決算" in title and "短信 ",
		"path": "input/kessan_tanshin_pdf_prompt.txt"
	},
]

_rise_stock_tags = [
	{
		# ((A, B), (C)) => (A & B) or C
		"tag": "配当",
		"condition": lambda title:  ("配当" in title and "修正" in title) or ("増配" in title),
		"path": "input/dividend_pdf_prompt.txt"
	},
	{
		"tag": "株式分割",
		"condition": lambda title:  "株式" in title and "分割" in title,
		"path": "input/stock_splits_pdf_prompt.txt"
	},
	{
		"tag": "自己株式取得",
		"condition": lambda title: ("自己株式" in title) and ("取得" in title),
		"path": "input/buy_my_stock_pdf_prompt.txt"
	},
	{
		"tag": "上方修正",
		"condition": lambda title: ("上方" in title) and ("修正" in title),
		"path": "input/upward_revision_pdf_prompt.txt"
	},
	{
		"tag": "業績予想の修正",
		"condition": lambda title: ("業績予想" in title) and ("修正" in title) and (not "下方" in title),
		"path": "input/earning_revision_pdf_prompt.txt"
	},
]

_watch_pdf_tags += _rise_stock_tags


config = {
	"scraping":{
		"skip_scraping": True,
		"is_on_day": False,
		"start_date_index": 1
	},
	"evaluate": {
		"end_date": today,
		"days_before_end_date": 30, #評価をする日数
		"top_evaluations_limit": 5, #トップのN社を列挙する
	},
	"disclosure" : {
		"watch_pdf_tags": _watch_pdf_tags,
		"rise_stock_tags": _rise_stock_tags,
	},
}