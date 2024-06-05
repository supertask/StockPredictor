  var refreshToken = "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.Eb0xkIqw1kym-_rv3YZ2OxDUzkw6Ch8Uozb_fDBKgSax2fIwhOJ3qWQZdWism8GAuT5efAgOs5o5JdXghfIxe2jGUMqrYMQyd5YciE_YNQHZoVBnqCqR1qQkZptIMs1HkCmaMwGG-pcp0LCKNXonRLOj-y2hGQztbWeGqysq6tZcl2qshAs36TC0jszs6cmEzl2mMVtpP7Pvyxd-qY5iNPwGST-QPTQdUKxFzFp2Q3FPcvwNsum9M0eB8L-EVrM9cMclL6rSexhGzdr5m8fSLugG44eG-AEESE9ynI0hgmojhh3mG0-KoxkcfyOmyRCJupkEigL_DoiU4Cr6ax5xVA.8sFnlx54vr6_nLhL.CFXZel5zTpO2oV65AYCV-jN3xwRNKVyAM4_m71wWQd4rwy22tOCOUMG3Q9b_MDdrs1FZdI5uohJs-RF0rzOMBapVfWV062SoK4ijIDjlrpibONUBNpV-nbcv2qGVqRugEka_DLiQBr4om6YSc3E9SH0DS7eXES9gC2CN87aYRtGYIaptJajw6DX7ovUNWITlhUNCGGUg_SGig4iRYRz2i__sTReCDFWIHahB68qgrENYgdYPlgxh_o9AxIOwEHhoU5zBw3UiSNC16_IZZtDfmIXReBkkEywPMTQbqCw8HJ88KoDhLh_vUn6zfRO8anam2kB7YswF_cv9vWRATPSDyKYXKS0J-1z6yMZj11IfPfNdtpACguRsJv9Sc_e347wQmY9pyNCu08RCx_ZmO7z_Az4qmQoAZC4rCPuQkXXoO_a6atpRpF4BZVWMlWUPcyPtIugh0pkKFHaBZkh7jnmkCBnTZIkM6Yaqo93Z8qEC9OmRr13It5l2NYIENPBXJ7b3AhkIzEhVYnTed3ItPlMBh3witSP1N_aDrQ0Yiy9-F6hzQNO17K0Db5ST3A7DJMN9DsOOt0W2Hpfwsz6_WFe2liYqo7X6MLqHisZC436xpDZw4dEXrK0kgon2AZZp1GefoUdlO0YAMYVJQw5J-xxbRoQlqxI_Kzpny1RxpxO2MdUGN_GMmkIwW-w8jlMHMzHC2ryqREK5Cl-I1A7bAkzy0MZA9aI3hUEWr90RlULHXhvrrE63AJlnHFmJGTkBODejhrqbb0es_lmT9lD-U-XLVgqnbKhJI-rOef0fB2OlpV4J_cGTeGqiL_pZQBs4_FZ1nGRTO2bxbeGnuVjrz3mvuFEWBUgevqL24Cxc1a6h9D2Y86lJuh2mKTo0wFNZ5QBxd6CIcpxAxiCcsYWouEPSKpddmNdanUxv5L5Y5eSokxbZh24OniRoWf2Ox1X7JEIRIjIBg90v2ZXGNL77yh7XD7v2UaYRlq7xqSmMhupyoE_uYTSh9heB1W47R-qUn7XiwhRnlCSl3ENxamKu2_dn9hmv-nPNAfTn41KqhPXxgt8DkdGy-FXNW8P1d5_XvC4yaWWhz2cpup8g7HkfSwaNT0i69o5S1veKvT5LJ6vbYld5NnCacO5dHhPJCJQXt6rREcI2B2WNLH1K00E_c5ZLlqKhr0i766wndQ030wxfN-xCCMsPgCtYxEXzV4uLyDuofFAMS_Yd5S7gbIyzPzgHpIFCoOGl6Zw0Ng1jYPemfYiCSoBm3Tes8IKy9wGnDJuTpHY_MY8y1O5jnuaWv1I_Yn5BqcsssEhcM0VrKGAaBkoTdIB1IdGkE_Qbd4TshMFi4xFnjbPmahtjLA.EhFz_PJ-GEB5cMjVsJRdkA"; // ここにリフレッシュトークンを記入


function getIdToken(refreshToken) {
  try {
    var url = "https://api.jquants.com/v1/token/auth_refresh?refreshtoken=" + refreshToken;
    var options = {
      method: "post",
      muteHttpExceptions: true
    };
    var response = UrlFetchApp.fetch(url, options);
    var json = JSON.parse(response.getContentText());
    return json.idToken;
  } catch (error) {
    Logger.log("Error getting ID token: " + error.message);
    return null;
  }
}


function getEarningsPerShare(code, idToken) {
  try {
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
  } catch (error) {
    Logger.log("Error getting earnings per share for code " + code + ": " + error.message);
    return null;
  }
}

function getLatestStockPrice(code, idToken) {
  try {
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
  } catch (error) {
    Logger.log("Error getting latest stock price for code " + code + ": " + error.message);
    return null;
  }
}

