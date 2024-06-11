const refreshToken = ScriptProperties.getProperty('JQUANTS_KEY');

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

function getNBaggerInfo(code, idToken) {
  var dailyQuotes = getStockPrices(idToken, code);
  if (!dailyQuotes || dailyQuotes.length === 0) return null;

  //
  //買う値段（最小の株価）を取得
  //
  var closeParam = 'AdjustmentClose';
  var FIRST_YEAR_DAYS = 12 * 20;
  var firstYearPrice = dailyQuotes.slice(0, Math.min(FIRST_YEAR_DAYS, dailyQuotes.length));
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
  var buyDateObj = new Date(buyDate);

  //
  // Nバガーの判定： 売る値段 / 買った値段
  //
  var remainingQuotes = dailyQuotes.slice(
    dailyQuotes.length < FIRST_YEAR_DAYS ? 0 : FIRST_YEAR_DAYS,
    dailyQuotes.length);

  // 5倍株になった年数
  var fiveBaggerObj = remainingQuotes.find(p => p[closeParam] >= buyPrice * 5);
  var fiveBaggerYears;
  if (fiveBaggerObj) {
    var fiveBaggerDateObj = new Date(fiveBaggerObj.Date);
    var deltaFive = Math.abs(fiveBaggerDateObj - buyDateObj);
    fiveBaggerYears = (deltaFive / (365 * 24 * 60 * 60 * 1000)).toFixed(2);
  } else {
    fiveBaggerYears = "None";
  }

  // 10倍株になった年数
  var tenBaggerObj = remainingQuotes.find(p => p[closeParam] >= buyPrice * 10);
  var tenBaggerYears;
  if (tenBaggerObj) {
    var tenBaggerDateObj = new Date(tenBaggerObj.Date);
    var deltaTen = Math.abs(tenBaggerDateObj - buyDateObj);
    tenBaggerYears = (deltaTen / (365 * 24 * 60 * 60 * 1000)).toFixed(2);
  } else {
    tenBaggerYears = "None";
  }

  //最大何倍株になったことがあるか
  var maxPriceObj = remainingQuotes.reduce((max, p) => p[closeParam] > max[closeParam] ? p : max, dailyQuotes[0]);
  var sellPrice = maxPriceObj[closeParam];
  var sellDate = maxPriceObj.Date;
  var sellDateObj = new Date(sellDate);
  var delta = Math.abs(sellDateObj - buyDateObj);
  var nBaggerYears = (delta / (365 * 24 * 60 * 60 * 1000)).toFixed(2);
  var maxNBagger = (sellPrice / buyPrice).toFixed(1); //最大何倍株か

  //購入した株価から現在の株価で何倍株になったか
  var nBagger = -1;

  Logger.log(`nBagger: ${nBagger}, maxNBagger: ${maxNBagger}, fiveBaggerYears: ${fiveBaggerYears}, tenBaggerYears: ${tenBaggerYears}, nBaggerYears: ${nBaggerYears}`);

  return [nBagger, maxNBagger, fiveBaggerYears, tenBaggerYears, nBaggerYears];
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

function updateSheetWithTenBagger() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var codeColumn = headers.indexOf("コード") + 1;
  var maxNBaggerColumn = headers.indexOf("最大何倍株") + 1;
  var nBaggerColumn = headers.indexOf("現在何倍株") + 1;
  var nYearByFiveBaggerColumn = headers.indexOf("何年で5倍株") + 1;
  var nYearByTenBaggerColumn = headers.indexOf("何年で10倍株") + 1;
  var nYearByNBaggerColunn = headers.indexOf("何年で最大N倍株") + 1;

  if (codeColumn === 0 || maxNBaggerColumn === 0　 || nYearByTenBaggerColumn == 0 || nYearByNBaggerColunn == 0) {
    Logger.log("「コード」または「最大何倍株」または「何年で5倍株」または「何年で10倍株」または「何年で最大N倍株」のヘッダーが見つかりませんでした。");
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
    if (i > 10) { break; }

    var code = values[i][0];
    if (code) {
      var nBaggerInfo = getNBaggerInfo(code, idToken);
      if (nBaggerInfo === null){
        sheet.getRange(i + 2, nBaggerColumn).setValue("None");
        sheet.getRange(i + 2, maxNBaggerColumn).setValue("None");
        sheet.getRange(i + 2, nYearByFiveBaggerColumn).setValue("None");
        sheet.getRange(i + 2, nYearByTenBaggerColumn).setValue("None");
        sheet.getRange(i + 2, nYearByNBaggerColunn).setValue("None");
      } else {
        var nBagger = nBaggerInfo[0];
        var maxNBagger = nBaggerInfo[1];
        var fiveBaggerYears = nBaggerInfo[2];
        var tenBaggerYears = nBaggerInfo[3];
        var nBaggerYears = nBaggerInfo[4];

        sheet.getRange(i + 2, nBaggerColumn).setValue(nBagger);
        sheet.getRange(i + 2, maxNBaggerColumn).setValue(maxNBagger);
        sheet.getRange(i + 2, nYearByFiveBaggerColumn).setValue(fiveBaggerYears);
        sheet.getRange(i + 2, nYearByTenBaggerColumn).setValue(tenBaggerYears);
        sheet.getRange(i + 2, nYearByNBaggerColunn).setValue(nBaggerYears);
      }
    }
  }
}
