//
// 社長株%が30 ~ 50%のレンジで指定するなどして、高い数値を探す
//

function analyzeStocks() {
  // 定数の定義
  const CEO_SHAREHOLDERS_THRESHOLD = 20;
  const MARKET_CAP_THRESHOLD = 250;
  const MULTIPLE_THRESHOLDS = [5, 7, 10]; // 5倍, 7倍, 10倍の閾値
  var sheetNames = ["2015", "2016"]; // 必要に応じてシート名を追加

  // スプレッドシートの取得
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  MULTIPLE_THRESHOLDS.forEach(function(N_BAGGER_THRESHOLD) {
    // 各N倍株用のシートを作成
    var outputSheetName = "集計" + N_BAGGER_THRESHOLD + "倍株";
    var resultSheet = ss.getSheetByName(outputSheetName) || ss.insertSheet(outputSheetName);
    resultSheet.clear();

    var data = [];

    // 各シートからデータを取得
    sheetNames.forEach(function(sheetName) {
      var sheet = ss.getSheetByName(sheetName);
      if (!sheet) return;

      var values = sheet.getDataRange().getValues();
      var headers = values[0];
      var codeIndex = headers.indexOf("コード");
      var maxMultipleIndex = headers.indexOf("最大何倍株");
      var ceoShareIndex = headers.indexOf("社長株%");
      var marketCapIndex = headers.indexOf("時価総額_上場1年以内（億円）");

      for (var i = 1; i < values.length; i++) {
        var row = values[i];
        if (row[codeIndex]) { // コード列が空でない場合
          data.push({
            maxMultiple: row[maxMultipleIndex],
            ceoShare: row[ceoShareIndex],
            marketCap: row[marketCapIndex]
          });
        }
      }
    });

    // 分析
    var totalStocks = data.length;
    var tenXStocks = data.filter(function(stock) {
      return stock.maxMultiple >= N_BAGGER_THRESHOLD;
    }).length;

    // 結果を計算
    var tenXPercentage = ((tenXStocks / totalStocks) * 100).toFixed(1);
    var nonTenXPercentage = (100 - tenXPercentage).toFixed(1);

    // フィルタ条件の分析
    var ceoFilterData = data.filter(function(stock) {
      return stock.ceoShare >= CEO_SHAREHOLDERS_THRESHOLD;
    });
    var ceoTenXStocks = ceoFilterData.filter(function(stock) {
      return stock.maxMultiple >= N_BAGGER_THRESHOLD;
    }).length;
    var ceoTotalStocks = ceoFilterData.length;
    var ceoTenXPercentage = ((ceoTenXStocks / ceoTotalStocks) * 100).toFixed(1);
    var ceoNonTenXPercentage = (100 - ceoTenXPercentage).toFixed(1);

    var marketCapFilterData = data.filter(function(stock) {
      return stock.marketCap <= MARKET_CAP_THRESHOLD;
    });
    var marketCapTenXStocks = marketCapFilterData.filter(function(stock) {
      return stock.maxMultiple >= N_BAGGER_THRESHOLD;
    }).length;
    var marketCapTotalStocks = marketCapFilterData.length;
    var marketCapTenXPercentage = ((marketCapTenXStocks / marketCapTotalStocks) * 100).toFixed(1);
    var marketCapNonTenXPercentage = (100 - marketCapTenXPercentage).toFixed(1);

    // 結果をシートに表示
    resultSheet.appendRow(["条件", N_BAGGER_THRESHOLD + "倍株 %", "それ以外 %"]);
    resultSheet.appendRow(["全体", tenXPercentage, nonTenXPercentage]);
    resultSheet.appendRow(["社長株 % >= " + CEO_SHAREHOLDERS_THRESHOLD, ceoTenXPercentage, ceoNonTenXPercentage]);
    resultSheet.appendRow(["時価総額_上場1年以内 <= " + MARKET_CAP_THRESHOLD + "億円", marketCapTenXPercentage, marketCapNonTenXPercentage]);
  });
}

