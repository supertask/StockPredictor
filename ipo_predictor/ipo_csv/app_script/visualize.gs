const BIG_INT = 9999999;
const TABLES_ROW = 35;

function processCategoryData(data, categoryKey, nXStocksData, categoryYearsToNX, categoryNXCounts) {
  var categoryCounts = {};
  data.forEach(function(stock) { // 全体の会社数をカウント
    var categoryType = stock[categoryKey];
    
    if (categoryType in categoryCounts) {
      categoryCounts[categoryType]++;
    } else {
      categoryCounts[categoryType] = 1;
    }
  });

  nXStocksData.forEach(function(stock) {
    var categoryType = stock[categoryKey];

    if (!isNaN(stock.yearsToMultiple) && stock.yearsToMultiple !== "None") {
      if (categoryType in categoryNXCounts) {
        categoryNXCounts[categoryType]++;
      } else {
        categoryNXCounts[categoryType] = 1;
      }

      if (!categoryYearsToNX[categoryType]) {
        categoryYearsToNX[categoryType] = [];
      }
      categoryYearsToNX[categoryType].push(stock.yearsToMultiple);
    }
  });

  var categoryYearsToNXAvg = {};
  var categoryYearsToNXMedian = {};
  for (var category in categoryYearsToNX) {
    var years = categoryYearsToNX[category];
    var sum = years.reduce((a, b) => a + b, 0);
    var avg = sum / years.length;
    var median = calculateMedian(years);

    categoryYearsToNXAvg[category] = avg.toFixed(2);
    categoryYearsToNXMedian[category] = median.toFixed(2);
  }

  return {
    categoryCounts: categoryCounts,
    categoryYearsToNXAvg: categoryYearsToNXAvg,
    categoryYearsToNXMedian: categoryYearsToNXMedian
  };
}

function displayCategoryData(resultSheet, categoryData, categoryStatsRow, categoryLabelStartColumn, categoryChartValStartColunn) {
  // categoryDataのキーを取得し、必要なデータをペアにして配列に格納
  var data = Object.keys(categoryData.categoryCounts).map(function(category) {
    var categoryNXCount = categoryData.categoryNXCounts.hasOwnProperty(category) ? categoryData.categoryNXCounts[category] : 0;
    var ratio = (categoryNXCount / categoryData.categoryCounts[category] * 100).toFixed(1);
    return {
      category: category,
      ratio: ratio,
      categoryNXCount: categoryNXCount,
      categoryCount: categoryData.categoryCounts[category],
      avg: categoryData.categoryYearsToNXAvg[category] || BIG_INT,
      median: categoryData.categoryYearsToNXMedian[category] || BIG_INT
    };
  });

  // ratioに基づいてデータをソート
  data.sort(function(a, b) {
    return a.median - b.median; //return b.ratio - a.ratio;
  });

  // ソート済みデータをスプレッドシートに設定
  data.forEach(function(item, index) {
    resultSheet.getRange(categoryStatsRow + 1 + index, categoryLabelStartColumn, 1, 1).setValue(item.category);
    resultSheet.getRange(categoryStatsRow + 1 + index, categoryChartValStartColunn, 1, 1).setValue(item.ratio || "0");
    resultSheet.getRange(categoryStatsRow + 1 + index, categoryChartValStartColunn + 1, 1, 1).setValue(item.categoryNXCount || "0");
    resultSheet.getRange(categoryStatsRow + 1 + index, categoryChartValStartColunn + 2, 1, 1).setValue(item.categoryCount || "0");
    resultSheet.getRange(categoryStatsRow + 1 + index, categoryChartValStartColunn + 3, 1, 1).setValue(item.avg);
    resultSheet.getRange(categoryStatsRow + 1 + index, categoryChartValStartColunn + 4, 1, 1).setValue(item.median);
  });

  // 5倍まで何年（中央値）が書かれていない項目（-）を除外したデータを返す
  return data.filter(function(item) {
    return item.median !== BIG_INT;
  });
}


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
    var ceoHoldingRow = TABLES_ROW;
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
    var sectorYearsToNX = {};
    var sectorNXCounts = {};
    var sectorData = processCategoryData(data, 'sector', nXStocksData, sectorYearsToNX, sectorNXCounts);

    // Sector別の結果をシートに表示
    var sectorStatsRow = ceoHoldingRow;
    var sectorLabelStartColumn = resultSheet.getLastColumn() + 2;
    var sectorChartValStartColunn = sectorLabelStartColumn + 1;
    resultSheet.getRange(sectorStatsRow, sectorChartValStartColunn, 1, 1).setValue(N_BAGGER_THRESHOLD + "倍の会社割合（％）");
    resultSheet.getRange(sectorStatsRow, sectorChartValStartColunn + 1, 1, 1).setValue(N_BAGGER_THRESHOLD + "倍になる会社数");
    resultSheet.getRange(sectorStatsRow, sectorChartValStartColunn + 2, 1, 1).setValue("会社数");
    resultSheet.getRange(sectorStatsRow, sectorChartValStartColunn + 3, 1, 1).setValue(N_BAGGER_THRESHOLD + "倍まで何年（平均）");
    resultSheet.getRange(sectorStatsRow, sectorChartValStartColunn + 4, 1, 1).setValue(N_BAGGER_THRESHOLD + "倍まで何年（中央値）");

    var filteredSectorData = displayCategoryData(resultSheet, { categoryCounts: sectorData.categoryCounts, categoryNXCounts: sectorNXCounts, categoryYearsToNXAvg: sectorData.categoryYearsToNXAvg, categoryYearsToNXMedian: sectorData.categoryYearsToNXMedian }, sectorStatsRow, sectorLabelStartColumn, sectorChartValStartColunn);

    // Industry別の範囲ごとの割合を計算
    var industryYearsToNX = {};
    var industryNXCounts = {};
    var industryData = processCategoryData(data, 'industry', nXStocksData, industryYearsToNX, industryNXCounts);

    // Industry別の結果をシートに表示
    var industryRow = ceoHoldingRow;
    var industryLabelStartColumn = resultSheet.getLastColumn() + 2;
    var industryChartValStartColunn = industryLabelStartColumn + 1;
    resultSheet.getRange(industryRow, industryLabelStartColumn, 1, 1).setValue("Industry別");
    resultSheet.getRange(industryRow + 1, industryLabelStartColumn, Object.keys(industryData.categoryCounts).length, 1).setValues(Object.keys(industryData.categoryCounts).map(function(value) {
      return [value];
    }));

    resultSheet.getRange(industryRow + 1, industryChartValStartColunn, Object.keys(industryData.categoryCounts).length, 1).setValues(Object.keys(industryData.categoryCounts).map(function(key) {
      return [industryData.categoryCounts[key]];
    }));

    var industryStatsRow = industryRow;
    resultSheet.getRange(industryStatsRow, industryChartValStartColunn, 1, 1).setValue(N_BAGGER_THRESHOLD + "倍の会社割合（％）");
    resultSheet.getRange(industryStatsRow, industryChartValStartColunn + 1, 1, 1).setValue(N_BAGGER_THRESHOLD + "倍になる会社数");
    resultSheet.getRange(industryStatsRow, industryChartValStartColunn + 2, 1, 1).setValue("会社数");
    resultSheet.getRange(industryStatsRow, industryChartValStartColunn + 3, 1, 1).setValue(N_BAGGER_THRESHOLD + "倍まで何年（平均）");
    resultSheet.getRange(industryStatsRow, industryChartValStartColunn + 4, 1, 1).setValue(N_BAGGER_THRESHOLD + "倍まで何年（中央値）");

    var filteredIndustryData = displayCategoryData(resultSheet, { categoryCounts: industryData.categoryCounts, categoryNXCounts: industryNXCounts, categoryYearsToNXAvg: industryData.categoryYearsToNXAvg, categoryYearsToNXMedian: industryData.categoryYearsToNXMedian }, industryStatsRow, industryLabelStartColumn, industryChartValStartColunn);

    createPieChart(resultSheet, "社長株保有率別", ceoHoldingRow + 1, ceoLabelStartColumn, ceoShareDistribution.length, 1, ceoLabelStartColumn);
    createPieChart(resultSheet, "時価総額別", marketCaptialRow + 1, capitalLabelStartColumn, marketCapDistribution.length, 15, ceoLabelStartColumn);

    createBarChart(resultSheet, "Sector別", filteredSectorData, sectorStatsRow + 1, sectorLabelStartColumn, 700, 500);
    createBarChart(resultSheet, "Industry別", filteredIndustryData, industryRow + 1, industryLabelStartColumn, 1250, 700);

  });
}

