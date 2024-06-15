import os
import requests
import zipfile
import io
import pandas as pd
import urllib3
import chardet
from datetime import datetime, timedelta

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Constants
API_KEY_PATH = '.token/edinet_api_key'
API_KEY = open(API_KEY_PATH, 'r').read().rstrip()
BASE_URL = "https://api.edinet-fsa.go.jp/api/v2/documents"
OUTPUT_DIR = 'output/ipo_reports'

class EdinetReportGetter:

  def __init__(self):
      self.securities_items = {
        "jpcrp_cor:DescriptionOfBusinessTextBlock": "事業の内容",
        "jpcrp_cor:BusinessPolicyBusinessEnvironmentIssuesToAddressEtcTextBlock": "経営方針、経営環境及び対処すべき課題等",
        "jpcrp_cor:BusinessRisksTextBlock": "事業等のリスク",
        "jpcrp_cor:ManagementAnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock": "経営者による財政状態、経営成績及びキャッシュ・フローの状況の分析",
        "jpcrp_cor:CriticalContractsForOperationTextBlock": "経営上の重要な契約等",
        "jpcrp_cor:ResearchAndDevelopmentActivitiesTextBlock": "研究開発活動",
        "jpcrp_cor:OverviewOfCapitalExpendituresEtcTextBlock": "設備投資等の概要",
        "jpcrp_cor:MajorFacilitiesTextBlock": "主要な設備の状況",
        "jpcrp_cor:TotalNumberOfSharesTextBlock": "株式の総数",
        "jpcrp_cor:IssuedSharesTotalNumberOfSharesEtcTextBlock": "発行済株式、株式の総数等",
        "jpcrp_cor:DividendPolicyTextBlock": "配当政策",
        "jpcrp_cor:OverviewOfCorporateGovernanceTextBlock": "コーポレート・ガバナンスの概要",
        "jpcrp_cor:InformationAboutOfficersTextBlock": "役員の状況",
        "jpcrp_cor:BalanceSheetTextBlock": "貸借対照表",
        "jpcrp_cor:StatementOfIncomeTextBlock": "損益計算書",
        "jpcrp_cor:StatementOfCashFlowsTextBlock": "キャッシュ・フロー計算書"
      }

  def documents_json(self, date):
    params = {
      "type" : 2,
      "date" : date,
      "Subscription-Key": API_KEY
    }
    res = requests.get(BASE_URL + ".json", params=params, verify=False)
    return res.json()['results']

  def document_detail(self, date, doc_id):
    params = {
      "type" : 5, #csv
      "date" : date,
      "Subscription-Key": API_KEY
    }
    res = requests.get(f"{BASE_URL}/{doc_id}", params=params, verify=False)
    tsv_df = self.extract_tsv_from_zip(res)
    doc_list = []
    for key, securities_type in self.securities_items.items():
      matching_row = tsv_df[tsv_df["要素ID"] == key]
      if matching_row.empty:
        doc_list.append([securities_type, None])
      else:
        doc_list.append([securities_type, matching_row["値"].values[0]])
    return doc_list

  def extract_tsv_from_zip(self, response):
      with zipfile.ZipFile(io.BytesIO(response.content)) as the_zip:
          for file_name in the_zip.namelist():
              if file_name.startswith('XBRL_TO_CSV/jpcrp') and file_name.endswith('.csv'):
                  with the_zip.open(file_name) as the_file:
                      raw_data = the_file.read()
                      result = chardet.detect(raw_data)
                      encoding = result['encoding']
                      df = pd.read_csv(io.BytesIO(raw_data), encoding=encoding, sep='\t')
                      return df
      return None

  def save_securities_reports_in_one_day(self, date_str, company_dict):
    doc_metas = self.documents_json(date_str)
    company_5codes = [code4 + '0' for code4 in company_dict.keys()]
    for meta in doc_metas:
      code5 = meta['secCode']
      if code5 in company_5codes:
        if meta['csvFlag'] == '1' and meta['ordinanceCode'] == '010' and (
            meta['formCode'] == '030000' or meta['formCode'] == '043000'):
          print(f"name = {meta['filerName']}, docDescription = {meta['docDescription']}, docId = {meta['docID']}")
          doc_list = self.document_detail(date_str, meta['docID'])
          code4 = code5[:-1]
          company_name = company_dict[code4]
          if meta['formCode'] == '030000':
            folder = 'annual_securities_reports'
            doc_name = '有価証券報告書'
          else:
            folder = 'quarter_securities_reports'
            doc_name = '四半期報告書'

          company_folder = f"{OUTPUT_DIR}/{code4}_{company_name}/{folder}"
          os.makedirs(company_folder, exist_ok=True)
          file_path = f"{company_folder}/{date_str}_{doc_name}.tsv"
          pd.DataFrame(doc_list, columns=['項目', '値']).to_csv(file_path, sep='\t', index=False)
          print(f"Saved: {file_path}")

  def save_securities_reports(self, company_dict):
    today = datetime.today()
    print(company_dict)
    for i in range(365 * 2):
      date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
      print(date_str)
      self.save_securities_reports_in_one_day(date_str, company_dict)

if __name__ == "__main__":
  tsv = EdinetReportGetter()
  tsv.save_securities_reports(companies = {
    '5588': 'ファーストアカウンティング'
  })
