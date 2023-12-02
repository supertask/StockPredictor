SELECT 
	ue.code, ue.date, ue.adj_max_stock_rise, ue.days_to_adj_max_stock_rise, ue.max_stock_rise, ue.days_to_max_stock_rise, 
	td.title, td.url, ue.rise_tags
FROM UpwardEvaluation ue
JOIN TimelyDisclosure td ON ue.code = td.code AND ue.date = td.date
LEFT JOIN TimelyDisclosureTags tg ON td.date = tg.date AND td.time = tg.time AND td.code = tg.code AND td.title = tg.title

WHERE ue.code = '35630'

GROUP BY ue.code, ue.date, ue.adj_max_stock_rise, ue.days_to_adj_max_stock_rise, ue.max_stock_rise, ue.days_to_max_stock_rise, 
td.title, td.url 
ORDER BY ue.adj_max_stock_rise DESC