function getCompanyInfo(code, idToken) {
  try {
    var url = "https://api.jquants.com/v1/listed/info?code=" + code;
    var options = {
      method: "get",
      headers: {
        Authorization: "Bearer " + idToken
      },
      muteHttpExceptions: true
    };
    var response = UrlFetchApp.fetch(url, options);
    var json = JSON.parse(response.getContentText());
    var info = json.info;
    //Logger.log(info);

    if (info && info.length > 0) {
      var companyInfo = info[0];
      return {
        Sector17CodeName: companyInfo.Sector17CodeName,
        Sector33CodeName: companyInfo.Sector33CodeName
      };
    } else {
      return null;
    }
  } catch (error) {
    Logger.log("Error getting company info for code " + code + ": " + error.message);
    return null;
  }
}



function getStockPrices(idToken, code) {
  try {
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
    return json.daily_quotes;
  } catch (error) {
    Logger.log("Error getting stock prices for code " + code + ": " + error.message);
    return null;
  }
}

function getTenBaggerDescription(code, idToken) {
  var dailyQuotes = getStockPrices(idToken, code);
  if (!dailyQuotes || dailyQuotes.length === 0) return null;

  var closeParam = 'AdjustmentClose';
  var firstYearPrice = dailyQuotes.slice(0, Math.min(12 * 20, dailyQuotes.length));

  var minPriceObj = firstYearPrice.reduce((min, p) => p[closeParam] < min[closeParam] ? p : min, firstYearPrice[0]);
  var buyPrice = minPriceObj[closeParam];
  var buyDate = minPriceObj.Date;

  var maxPriceObj = dailyQuotes.reduce((max, p) => p[closeParam] > max[closeParam] ? p : max, dailyQuotes[0]);
  var sellPrice = maxPriceObj[closeParam];
  var sellDate = maxPriceObj.Date;

  var buyDateObj = new Date(buyDate);
  var sellDateObj = new Date(sellDate);
  var delta = Math.abs(sellDateObj - buyDateObj);
  var years = Math.floor(delta / (365 * 24 * 60 * 60 * 1000));
  var months = Math.floor((delta % (365 * 24 * 60 * 60 * 1000)) / (30 * 24 * 60 * 60 * 1000));
  var days = Math.floor((delta % (30 * 24 * 60 * 60 * 1000)) / (24 * 60 * 60 * 1000));

  var nTimes = (sellPrice / buyPrice).toFixed(1);

  var yearsStr = years > 0 ? `${years}年` : '';
  var monthsStr = months > 0 ? `${months}ヶ月` : '';
  var daysStr = days > 0 ? `${days}日` : '';

  var tenBaggerDescription = ``;
  if (sellPrice >= 10 * buyPrice) {
    tenBaggerDescription = `${yearsStr}${monthsStr}${daysStr}で${nTimes}倍株\n最小: ${buyPrice}円 on ${buyDate}\n最大: ${sellPrice}円 on ${sellDate}`;
  } else {
    tenBaggerDescription = `${yearsStr}${monthsStr}${daysStr}で${nTimes}倍株`;
  }

  return tenBaggerDescription;
}


function updateSheetWithPERAndSectors() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var codeColumn = headers.indexOf("コード") + 1; // 「コード」の列番号
  var PERColumn = headers.indexOf("PER") + 1; // 「PER」の列番号
  var sector17Column = headers.indexOf("17業種") + 1; // 「17業種」の列番号
  var sector33Column = headers.indexOf("33業種") + 1; // 「33業種」の列番号
  var tenBaggerColumn = headers.indexOf("何倍株か") + 1; // 「何倍株か」の列番号

  if (codeColumn === 0 || PERColumn === 0 || sector17Column === 0 || sector33Column === 0 || tenBaggerColumn === 0) {
    Logger.log("「コード」、「PER」、「17業種」、「33業種」または「何倍株か」のヘッダーが見つかりませんでした。");
    return;
  }

  var range = sheet.getRange(2, codeColumn, sheet.getLastRow() - 1, 1); // 「コード」の列を取得
  var values = range.getValues();

  var idToken = getIdToken(refreshToken);

  if (!idToken) {
    Logger.log("IDトークンの取得に失敗しました。");
    return;
  }

  for (var i = 0; i < values.length; i++) {
    var code = values[i][0];
    if (code) {
      var earningsPerShare = getEarningsPerShare(code, idToken);
      var latestStockPrice = getLatestStockPrice(code, idToken);
      var companyInfo = getCompanyInfo(code, idToken);
      var tenBaggerDescription = getTenBaggerDescription(code, idToken);

      if (earningsPerShare !== null && latestStockPrice !== null) {
        var per = (latestStockPrice / earningsPerShare).toFixed(1);
        sheet.getRange(i + 2, PERColumn).setValue(per); // PERを出力
      } else {
        sheet.getRange(i + 2, PERColumn).setValue("None");
      }

      if (companyInfo !== null) {
        sheet.getRange(i + 2, sector17Column).setValue(companyInfo.Sector17CodeName); // 17業種を出力
        sheet.getRange(i + 2, sector33Column).setValue(companyInfo.Sector33CodeName); // 33業種を出力
      } else {
        sheet.getRange(i + 2, sector17Column).setValue("None");
        sheet.getRange(i + 2, sector33Column).setValue("None");
      }

      if (tenBaggerDescription === null) {
        sheet.getRange(i + 2, tenBaggerColumn).setValue("None");
      } else {
        sheet.getRange(i + 2, tenBaggerColumn).setValue(tenBaggerDescription); // 何倍株かを出力
      }
    }
  }
}