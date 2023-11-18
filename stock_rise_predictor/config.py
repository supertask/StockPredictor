import pytz
from datetime import datetime, timedelta
	
def get_datetime_now():
    jst = pytz.timezone('Asia/Tokyo')
    return datetime.now(jst)

today = get_datetime_now()
yesterday = today - timedelta(days=1)

config = {
	"scraping":{
		"skip_scraping": True,
		"is_on_day": True,
		"start_date_index": 4
	},
	"evaluate": {
		"end_date": today,
		"days_before_end_date": 10
	}
}