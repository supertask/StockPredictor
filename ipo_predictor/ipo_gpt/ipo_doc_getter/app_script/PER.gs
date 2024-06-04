function getIdToken(refreshToken) {
  var url = "https://api.jquants.com/v1/token/auth_refresh?refreshtoken=" + refreshToken;
  var options = {
    method: "post",
    muteHttpExceptions: true
  };
  var response = UrlFetchApp.fetch(url, options);
  var json = JSON.parse(response.getContentText());
  return json.idToken;
}

function getEarningsPerShare(code, idToken) {
  var url = "https://api.jquants.com/v1/fins/statements?code=" + code;
  var options = {
    method: "get",
    headers: {
      Authorization: "Bearer " + idToken
    },
    muteHttpExceptions: true
  };
  var response = UrlFetchApp.fetch(url, options);
  var json = JSON.parse(response.getContentText());
  var statements = json.statements;
  if (statements && statements.length > 0) {
    var earningsPerShare = statements[statements.length - 1].EarningsPerShare;
    return earningsPerShare;
  } else {
    return null;
  }
}

function getLatestStockPrice(code, idToken) {
  var url = "https://api.jquants.com/v1/prices/daily_quotes?code=" + code;
  var options = {
    method: "get",
    headers: {
      Authorization: "Bearer " + idToken
    },
    muteHttpExceptions: true
  };
  var response = UrlFetchApp.fetch(url, options);
  var json = JSON.parse(response.getContentText());
  var dailyQuotes = json.daily_quotes;
  if (dailyQuotes && dailyQuotes.length > 0) {
    var latestStockPrice = dailyQuotes[dailyQuotes.length - 1].Close;
    return latestStockPrice;
  } else {
    return null;
  }
}

function updateSheetWithPER() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  // 「コード」と「PER」のヘッダーをもとに列番号を取得
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var codeColumn = headers.indexOf("コード") + 1; // 「コード」の列番号
  var PERColumn = headers.indexOf("PER") + 1; // 「PER」の列番号
  
  if (codeColumn === 0 || PERColumn === 0) {
    Logger.log("「コード」または「PER」のヘッダーが見つかりませんでした。");
    return;
  }
  
  var range = sheet.getRange(2, codeColumn, sheet.getLastRow() - 1, 1); // 「コード」の列を取得
  var values = range.getValues();

  var refreshToken = "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.aBM_avBwTaQ77VGi6jR-Q_LYB-pTT5R-hSnHYxUwzkTUypwqGONuJKG7-u7JY8v-SmRFA_A2EsVvWRdk0yflM9V0EXvLPIpwG7qRFF-AM7T_BQx-u7WAj3IgJB6PPejqIz7ePRdcc4rKgKy1kBSivOdsA6f-5BteNsoynp3Pbfw1FedihA4iOvDqIyM9dszjubb5TDpYMpV2Ot-oj5LohLGcssdYfHqffjaUq4HFmoCim35uDvsYL2NTWmIYDB4Z0vRvgCdewshbDAm2K0TYhqWZUwABuu-uuDTw3_xKhd45GCoSDLLFiICrsSLMKLVi_V8sh-TfIvoLTdj20lEjVg.Ec5O_61iJlglXIPD.C9Q49xhBHT_QNrmO55iDwJcC2Zc6sm9ZxmQXxxB2BdefjRwhXi5hUr6qHppc7o8-Gx3c32z-W7oIOmKrafs0aT_OpkGvPwaH4h5NQ8cfxNe8HPHJj8Fkmv5N519ULG7M4u8m4n02-NXNG8Imo2jOd8HW5dJpJ1MFByG-IOHjyuib0Nco96-Pv6zsw89IoCv-QyTye8NmOKGyEfrrb4fHm3EVRLzEzmFcdlXU0aLWttxOU9995c6ywfvELHU1Q3Y8iVQOFcYBECUJdjh9FKgF5Op8XN6J3W4Dy0vqXrTbTg7TkBhacVSDAmLuey845T4P_T14ujyBrUx0qmKyBeQj1kLlSQq_NEaFi9OfePNtrAnF-klCaqSDrDImkGBOp4JyCVddm92GyQtsPlKWhh2UeIUhvZJHUfiMSfWHljTReMWj8FKbLPD8tSfSrkqZxdSzuJlrvYElYkpZM6Pzj_SfFzDw02E24gTrY_Q43-EEmtxEm6F1DW3EwF9d2WjtoL46SbBw0Bq2l7HSFErSpqUfUy-K9EOqv1Qoe1oHNVPFx2VDCXQ4xJftoHsxicCYySqxLmbWGAQeauRnIEbdfxavWLnrnu53xm6p3vdQtIysKCwu7BBibyEl4gnq31NNoiW98Gda4nAyYmcaM1gt5v3sfm-86syU_-Bkm5HpQNtHSmkqsdUftP5cKmdLZ3FQZhhJ0aCOkp48TOS9y0vnuJgGpYj2LPzEX-gUlnZDthV_uUKqkGm4TSixLAY0eRpAAmysig82cGxKCFCrkj-Mdc2fqYFLpFIQ_1nW29vq07DiZRezvRIWqm0Mps4GHowIRpsOG1Qnc3urAYS79H-n61RE2wCuoXtrtOyeUOBGa20g9knR4w6hkxejAqq0ABATpLDMqn567fmUJimFCIFWXl-LhJvIzTn6gZ9jNCrMX3FOCf20lHh1YhW2JoKWTohJV3an5Gjjt_YV48W3rgsNxAEKxzIiHFUYsIRqkic3JyvOdT4i0qe6yA1fmQeUWre1MP5AoIa3NNOnlXbiINvbvDFDZqiQUZ1pFTCkKwuNdAlL49eTN3UKRk43p14Y-PM1s7OA41kK0hsAUl-B7dwqPlNZ2wvxagVG2B9rc4LcIxYIxaVlB8_ZPq1Oj0ULbBoNFTGqCVJr1E46SxPQwYLthEwdxZT3EJmswjn1AKQF5tktgBGp3tXuzI-qt-oF5UR-y7gg-K7LpckmC2dpjbanlA9QagpkAZpS7wQ6_vRkuEG4TmDjmubto8wW5nwObH7oNufZUtJKSOxvv_4KYmnj68CHRJyrWajR9ucqGYFTw0_BtOZ5VMW1s5sNPgtdsdkKjFEIttz073sstQgcNw.flMiM_-YvBOQYsxHX8WCBQ"; // ここにリフレッシュトークンを記入
  
  var idToken = getIdToken(refreshToken);


  for (var i = 0; i < values.length; i++) {
    var code = values[i][0];
    if (code) {
      var earningsPerShare = getEarningsPerShare(code, idToken);
      var latestStockPrice = getLatestStockPrice(code, idToken);
      if (earningsPerShare !== null && latestStockPrice !== null) {
        var per = (latestStockPrice / earningsPerShare).toFixed(1);
        sheet.getRange(i + 2, PERColumn).setValue(per); // E列にPERを出力
      } else {
        sheet.getRange(i + 2, PERColumn).setValue("None");
      }
    }
  }

}

