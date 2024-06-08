
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

function getNBaggerDescription(code, idToken) {
  var dailyQuotes = getStockPrices(idToken, code);
  if (!dailyQuotes || dailyQuotes.length === 0) return null;

  //
  //買う値段（最小の株価）を取得
  //
  var closeParam = 'AdjustmentClose';
  var firstYearPrice = dailyQuotes.slice(0, Math.min(12 * 20, dailyQuotes.length));
  var initialValue = firstYearPrice.find(p => p[closeParam] !== null);
  if (initialValue === null) {
    throw new Error("No valid initial value found");
  }
  var minPriceObj = firstYearPrice.reduce((min, p) => {
    if (p[closeParam] === null) { return min; }
    return p[closeParam] < min[closeParam] ? p : min;
  }, initialValue);
  var buyPrice = minPriceObj[closeParam];
  var buyDate = minPriceObj.Date;

  //
  //売る値段（最大の株価）を取得
  //
  var maxPriceObj = dailyQuotes.reduce((max, p) => p[closeParam] > max[closeParam] ? p : max, dailyQuotes[0]);
  var sellPrice = maxPriceObj[closeParam];
  var sellDate = maxPriceObj.Date;

  var buyDateObj = new Date(buyDate);
  var sellDateObj = new Date(sellDate);
  var delta = Math.abs(sellDateObj - buyDateObj);
  var years = Math.floor(delta / (365 * 24 * 60 * 60 * 1000));
  var months = Math.floor((delta % (365 * 24 * 60 * 60 * 1000)) / (30 * 24 * 60 * 60 * 1000));
  var days = Math.floor((delta % (30 * 24 * 60 * 60 * 1000)) / (24 * 60 * 60 * 1000));

  var nBagger = (sellPrice / buyPrice).toFixed(1);

  var yearsStr = years > 0 ? `${years}年` : '';
  var monthsStr = months > 0 ? `${months}ヶ月` : '';
  var daysStr = days > 0 ? `${days}日` : '';

  var tenBaggerDescription = `${yearsStr}${monthsStr}${daysStr}で${nBagger}倍株\n最小: ${buyPrice}円 on ${buyDate}\n最大: ${sellPrice}円 on ${sellDate}`;

  return [nBagger,　tenBaggerDescription];
}



function updateSheetWithPER() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var codeColumn = headers.indexOf("コード") + 1;
  var PERColumn = headers.indexOf("PER") + 1;

  if (codeColumn === 0 || PERColumn === 0) {
    Logger.log("「コード」または「PER」のヘッダーが見つかりませんでした。");
    return;
  }

  var range = sheet.getRange(2, codeColumn, sheet.getLastRow() - 1, 1);
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

      if (earningsPerShare !== null && latestStockPrice !== null) {
        var per = (latestStockPrice / earningsPerShare).toFixed(1);
        sheet.getRange(i + 2, PERColumn).setValue(per);
      } else {
        sheet.getRange(i + 2, PERColumn).setValue("None");
      }
    }
  }
}

function updateSheetWithSectors() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var codeColumn = headers.indexOf("コード") + 1;
  var sector17Column = headers.indexOf("17業種") + 1;
  var sector33Column = headers.indexOf("33業種") + 1;

  if (codeColumn === 0 || sector17Column === 0 || sector33Column === 0) {
    Logger.log("「コード」、「17業種」または「33業種」のヘッダーが見つかりませんでした。");
    return;
  }

  var range = sheet.getRange(2, codeColumn, sheet.getLastRow() - 1, 1);
  var values = range.getValues();
  var idToken = getIdToken(refreshToken);

  if (!idToken) {
    Logger.log("IDトークンの取得に失敗しました。");
    return;
  }

  for (var i = 0; i < values.length; i++) {
    var code = values[i][0];
    if (code) {
      var companyInfo = getCompanyInfo(code, idToken);
      if (companyInfo !== null) {
        sheet.getRange(i + 2, sector17Column).setValue(companyInfo.Sector17CodeName);
        sheet.getRange(i + 2, sector33Column).setValue(companyInfo.Sector33CodeName);
      } else {
        sheet.getRange(i + 2, sector17Column).setValue("None");
        sheet.getRange(i + 2, sector33Column).setValue("None");
      }
    }
  }
}

function updateSheetWithTenBagger() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var codeColumn = headers.indexOf("コード") + 1;
  var tenBaggerColumn = headers.indexOf("何倍株か") + 1;
  var tenBaggerDetailColumn = headers.indexOf("何倍株かの詳細") + 1;

  if (codeColumn === 0 || tenBaggerColumn === 0　 || tenBaggerDetailColumn == 0) {
    Logger.log("「コード」または「何倍株か」または「何倍株かの詳細」のヘッダーが見つかりませんでした。");
    return;
  }

  var range = sheet.getRange(2, codeColumn, sheet.getLastRow() - 1, 1);
  var values = range.getValues();
  var idToken = getIdToken(refreshToken);

  if (!idToken) {
    Logger.log("IDトークンの取得に失敗しました。");
    return;
  }

  for (var i = 0; i < values.length; i++) {
    var code = values[i][0];
    if (code) {
      var nBaggerDescription = getNBaggerDescription(code, idToken);
      if (nBaggerDescription === null){
        sheet.getRange(i + 2, tenBaggerColumn).setValue("None");
        sheet.getRange(i + 2, tenBaggerDetailColumn).setValue("None");
      } else {
        var nBagger = nBaggerDescription[0];
        var nBaggerDetail = nBaggerDescription[1];
        sheet.getRange(i + 2, tenBaggerColumn).setValue(nBagger);
        sheet.getRange(i + 2, tenBaggerDetailColumn).setValue(nBaggerDetail);
      }
    }
  }
}
