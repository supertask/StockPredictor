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
		#"condition": lambda title: "決算" in title and "短信 ",
		"condition": lambda title: ("決算" in title) and ("短信" in title),
		"prompt_path": "input/kessan_tanshin_pdf_prompt.txt"
	},
]

_rise_stock_tags = [
	{
		# ((A, B), (C)) => (A & B) or C
		"tag": "配当",
		"condition": lambda title:  ("配当" in title and "修正" in title) or ("増配" in title),
		"prompt_path": "input/dividend_pdf_prompt.txt"
	},
	{
		"tag": "株式分割",
		"condition": lambda title:  "株式" in title and "分割" in title,
		"prompt_path": "input/stock_splits_pdf_prompt.txt"
	},
	{
		"tag": "自己株式取得",
		"condition": lambda title: ("自己株式" in title) and ("取得" in title),
		"prompt_path": "input/buy_my_stock_pdf_prompt.txt"
	},
	{
		"tag": "上方修正",
		"condition": lambda title: ("上方" in title) and ("修正" in title),
		"prompt_path": "input/upward_revision_pdf_prompt.txt"
	},
	{
		"tag": "業績予想の修正",
		"condition": lambda title: ("業績予想" in title) and ("修正" in title) and (not "下方" in title),
		"prompt_path": "input/earning_revision_pdf_prompt.txt"
	},
]

_watch_pdf_tags += _rise_stock_tags


setting = {
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

def get_watch_tags():
    watch_pdf_tags = setting["disclosure"]["watch_pdf_tags"]
    tags = [tag_info["tag"] for tag_info in watch_pdf_tags]
    return tags

def get_rise_tags():
    rise_tags = setting["disclosure"]["rise_stock_tags"]
    tags = [tag_info["tag"] for tag_info in rise_tags]
    return tags

def get_tag_prompt_path_dict():
	tag_prompt_dict = {}
	watch_pdf_tags = setting["disclosure"]["watch_pdf_tags"]
	for tag_info in watch_pdf_tags:
		tag_prompt_dict[tag_info["tag"]] = tag_info["prompt_path"]
	return tag_prompt_dict