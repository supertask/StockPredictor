import requests
import zipfile
import io
import pandas as pd
import urllib3
import chardet

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api_key = open('../.token/edinet_api_key', 'r').read().rstrip()


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
    url = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
    params = {
      "type" : 2,
      "date" : date,
      "Subscription-Key": api_key
    }
    res = requests.get(url, params=params, verify=False)
    return res.json()['results']

  def document_detail(self, date, doc_id):
    url = f"https://api.edinet-fsa.go.jp/api/v2/documents/{doc_id}"
    params = {
      "type" : 5, #csv
      "date" : date,
      "Subscription-Key": api_key
    }
    res = requests.get(url, params=params, verify=False)
    tsv_df = self.extract_tsv_from_zip(res)
    doc_dict = {}
    for key, securities_type in self.securities_items.items():
      matching_row = tsv_df[tsv_df["要素ID"] == key]
      if matching_row.empty:
        doc_dict[securities_type] = None
      else:
        doc_dict[securities_type] = matching_row["値"].values[0]
      #print(f"{securities_type}: {doc_data[securities_type]}")
    return doc_dict


  def extract_tsv_from_zip(self, response):
      with zipfile.ZipFile(io.BytesIO(response.content)) as the_zip:
          for file_name in the_zip.namelist():
              if file_name.startswith('XBRL_TO_CSV/jpcrp') and file_name.endswith('.csv'):
                  print(file_name)
                  with the_zip.open(file_name) as the_file:
                      raw_data = the_file.read()
                      result = chardet.detect(raw_data)
                      encoding = result['encoding']
                      #print(f"Detected encoding: {encoding}")
                      df = pd.read_csv(io.BytesIO(raw_data), encoding=encoding, sep='\t')
                      return df
      return None
  
  def save_securities_reports(self, company_codes = ['55880']):
    #date_str = "2023-11-14"
    date_str = "2024-03-28"
    doc_metas = self.documents_json(date_str)

    for meta in doc_metas:
      if meta['secCode'] in company_codes:
        # 有価証券報告書 = 030000
        # 四半期報告書　 = 043000
        if meta['csvFlag'] == '1' and meta['ordinanceCode'] == '010' and (
            meta['formCode'] == '030000' or meta['formCode'] == '043000'):
          print(f"name = {meta['filerName']}, docDescription = {meta['docDescription']}, docId = {meta['docID']}")
          doc_dict = self.document_detail(date_str, meta['docID'])
          print(doc_dict)

if __name__ == "__main__":
  tsv = EdinetReportGetter()
  tsv.save_securities_reports()