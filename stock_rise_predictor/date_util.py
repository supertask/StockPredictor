
def get_datetime_now():
    jst = pytz.timezone('Asia/Tokyo')
    return datetime.now(jst)
    
def format_datetime_str(datetime_now):
    return datetime_now.strftime('%Y-%m-%d')