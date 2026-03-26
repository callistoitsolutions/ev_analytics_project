SELECT COUNT(*) AS total_vehicles FROM ev_data;

SELECT SUM(RevenueINR) AS total_revenue FROM ev_data;

SELECT SUM(ProfitINR) AS total_profit FROM ev_data;

SELECT Segment, SUM(RevenueINR) AS revenue
FROM ev_data
GROUP BY Segment;
