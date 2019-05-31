#!/usr/bin/env python
# coding: utf-8

# Exercise 1. How many distinct dates are there in the saledate column of the transaction table for each month/year combination in the database?

# In[ ]:


SELECT COUNT(DISTINCT saledate) AS numdates, 
EXTRACT(MONTH from saledate) AS month_num,
EXTRACT(YEAR from saledate) AS year_num
FROM trnsact
GROUP BY month_num, year_num
ORDER BY numdates DESC;


# Exercise 2. Use a CASE statement within an aggregate function to determine which sku had the greatest total sales during the combined summer months of June, July, and August.

# In[ ]:


SELECT sku, 
SUM(CASE WHEN EXTRACT(MONTH from saledate) = 6 THEN amt END) AS June_sale,
SUM(CASE WHEN EXTRACT(MONTH from saledate) = 7 THEN amt END) AS July_sale,
SUM(CASE WHEN EXTRACT(MONTH from saledate) = 8 THEN amt END) AS August_sale,
June_sale + July_sale + August_sale AS total_sale
FROM trnsact 
WHERE stype = 'P'
GROUP BY sku
ORDER BY total_sale DESC;


# Exercise 3. How many distinct dates are there in the saledate column of the transaction table for each month/year/store combination in the database? Sort your results by the number of days per combination in ascending order.

# In[ ]:


SELECT COUNT(DISTINCT saledate) AS numdates,
EXTRACT(month from saledate) AS month_num,
EXTRACT(year from saledate) AS year_num,
store
FROM trnsact
GROUP BY 2,3,4
ORDER BY numdates ASC;


# Exercise 4. What is the average daily revenue for each store/month/year combination in the database? Calculate this by dividing the total revenue for a group by the number of sales days available in the transaction table for that group.

# In[ ]:


SELECT 
SUM(amt)/COUNT(DISTINCT saledate) AS daily_revenue,
store,
EXTRACT(month from saledate) AS month_num,
EXTRACT(year from saledate) AS year_num
FROM trnsact
WHERE stype = 'P'
GROUP BY 2,3,4
ORDER BY daily_revenue DESC;


# In[ ]:


SELECT store, month_num, year_num, total_revenue, saledates, daily_revenue
FROM (SELECT 
 store,
 EXTRACT(month from saledate) AS month_num,
 EXTRACT(year from saledate) AS year_num,
 SUM(amt) AS total_revenue,
 COUNT(DISTINCT saledate) AS saledates,
 total_revenue / saledates AS daily_revenue,
 (CASE WHEN month_num = 8 AND year_num = 2005 THEN 'cannot' ELSE 'can' END) AS can_cannot
 FROM trnsact
 WHERE stype = 'P' AND can_cannot = 'can'
 GROUP BY 1,2,3
 HAVING saledates >= 20) AS sub;


# Exercise 5. What is the average daily revenue brought in by Dillard’s stores in areas of high, medium, or low levels of high school education?

# In[ ]:


SELECT sub1.education, 
SUM(sub2.total_revenue) AS total,
SUM(sub2.saledates) AS dates,
total / dates AS daily_revenue
FROM (SELECT 
store,
(CASE 
WHEN msa_high >= 50 AND msa_high <= 60 THEN 'low'
WHEN msa_high >= 60.01 AND msa_high <= 70 THEN 'medium'
WHEN msa_high > 70 THEN 'high'
END) AS education
FROM store_msa) AS sub1
JOIN 
(SELECT 
 store,
 EXTRACT(month from saledate) AS month_num,
 EXTRACT(year from saledate) AS year_num,
 SUM(amt) AS total_revenue,
 COUNT(DISTINCT saledate) AS saledates,
 (CASE WHEN month_num = 8 AND year_num = 2005 THEN 'cannot' ELSE 'can' END) AS can_cannot
 FROM trnsact
 WHERE stype = 'P' AND can_cannot = 'can'
 GROUP BY 1,2,3
 HAVING saledates >= 20) AS sub2
ON sub1.store = sub2.store
GROUP BY sub1.education;


