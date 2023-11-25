import sys

sys.path.append("../realtime_stock_rise_predicter") #mainのモジュール読み込む

from disclosure_scraper import DisclosureScraper
from pdf_downloader import PdfDownloader
from db_manager import DBManager
from db_manager_debugger import DBManagerDebugger
from title_evaluator import TitleEvaluator
import config

# 使用例
path = config.setting['db']['past']
#path = config.setting['db']['recent']
db_manager = DBManager(path)
debugger = DBManagerDebugger(db_manager)  # デバッガークラスのインスタンスを作成
debugger.display_tags_for_all_companies_and_dates(limit=20)  # 最大10件のタグを表示