function analyzeStocks() {
  // 定数の定義
  const CEO_SHAREHOLDERS_THRESHOLD = 20;
  const MARKET_CAP_THRESHOLD = 250;
  const MULTIPLE_THRESHOLDS = [5, 7, 10]; // 5倍, 7倍, 10倍の閾値
  const CEO_SHARE_RANGES = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]; // 社長株%の範囲
  const MARKET_CAP_RANGES = [0, 50, 100, 150, 200, 250, 300, 400, 500, 1000, Infinity]; // 時価総額の範囲
  var sheetNames = ["2015", "2016"]; // 必要に応じてシート名を追加

  // スプレッドシートの取得
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  MULTIPLE_THRESHOLDS.forEach(function(N_BAGGER_THRESHOLD, index) {
    // 各N倍株用のシートを作成
    var outputSheetName = "集計" + N_BAGGER_THRESHOLD + "倍株";
    var resultSheet = ss.getSheetByName(outputSheetName) || ss.insertSheet(outputSheetName);
    resultSheet.clear();
    resultSheet.getCharts().forEach(function(chart) {
      resultSheet.removeChart(chart);
    });

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
      var sectorIndex = headers.indexOf("Sector");
      var industryIndex = headers.indexOf("Industry");

      for (var i = 1; i < values.length; i++) {
        var row = values[i];
        if (row[codeIndex]) { // コード列が空でない場合
          data.push({
            maxMultiple: row[maxMultipleIndex],
            ceoShare: row[ceoShareIndex],
            marketCap: row[marketCapIndex],
            sector: row[sectorIndex],
            industry: row[industryIndex]
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

    // 社長株%の範囲ごとの割合を計算
    var ceoShareDistribution = new Array(CEO_SHARE_RANGES.length - 1).fill(0);
    tenXStocksData = data.filter(function(stock) {
      return stock.maxMultiple >= N_BAGGER_THRESHOLD;
    });

    tenXStocksData.forEach(function(stock) {
      for (var i = 0; i < CEO_SHARE_RANGES.length - 1; i++) {
        if (stock.ceoShare >= CEO_SHARE_RANGES[i] && stock.ceoShare < CEO_SHARE_RANGES[i + 1]) {
          ceoShareDistribution[i]++;
          break;
        }
      }
    });

    ceoShareDistribution = ceoShareDistribution.map(function(count) {
      return ((count / tenXStocksData.length) * 100).toFixed(1);
    });

    // 結果をシートに表示（既存の表と2列間隔をあける）
    var ceoHoldingRow = 15;
    var ceoLabelStartColumn = resultSheet.getLastColumn() + 2;
    var ceoChartValStartColunn = ceoLabelStartColumn + 1;
    resultSheet.getRange(ceoHoldingRow, ceoLabelStartColumn, 1, 1).setValue("社長株保有率別");
    resultSheet.getRange(ceoHoldingRow + 1, ceoLabelStartColumn, CEO_SHARE_RANGES.length - 1, 1).setValues(CEO_SHARE_RANGES.slice(1).map(function(range, i) {
      return [[CEO_SHARE_RANGES[i] + " ~ " + range + "%"]];
    }));
    resultSheet.getRange(ceoHoldingRow + 1, ceoChartValStartColunn, CEO_SHARE_RANGES.length - 1, 1).setValues(ceoShareDistribution.map(function(value) {
      return [value];
    }));

    // 時価総額別の範囲ごとの割合を計算
    var marketCapDistribution = new Array(MARKET_CAP_RANGES.length - 1).fill(0);

    tenXStocksData.forEach(function(stock) {
      for (var i = 0; i < MARKET_CAP_RANGES.length - 1; i++) {
        if (stock.marketCap >= MARKET_CAP_RANGES[i] && stock.marketCap < MARKET_CAP_RANGES[i + 1]) {
          marketCapDistribution[i]++;
          break;
        }
      }
    });

    marketCapDistribution = marketCapDistribution.map(function(count) {
      return ((count / tenXStocksData.length) * 100).toFixed(1);
    });

    // 時価総額別の結果をシートに表示
    var marketCaptialRow = ceoHoldingRow;
    var capitalLabelStartColumn = resultSheet.getLastColumn() + 2;
    var capitalChartValStartColunn = capitalLabelStartColumn + 1;
    resultSheet.getRange(marketCaptialRow, capitalLabelStartColumn, 1, 1).setValue("時価総額別");
    resultSheet.getRange(marketCaptialRow + 1, capitalLabelStartColumn, MARKET_CAP_RANGES.length - 1, 1).setValues(MARKET_CAP_RANGES.slice(1).map(function(range, i) {
      return [[MARKET_CAP_RANGES[i] + " ~ " + (range === Infinity ? "以上" : range + "億")]];
    }));
    resultSheet.getRange(marketCaptialRow + 1, capitalChartValStartColunn, MARKET_CAP_RANGES.length - 1, 1).setValues(marketCapDistribution.map(function(value) {
      return [value];
    }));

    // Sector別の範囲ごとの割合を計算
    var sectorCounts = {};
    tenXStocksData.forEach(function(stock) {
      if (stock.sector in sectorCounts) {
        sectorCounts[stock.sector]++;
      } else {
        sectorCounts[stock.sector] = 1;
      }
    });

    var sectorDistribution = Object.keys(sectorCounts).map(function(key) {
      return ((sectorCounts[key] / tenXStocksData.length) * 100).toFixed(1);
    });

    // Sector別の結果をシートに表示
    var sectorRow = ceoHoldingRow;
    var sectorLabelStartColumn = resultSheet.getLastColumn() + 2;
    var sectorChartValStartColunn = sectorLabelStartColumn + 1;
    resultSheet.getRange(sectorRow, sectorLabelStartColumn, 1, 1).setValue("Sector別");
    resultSheet.getRange(sectorRow + 1, sectorLabelStartColumn, Object.keys(sectorCounts).length, 1).setValues(Object.keys(sectorCounts).map(function(value) {
      return [value];
    }));
    resultSheet.getRange(sectorRow + 1, sectorChartValStartColunn, sectorDistribution.length, 1).setValues(sectorDistribution.map(function(value) {
      return [value];
    }));

    // Industry別の範囲ごとの割合を計算
    var industryCounts = {};
    tenXStocksData.forEach(function(stock) {
      if (stock.industry in industryCounts) {
        industryCounts[stock.industry]++;
      } else {
        industryCounts[stock.industry] = 1;
      }
    });

    var industryDistribution = Object.keys(industryCounts).map(function(key) {
      return ((industryCounts[key] / tenXStocksData.length) * 100).toFixed(1);
    });

    // Industry別の結果をシートに表示
    var industryRow = ceoHoldingRow;
    industryLabelStartColumn = resultSheet.getLastColumn() + 2;
    var industryChartValStartColunn = industryLabelStartColumn + 1;
    resultSheet.getRange(industryRow, industryLabelStartColumn, 1, 1).setValue("Industry別");
    resultSheet.getRange(industryRow + 1, industryLabelStartColumn, Object.keys(industryCounts).length, 1).setValues(Object.keys(industryCounts).map(function(value) {
      return [value];
    }));
    resultSheet.getRange(industryRow + 1, industryChartValStartColunn, industryDistribution.length, 1).setValues(industryDistribution.map(function(value) {
      return [value];
    }));

    // 円グラフの作成
    createPieChart(resultSheet, "社長株保有率別", ceoHoldingRow + 1, ceoChartValStartColunn, ceoShareDistribution.length, ceoLabelStartColumn);
    createPieChart(resultSheet, "時価総額別", marketCaptialRow + 1, capitalChartValStartColunn, marketCapDistribution.length, capitalLabelStartColumn);
    createPieChart(resultSheet, "Sector別", sectorRow + 1, sectorChartValStartColunn, sectorDistribution.length, sectorLabelStartColumn);
    createPieChart(resultSheet, "Industry別", industryRow + 1, industryChartValStartColunn, industryDistribution.length, industryLabelStartColumn);
  });
}

function createPieChart(sheet, title, row, column, length, labelColumn) {
  //Logger.log(row + ", " + column + ", " + length +  ", " + 1 );

  // データを取得
  var labels = sheet.getRange(row, labelColumn, length, 1).getValues().flat();
  var values = sheet.getRange(row, column, length, 1).getValues().flat();
  //Logger.log(labels);
  //Logger.log(values);

  // データを多い順にソート
  var data = labels.map((label, index) => [label, parseFloat(values[index])]);
  data.sort((a, b) => b[1] - a[1]);
  //Logger.log(labels);
  Logger.log(values);

  // ソートしたデータを新しい範囲に設定
  sheet.getRange(row, labelColumn, length, 1).setValues(data.map(item => [item[0]]));
  sheet.getRange(row, column, length, 1).setValues(data.map(item => [item[1]]));

  // グラフの作成
  var range = sheet.getRange(row, labelColumn, length, 2); // ラベルと値の範囲を選択
  //Logger.log(range.getValues() );

  var chart = sheet.newChart()
    .setChartType(Charts.ChartType.PIE)
    .addRange(range)
    .setPosition(1, labelColumn, 0, 0) // セルの参照を使用して位置を設定
    .setOption('title', title)
    .setOption('width', 300) // 幅を設定
    .setOption('height', 200) // 高さを設定
    .build();

  sheet.insertChart(chart);
}