# 
# Exercise 6. Compare the average daily revenues of the stores with the highest median msa_income and the lowest median msa_income. In what city and state were these stores, and which store had a higher average daily revenue?

# In[ ]:


SELECT s.msa_income,
s.city,
s.state, 
AVG(daily_revenue)
FROM store_msa s
JOIN 
(SELECT 
 store,
 EXTRACT(month from saledate) AS month_num,
 EXTRACT(year from saledate) AS year_num,
 SUM(amt) AS total_revenue,
 COUNT(DISTINCT saledate) AS saledates,
 total_revenue / saledates AS daily_revenue,
 (CASE WHEN month_num = 8 AND year_num = 2005 THEN 'cannot' ELSE 'can' END) AS can_cannot
 FROM trnsact
 WHERE stype = 'P' AND can_cannot = 'can'
 GROUP BY 1,2,3
 HAVING saledates >= 20) AS sub
ON s.store = sub.store
WHERE s.msa_income IN ((SELECT MIN(msa_income) FROM store_msa), 
                       (SELECT MAX(msa_income) FROM store_msa))
GROUP BY s.msa_income, s.city, s.state;


# Exercise 7: What is the brand of the sku with the greatest standard deviation in sprice? Only examine skus that have been part of over 100 transactions.

# In[ ]:


SELECT s.brand, t.stddev_sprice, t.sku
FROM (SELECT sku, STDDEV_SAMP(sprice) AS stddev_sprice
  FROM trnsact
  WHERE stype = 'P'
  GROUP BY sku
  HAVING COUNT(*) > 100) AS t
JOIN skuinfo s ON t.sku = s.sku
ORDER BY t.stddev_sprice DESC;


# Exercise 8: Examine all the transactions for the sku with the greatest standard deviation in sprice, but only consider skus that are part of more than 100 transactions.

# In[ ]:


SELECT *
FROM trnsact
WHERE sku = (SELECT sub.sku FROM(SELECT top 1 s.brand, t.stddev_sprice, t.sku
  FROM (SELECT sku, STDDEV_SAMP(sprice) AS stddev_sprice
  FROM trnsact
  WHERE stype = 'P'
  GROUP BY sku
  HAVING COUNT(*) > 100) AS t
  JOIN skuinfo s ON t.sku = s.sku
  ORDER BY t.stddev_sprice DESC) AS sub);


# 
# Exercise 9: What was the average daily revenue Dillard’s brought in during each month of the year?

# In[ ]:


SELECT month_num, AVG(sub.daily_revenue) AS avg_daily_revenue
FROM (SELECT 
 store,
 EXTRACT(month from saledate) AS month_num,
 EXTRACT(year from saledate) AS year_num,
 SUM(amt) AS total_revenue,
 COUNT(DISTINCT saledate) AS saledates,
 total_revenue / saledates AS daily_revenue,
 (CASE WHEN month_num = 8 AND year_num = 2005 THEN 'cannot' ELSE 'can' END) AS can_cannot
 FROM trnsact
 WHERE stype = 'P' AND can_cannot = 'can'
 GROUP BY 1, 2, 3
 HAVING saledates >= 20) AS sub
GROUP BY month_num
ORDER BY 2 DESC; 


# 
# Exercise 10: Which department, in which city and state of what store, had the greatest % increase in average daily sales revenue from November to December?

# In[ ]:


