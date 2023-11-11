import time
import csv
import pandas as pd
import re
import os

FIXED_OUTPUT_DIR = "fixed_output/"
COMMON_DROP_OFF_COLUMNS = ['予想', '前回', 'Unnamed: 5']

# Revised function to accurately convert the date format
def convert_date_format_revised(date_str):
    match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日.*', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return None

# Function to convert "K" values to integers
def convert_k_values(value):
    if 'K' in str(value):
        return int(float(value.replace('K', '').replace(',', '')) * 1000)
    return value

# Generic function to clean and save data
def clean_and_save_data(input_path, drop_columns, result_conversion=None, additional_processing=None, rename_columns=None):
    data = pd.read_csv(input_path)
    data_cleaned = data.drop(columns=drop_columns)
    data_cleaned['公表日時'] = data_cleaned['公表日時'].apply(convert_date_format_revised)
    data_cleaned.sort_values(by='公表日時', inplace=True)  # 公表日時でソート

    data_cleaned = data_cleaned[data_cleaned['結果'].notna() & data_cleaned['結果'].ne('') & data_cleaned['結果'].ne(' ')]

    if additional_processing:
        data_cleaned = additional_processing(data_cleaned)

    if result_conversion:
        data_cleaned['結果'] = data_cleaned['結果'].apply(result_conversion)

    if rename_columns:
        data_cleaned.rename(columns=rename_columns, inplace=True)

    fixed_output_path = os.path.join(FIXED_OUTPUT_DIR, "fixed_" + os.path.basename(input_path))
    data_cleaned.to_csv(fixed_output_path, index=False)



# Additional processing functions
def remove_empty_results(data):
    data['結果'] = data['結果'].astype(str)
    return data[data['結果'].str.strip() != '']

def remove_whitespace_from_time(data):
    data['時間'] = data['時間'].str.strip()
    return data

# Functions for each dataset
def convert_cb_consumer_confidence(input_path):
    clean_and_save_data(input_path, COMMON_DROP_OFF_COLUMNS)

def convert_percent_csv(input_path):
    clean_and_save_data(input_path, COMMON_DROP_OFF_COLUMNS, 
                        result_conversion=lambda x: pd.to_numeric(x.rstrip('%'), errors='coerce'),
						rename_columns={'結果': '結果（%）'})

def convert_k_value_csv(input_path):
    clean_and_save_data(input_path, COMMON_DROP_OFF_COLUMNS, 
                        result_conversion=convert_k_values, additional_processing=remove_empty_results)

def convert_ism_manufacturing_pmi(input_path):
    clean_and_save_data(input_path, COMMON_DROP_OFF_COLUMNS, 
                        additional_processing=remove_empty_results)

def convert_michigan_consumer_sentiment(input_path):
    clean_and_save_data(input_path, COMMON_DROP_OFF_COLUMNS, 
                        additional_processing=remove_whitespace_from_time)

def convert_nikkei(input_path):
    data = pd.read_csv(input_path)
    data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d') # 意味はないが、日付の形式を変更する
    keys = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    for key in keys:
        data[key] = pd.to_numeric(data[key], errors='coerce')
    data.dropna(inplace=True)
    data.sort_values(by='Date', inplace=True)  # 日付でソート

    fixed_output_path = os.path.join(FIXED_OUTPUT_DIR, "fixed_" + os.path.basename(input_path))
    data.to_csv(fixed_output_path, index=False)

convert_cb_consumer_confidence("output/cb_consumer_confidence.csv")
convert_percent_csv("output/core_cpi.csv")
convert_percent_csv("output/core_durable_goods_orders.csv")
convert_percent_csv("output/industrial_production.csv")
convert_k_value_csv("output/initial_jobless_claims.csv")
convert_ism_manufacturing_pmi("output/ism_manufacturing_pmi.csv")
convert_michigan_consumer_sentiment("output/michigan-consumer-sentiment.csv")
convert_k_value_csv("output/nonfarm_payrolls.csv")
convert_percent_csv("output/personal_spending.csv")
convert_percent_csv("output/retail_sales.csv")
convert_percent_csv("output/unemployment_rate.csv")
convert_nikkei("output/nikkei_225.csv")