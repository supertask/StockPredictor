# モジュールのインポート
import pandas as pd
import requests
import json

# リフレッシュトークンの取得
#mail_address = ""
#password = ""

#data = {"mailaddress":mail_address, "password":password}
#r_post = requests.post(
#    "https://api.jpx-jquants.com/v1/token/auth_user",
#    data=json.dumps(data)
#)
#refresh_token = r_post.json()['refreshToken']

refresh_token = "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.aBM_avBwTaQ77VGi6jR-Q_LYB-pTT5R-hSnHYxUwzkTUypwqGONuJKG7-u7JY8v-SmRFA_A2EsVvWRdk0yflM9V0EXvLPIpwG7qRFF-AM7T_BQx-u7WAj3IgJB6PPejqIz7ePRdcc4rKgKy1kBSivOdsA6f-5BteNsoynp3Pbfw1FedihA4iOvDqIyM9dszjubb5TDpYMpV2Ot-oj5LohLGcssdYfHqffjaUq4HFmoCim35uDvsYL2NTWmIYDB4Z0vRvgCdewshbDAm2K0TYhqWZUwABuu-uuDTw3_xKhd45GCoSDLLFiICrsSLMKLVi_V8sh-TfIvoLTdj20lEjVg.Ec5O_61iJlglXIPD.C9Q49xhBHT_QNrmO55iDwJcC2Zc6sm9ZxmQXxxB2BdefjRwhXi5hUr6qHppc7o8-Gx3c32z-W7oIOmKrafs0aT_OpkGvPwaH4h5NQ8cfxNe8HPHJj8Fkmv5N519ULG7M4u8m4n02-NXNG8Imo2jOd8HW5dJpJ1MFByG-IOHjyuib0Nco96-Pv6zsw89IoCv-QyTye8NmOKGyEfrrb4fHm3EVRLzEzmFcdlXU0aLWttxOU9995c6ywfvELHU1Q3Y8iVQOFcYBECUJdjh9FKgF5Op8XN6J3W4Dy0vqXrTbTg7TkBhacVSDAmLuey845T4P_T14ujyBrUx0qmKyBeQj1kLlSQq_NEaFi9OfePNtrAnF-klCaqSDrDImkGBOp4JyCVddm92GyQtsPlKWhh2UeIUhvZJHUfiMSfWHljTReMWj8FKbLPD8tSfSrkqZxdSzuJlrvYElYkpZM6Pzj_SfFzDw02E24gTrY_Q43-EEmtxEm6F1DW3EwF9d2WjtoL46SbBw0Bq2l7HSFErSpqUfUy-K9EOqv1Qoe1oHNVPFx2VDCXQ4xJftoHsxicCYySqxLmbWGAQeauRnIEbdfxavWLnrnu53xm6p3vdQtIysKCwu7BBibyEl4gnq31NNoiW98Gda4nAyYmcaM1gt5v3sfm-86syU_-Bkm5HpQNtHSmkqsdUftP5cKmdLZ3FQZhhJ0aCOkp48TOS9y0vnuJgGpYj2LPzEX-gUlnZDthV_uUKqkGm4TSixLAY0eRpAAmysig82cGxKCFCrkj-Mdc2fqYFLpFIQ_1nW29vq07DiZRezvRIWqm0Mps4GHowIRpsOG1Qnc3urAYS79H-n61RE2wCuoXtrtOyeUOBGa20g9knR4w6hkxejAqq0ABATpLDMqn567fmUJimFCIFWXl-LhJvIzTn6gZ9jNCrMX3FOCf20lHh1YhW2JoKWTohJV3an5Gjjt_YV48W3rgsNxAEKxzIiHFUYsIRqkic3JyvOdT4i0qe6yA1fmQeUWre1MP5AoIa3NNOnlXbiINvbvDFDZqiQUZ1pFTCkKwuNdAlL49eTN3UKRk43p14Y-PM1s7OA41kK0hsAUl-B7dwqPlNZ2wvxagVG2B9rc4LcIxYIxaVlB8_ZPq1Oj0ULbBoNFTGqCVJr1E46SxPQwYLthEwdxZT3EJmswjn1AKQF5tktgBGp3tXuzI-qt-oF5UR-y7gg-K7LpckmC2dpjbanlA9QagpkAZpS7wQ6_vRkuEG4TmDjmubto8wW5nwObH7oNufZUtJKSOxvv_4KYmnj68CHRJyrWajR9ucqGYFTw0_BtOZ5VMW1s5sNPgtdsdkKjFEIttz073sstQgcNw.flMiM_-YvBOQYsxHX8WCBQ"

# IDトークンの取得
r_post = requests.post(
    f"https://api.jquants.com/v1/token/auth_refresh?refreshtoken={refresh_token}"
)
id_token = r_post.json()['idToken']

code = "160A"

# 株価情報の取得
headers = {'Authorization': 'Bearer {}'.format(id_token)}
r = requests.get(
    f"https://api.jquants.com/v1/prices/daily_quotes?code={code}",
    headers=headers
)
price_df = pd.DataFrame(r.json()['daily_quotes'])
lastest_stock_price = price_df.iloc[-1]['Close']
print(lastest_stock_price)


# 財務データの取得
headers = {'Authorization': 'Bearer {}'.format(id_token)}
r = requests.get(
    f"https://api.jquants.com/v1/fins/statements?code={code}",
    headers=headers
)
statements_df = pd.DataFrame(r.json()['statements'])
eps = float(statements_df['EarningsPerShare'].iloc[-1])
#print(statements_df[['CurrentPeriodEndDate', 'EarningsPerShare', 'ForecastEarningsPerShare']])
#print(eps)


print(lastest_stock_price / eps)
