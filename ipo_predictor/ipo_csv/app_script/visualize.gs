function analyzeStocks() {
  // 定数の定義
  const CEO_SHAREHOLDERS_THRESHOLD = 1;
  const MARKET_CAP_THRESHOLD = 250;
  const MULTIPLE_THRESHOLDS = [5, 7, 10]; // 5倍, 7倍, 10倍の閾値
  const CEO_SHARE_RANGES = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]; // 社長株%の範囲
  const MARKET_CAP_RANGES = [0, 50, 100, 150, 200, 250, 300, 400, 500, 1000, Infinity]; // 時価総額の範囲
  const STRONG_INDUSTRIES = [
    "不動産_不動産サービス", //不動産の10倍株は結構簡単そう
    //"技術_情報技術サービス",
    //"産業_専門ビジネスサービス",
    //"通信サービス_インターネットコンテンツ・情報",
    //"ヘルスケア_バイオテクノロジー",
    //"産業_コンサルティングサービス",
    //"消費者防衛_教育・訓練サービス",
    //"通信サービス_広告代理店",
    //"技術_ソフトウェア - アプリケーション",
    //"通信サービス_電気通信サービス",
    //"ヘルスケア_医薬品メーカー - 専門・ジェネリック",
    //"消費者循環_個人サービス",
    //"消費者循環_衣料品小売",
    //"技術_電子部品",
    //"消費者循環_インターネット小売",
    //"技術_半導体",
    //"基礎材料_特殊化学品",
    //"消費者防衛_包装食品",
    //"消費者循環_自動車・トラック販売",
    //"産業_廃棄物管理",
    //"公共事業_再生可能エネルギー",
    //"産業_コングロマリット",
    //"通信サービス_電子ゲーム・マルチメディア"

  ];
  var sheetNames = ["2015", "2016", "2017", "2018", "2019"];

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
      var yearsToMultipleIndex = headers.indexOf("5,7,10,N倍まで何年");

      for (var i = 1; i < values.length; i++) {
        var row = values[i];
        if (row[codeIndex]) { // コード列が空でない場合
          var yearsToMultiple = row[yearsToMultipleIndex].split('\n').map(parseFloat);
          data.push({
            maxMultiple: row[maxMultipleIndex],
            ceoShare: row[ceoShareIndex],
            marketCap: row[marketCapIndex],
            sector: row[sectorIndex],
            industry: row[industryIndex],
            yearsToMultiple: yearsToMultiple[index] // 適切な倍率までの年数
          });
        }
      }
    });

    // 分析
    var totalStocks = data.length;
    var nXStocks = data.filter(function(stock) {
      return stock.maxMultiple >= N_BAGGER_THRESHOLD;
    }).length;

    // 結果を計算
    var nXPercentage = ((nXStocks / totalStocks) * 100).toFixed(1);

    // フィルタ条件の分析
    var ceoFilterData = data.filter(function(stock) {
      return stock.ceoShare >= CEO_SHAREHOLDERS_THRESHOLD;
    });
    var ceoNXStocks = ceoFilterData.filter(function(stock) {
      return stock.maxMultiple >= N_BAGGER_THRESHOLD;
    }).length;
    var ceoTotalStocks = ceoFilterData.length;
    var ceoNXPercentage = ((ceoNXStocks / ceoTotalStocks) * 100).toFixed(1);

    var marketCapFilterData = data.filter(function(stock) {
      return stock.marketCap <= MARKET_CAP_THRESHOLD;
    });
    var marketCapNXStocks = marketCapFilterData.filter(function(stock) {
      return stock.maxMultiple >= N_BAGGER_THRESHOLD;
    }).length;
    var marketCapTotalStocks = marketCapFilterData.length;
    var marketCapNXPercentage = ((marketCapNXStocks / marketCapTotalStocks) * 100).toFixed(1);

    var ceoAndMarketCapFilterData = data.filter(function(stock) {
      return stock.ceoShare >= CEO_SHAREHOLDERS_THRESHOLD && stock.marketCap <= MARKET_CAP_THRESHOLD;
    });
    var ceoAndMarketCapNXStocks = ceoAndMarketCapFilterData.filter(function(stock) {
      return stock.maxMultiple >= N_BAGGER_THRESHOLD;
    }).length;
    var ceoAndMarketCapTotalStocks = ceoAndMarketCapFilterData.length;
    var ceoAndMarketCapNXPercentage = ((ceoAndMarketCapNXStocks / ceoAndMarketCapTotalStocks) * 100).toFixed(1);

    var ceoMarketCapAndIndustryFilterData = ceoAndMarketCapFilterData.filter(function(stock) {
      return STRONG_INDUSTRIES.includes(stock.sector + "_" + stock.industry);
    });
    var ceoMarketCapAndIndustryNXStocks = ceoMarketCapAndIndustryFilterData.filter(function(stock) {
      return stock.maxMultiple >= N_BAGGER_THRESHOLD;
    }).length;
    var ceoMarketCapAndIndustryTotalStocks = ceoMarketCapAndIndustryFilterData.length;
    var ceoMarketCapAndIndustryNXPercentage = ((ceoMarketCapAndIndustryNXStocks / ceoMarketCapAndIndustryTotalStocks) * 100).toFixed(1);

    // 結果をシートに表示
    resultSheet.appendRow(["条件", N_BAGGER_THRESHOLD + "倍株 %"]);
    resultSheet.appendRow(["全体", nXPercentage]);
    resultSheet.appendRow(["社長株 % >= " + CEO_SHAREHOLDERS_THRESHOLD, ceoNXPercentage]);
    resultSheet.appendRow(["時価総額_上場1年以内 <= " + MARKET_CAP_THRESHOLD + "億円", marketCapNXPercentage]);
    resultSheet.appendRow(["社長株 % >= " + CEO_SHAREHOLDERS_THRESHOLD + "かつ時価総額_上場1年以内 <= " + MARKET_CAP_THRESHOLD + "億円", ceoAndMarketCapNXPercentage]);
    resultSheet.appendRow(["社長株 % >= " + CEO_SHAREHOLDERS_THRESHOLD + "かつ時価総額_上場1年以内 <= " + MARKET_CAP_THRESHOLD + "億円かつ強い産業", ceoMarketCapAndIndustryNXPercentage]);

    // 社長株%の範囲ごとの割合を計算
    var ceoShareDistribution = new Array(CEO_SHARE_RANGES.length - 1).fill(0);
    var nXStocksData = data.filter(function(stock) {
      return stock.maxMultiple >= N_BAGGER_THRESHOLD;
    });

    nXStocksData.forEach(function(stock) {
      for (var i = 0; i < CEO_SHARE_RANGES.length - 1; i++) {
        if (stock.ceoShare >= CEO_SHARE_RANGES[i] && stock.ceoShare < CEO_SHARE_RANGES[i + 1]) {
          ceoShareDistribution[i]++;
          break;
        }
      }
    });

    ceoShareDistribution = ceoShareDistribution.map(function(count) {
      return count;
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

    nXStocksData.forEach(function(stock) {
      for (var i = 0; i < MARKET_CAP_RANGES.length - 1; i++) {
        if (stock.marketCap >= MARKET_CAP_RANGES[i] && stock.marketCap < MARKET_CAP_RANGES[i + 1]) {
          marketCapDistribution[i]++;
          break;
        }
      }
    });

    marketCapDistribution = marketCapDistribution.map(function(count) {
      return count;
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
    nXStocksData.forEach(function(stock) {
      if (stock.sector in sectorCounts) {
        sectorCounts[stock.sector]++;
      } else {
        sectorCounts[stock.sector] = 1;
      }
    });

    var sectorDistribution = Object.keys(sectorCounts).map(function(key) {
      return sectorCounts[key];
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
    nXStocksData.forEach(function(stock) {
      var industryType = stock.sector + "_" + stock.industry;

      if (industryType in industryCounts) {
        industryCounts[industryType]++;
      } else {
        industryCounts[industryType] = 1;
      }
    });

    var industryDistribution = Object.keys(industryCounts).map(function(key) {
      return industryCounts[key];
    });

    var industryYearsToNX = {}; //産業ごとのN倍株にかかるまでの年数
    nXStocksData.forEach(function(stock) {
      var industryType = stock.sector + "_" + stock.industry;

      if ( !isNaN(stock.yearsToMultiple) && stock.yearsToMultiple !== "None") {
        if (!industryYearsToNX[industryType]) {
          industryYearsToNX[industryType] = [];
        }
        industryYearsToNX[industryType].push(stock.yearsToMultiple);
      }

    });

    var industryYearsToNXAvg = {};
    var industryYearsToNXMedian = {};
    for (var industry in industryYearsToNX) {
      var years = industryYearsToNX[industry];
      var sum = years.reduce((a, b) => a + b, 0);
      var avg = sum / years.length;
      var median = calculateMedian(years);
      if (industry === "消費者防衛_食品流通") {
        Logger.log("sum = " + sum + ", years.length: " + years.length);
      }

      industryYearsToNXAvg[industry] = avg.toFixed(2);
      industryYearsToNXMedian[industry] = median.toFixed(2);
    }

    // Industry別の結果をシートに表示
    var industryRow = ceoHoldingRow;
    var industryLabelStartColumn = resultSheet.getLastColumn() + 2;
    var industryChartValStartColunn = industryLabelStartColumn + 1;
    resultSheet.getRange(industryRow, industryLabelStartColumn, 1, 1).setValue("Industry別");
    resultSheet.getRange(industryRow + 1, industryLabelStartColumn, Object.keys(industryCounts).length, 1).setValues(Object.keys(industryCounts).map(function(value) {
      return [value];
    }));
    resultSheet.getRange(industryRow + 1, industryChartValStartColunn, industryDistribution.length, 1).setValues(industryDistribution.map(function(value) {
      return [value];
    }));

    var industryStatsRow = industryRow;
    resultSheet.getRange(industryStatsRow, industryChartValStartColunn, 1, 1).setValue(N_BAGGER_THRESHOLD + "倍になる会社数");
    resultSheet.getRange(industryStatsRow, industryChartValStartColunn + 1, 1, 1).setValue(N_BAGGER_THRESHOLD + "倍まで何年（平均）");
    resultSheet.getRange(industryStatsRow, industryChartValStartColunn + 2, 1, 1).setValue(N_BAGGER_THRESHOLD + "倍まで何年（中央値）");

    resultSheet.getRange(industryStatsRow + 1, industryChartValStartColunn + 1, Object.keys(industryYearsToNXAvg).length, 1).setValues(Object.keys(industryYearsToNXAvg).map(function(value) {
      return [industryYearsToNXAvg[value]];
    }));

    resultSheet.getRange(industryStatsRow + 1, industryChartValStartColunn + 2, Object.keys(industryYearsToNXMedian).length, 1).setValues(Object.keys(industryYearsToNXMedian).map(function(value) {
      return [industryYearsToNXMedian[value]];
    }));

    // 円グラフの作成
    createPieChart(resultSheet, "社長株保有率別", ceoHoldingRow + 1, ceoChartValStartColunn, ceoShareDistribution.length, ceoLabelStartColumn);
    createPieChart(resultSheet, "時価総額別", marketCaptialRow + 1, capitalChartValStartColunn, marketCapDistribution.length, capitalLabelStartColumn);
    createPieChart(resultSheet, "Sector別", sectorRow + 1, sectorChartValStartColunn, sectorDistribution.length, sectorLabelStartColumn);
    createPieChart(resultSheet, "Industry別", industryRow + 1, industryChartValStartColunn, industryDistribution.length, industryLabelStartColumn);
  });
}

function createPieChart(sheet, title, row, column, length, labelColumn) {
  // データを取得
  var labels = sheet.getRange(row, labelColumn, length, 1).getValues().flat();
  var values = sheet.getRange(row, column, length, 1).getValues().flat();
  var avgValues = sheet.getRange(row, column + 1, length, 1).getValues().flat();
  var medianValues = sheet.getRange(row, column + 2, length, 1).getValues().flat();

  // データを多い順にソート
  var data = labels.map((label, index) => [label, parseFloat(values[index]), avgValues[index], medianValues[index]]);
  data.sort((a, b) => b[1] - a[1]);

  // ソートしたデータを新しい範囲に設定
  sheet.getRange(row, labelColumn, length, 1).setValues(data.map(item => [item[0]]));
  sheet.getRange(row, column, length, 1).setValues(data.map(item => [item[1]]));
  sheet.getRange(row, column + 1, length, 1).setValues(data.map(item => [item[2]]));
  sheet.getRange(row, column + 2, length, 1).setValues(data.map(item => [item[3]]));

  // グラフの作成
  var range = sheet.getRange(row, labelColumn, length, 2); // ラベルと値の範囲を選択

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

function calculateMedian(values) {
  values.sort(function(a, b) {
    return a - b;
  });
  var half = Math.floor(values.length / 2);

  if (values.length % 2) {
    return values[half];
  } else {
    return (values[half - 1] + values[half]) / 2.0;
  }
}