function createBarChart(sheet, title, filteredData, row, labelColumn, width, height) {
  // データの作成
  var labels = filteredData.map(item => [item.category]);
  var medians = filteredData.map(item => [item.median]);
  var ratios = filteredData.map(item => [item.ratio]);

  var startRow = row;
  var startColumn = labelColumn;

  var labelRange = sheet.getRange(startRow, startColumn, labels.length, 1);
  labelRange.setValues(labels);

  var medianRange = sheet.getRange(startRow, startColumn + 1, medians.length, 1);
  medianRange.setValues(medians);

  var ratioRange = sheet.getRange(startRow, startColumn + 2, ratios.length, 1);
  ratioRange.setValues(ratios);

  // グラフの作成
  var chart = sheet.newChart()
    .setChartType(Charts.ChartType.COLUMN) // 縦の棒グラフに変更
    .addRange(labelRange)
    .addRange(medianRange)
    .addRange(ratioRange)
    .setPosition(1, startColumn, 0, 0) // セルの参照を使用して位置を設定
    .setOption('title', title)
    .setOption('width', width) // 幅を設定
    .setOption('height', height) // 高さを設定
    .setOption('legend', {position: 'top', fontSize: 11 })
    .setOption('vAxes', {
      0: { title: 'Years', minValue: 0, maxValue: 7 },  // 左軸（5倍まで何年（中央値））
      1: { title: 'Percentage', minValue: 0, maxValue: 75 } // 右軸（5倍の会社割合（％））
    })
    .setOption('series', {
      0: { targetAxisIndex: 0, color: 'blue', labelInLegend: '5倍まで何年（中央値）' }, // 凡例に名前を設定
      1: { targetAxisIndex: 1, color: 'red', labelInLegend: '5倍の会社割合（％）' }
    })
    .setOption('hAxis', {
      title: title.split(" ")[0],
      slantedText: true,
      slantedTextAngle: 45, // X軸のテキストを45度傾ける
      textStyle: { fontSize: 11 } // テキストのサイズを変更
    })
    //.setOption('hAxis', { title: title.split(" ")[0] }) // X軸のタイトルを設定
    .build();

  sheet.insertChart(chart);
}

function createPieChart(sheet, title, row, column, length, visualizeRow, visualizeColumn) {
  // グラフの作成
  var range = sheet.getRange(row, column, length, 2); // ラベルと値の範囲を選択

  var chart = sheet.newChart()
    .setChartType(Charts.ChartType.PIE)
    .addRange(range)
    .setPosition(visualizeRow, visualizeColumn, 0, 0) // セルの参照を使用して位置を設定
    .setOption('title', title)
    .setOption('width', 500) // 幅を設定
    .setOption('height', 270) // 高さを設定
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