SELECT sub2.deptdesc, sub2.city, sub2.state, sub2.store, sub2.per_increase
FROM (SELECT
  b.city,
  b.state,
  c.dept,
  c.deptdesc,
  sub.store,
  SUM(CASE WHEN EXTRACT(month from sub.saledate) = 11 THEN sub.amt END) AS Nov_sale,
  SUM(CASE WHEN EXTRACT(month from sub.saledate) = 12 THEN sub.amt END) AS Dec_sale,
  COUNT(DISTINCT (CASE WHEN sub.month_num = 11 THEN sub.saledate END)) AS Nov_dates,
  COUNT(DISTINCT (CASE WHEN sub.month_num = 12 THEN sub.saledate END)) AS Dec_dates,
  Nov_sale / Nov_dates AS Nov_daily_rev,
  Dec_sale / Dec_dates AS Dec_daily_rev,
  (Dec_daily_rev / Nov_daily_rev - 1) * 100 AS per_increase
  FROM (SELECT t.store, t.saledate, t.amt, a.dept,
        EXTRACT(month from t.saledate) AS month_num,
        EXTRACT(year from t.saledate) AS year_num,
        (CASE WHEN month_num = 8 AND year_num = 2005 THEN 'cannot' ELSE 'can' END) AS can_cannot
        FROM trnsact t JOIN skuinfo a ON t.sku = a.sku
        WHERE stype = 'P' AND can_cannot = 'can') AS sub
  JOIN strinfo b ON sub.store = b.store
  JOIN deptinfo c ON sub.dept = c.dept
  GROUP BY 1,2,3,4,5
  HAVING Nov_dates>=20 AND Dec_dates>=20) AS sub2
ORDER BY sub2.per_increase DESC
("")


# Exercise 11: What is the city and state of the store that had the greatest decrease in average daily revenue from August to September?

# In[ ]:


SELECT sub2.city, sub2.state, sub2.store, sub2.per_decrease
FROM (SELECT
  b.city,
  b.state,
  sub.store,
  SUM(CASE WHEN EXTRACT(month from sub.saledate) = 8 THEN sub.amt END) AS Aug_sale,
  SUM(CASE WHEN EXTRACT(month from sub.saledate) = 9 THEN sub.amt END) AS Sep_sale,
  COUNT(DISTINCT (CASE WHEN sub.month_num = 8 THEN sub.saledate END)) AS Aug_dates,
  COUNT(DISTINCT (CASE WHEN sub.month_num = 9 THEN sub.saledate END)) AS Sep_dates,
  Aug_sale / Aug_dates AS Aug_daily_rev,
  Sep_sale / Sep_dates AS Sep_daily_rev,
  Aug_daily_rev - Sep_daily_rev AS per_decrease
  FROM (SELECT t.store, t.saledate, t.amt, a.dept,
        EXTRACT(month from t.saledate) AS month_num,
        EXTRACT(year from t.saledate) AS year_num,
        (CASE WHEN month_num = 8 AND year_num = 2005 THEN 'cannot' ELSE 'can' END) AS can_cannot
        FROM trnsact t JOIN skuinfo a ON t.sku = a.sku
        WHERE stype = 'P' AND can_cannot = 'can') AS sub
  JOIN strinfo b ON sub.store = b.store
  GROUP BY 1,2,3
  HAVING Aug_dates>=20 AND Sep_dates>=20) AS sub2
ORDER BY sub2.per_decrease DESC
("")


# Exercise 12: Determine the month of maximum total revenue for each store. Count the number of stores whose month of maximum total revenue was in each of the twelve months. Then determine the month of maximum average daily revenue. Count the number of stores whose month of maximum average daily revenue was in each of the twelve months. How do they compare?

# In[ ]:


SELECT 
sub.month_num,
COUNT(CASE WHEN sub.row_daily_rev = 12 THEN sub.store END) AS daily_rev_num,
COUNT(CASE WHEN sub.row_total_rev = 12 THEN sub.store END) AS total_rev_num
FROM (SELECT store, 
  EXTRACT(month from saledate) AS month_num, 
  EXTRACT(year from saledate) AS year_num,
  sum(amt) AS total_rev,
  COUNT(DISTINCT saledate) AS saledates,
  total_rev / saledates AS daily_rev,
  CASE WHEN month_num = 8 AND year_num = 2005 THEN 'cannot' ELSE 'can' END AS canornot,
  ROW_NUMBER() OVER(PARTITION BY store ORDER BY total_rev DESC) AS row_total_rev,
  ROW_NUMBER() OVER(PARTITION BY store ORDER BY daily_rev DESC) AS row_daily_rev
  WHERE stype = 'P' AND canornot = 'can'
  FROM trnsact
  GROUP BY store, month_num, year_num
  HAVING saledates >= 20) AS sub
GROUP BY sub.month_num
ORDER BY total_rev_num DESC;

