import streamlit as st


st.header('Export Database')

st.subheader(":orange[10. Export your SQL Database and analyse it with your favourite visualization tool. If you are planning to actually use this application, this is not required since the DB is already on you computer.]")

with open("my_finance.db", "rb") as file:
    btn = st.download_button(
        label="Download SQL",
        data=file,
        file_name='my_finance.db',
    )

st.subheader(":orange[To get help to connect your data to PowerBI, you can visit this page.]")
st.page_link('https://apps.provingground.io/docs/tracer-v1-0-documentation/tracer-power-bi-workflow/how-to-use-sqlite-as-a-power-bi-data-source/', label='How to Connect My SQL', icon="🌎")


st.subheader(":orange[Here you can try an example version of the Looker Studio Report that I actually use, and maybe get some ideas to crunch your data]")
st.page_link('https://lookerstudio.google.com/reporting/f5630023-10c5-4b5e-9904-9049d79ea7db', label='An example report for your Data', icon="🌎")
st.image('frontend/app_assets/report.png', caption='Monthly Expendatures Page')

with st.expander('See the SQL code'):
    st.subheader('This SQL code transforms the f_assets table to the format used in the Looker Studio Report')

    st.code('''WITH original_table AS (
  SELECT  
    KeyDate AS date,
    category,
    value,
    True AS include_house 
  FROM f_assets
),

capital_market_value AS (
  SELECT
  KeyDate AS date,
  CASE
    WHEN category IN ('CAPITAL-ASSETS-PURCHASE-PRICE', 'UNREALIZED-CAPITAL-GAINS') THEN 'CAPITAL-ASSETS-VALUE'
  END AS category,
  SUM(value) as value,
  True AS include_house 
  FROM f_assets
  WHERE category IN ('CAPITAL-ASSETS-PURCHASE-PRICE', 'UNREALIZED-CAPITAL-GAINS')
  GROUP BY 1,2
),

total_values AS (
  SELECT
  KeyDate AS date,
  CASE
    WHEN category IN ('APARTMENT', 'CAPITAL-ASSETS-PURCHASE-PRICE', 'UNREALIZED-CAPITAL-GAINS', 'CASH', 'OTHER-ASSETS') THEN 'TOTAL-ASSETS'
    WHEN category IN ('MORTGAGE', 'OTHER-LOANS', 'STUDENT-LOAN') THEN 'TOTAL-LIABILITIES'
  END AS category,
  SUM(value) as value,
  True AS include_house 
  FROM f_assets
  WHERE category IN ('APARTMENT', 'CAPITAL-ASSETS-PURCHASE-PRICE', 'UNREALIZED-CAPITAL-GAINS', 'CASH', 'OTHER-ASSETS', 'MORTGAGE', 'OTHER-LOANS', 'STUDENT-LOAN')
  GROUP BY 1,2
),
net_value AS (
  SELECT
  date,
  CASE 
    WHEN category IN ('TOTAL-ASSETS', 'TOTAL-LIABILITIES') THEN 'NET-ASSETS'
  END AS category,
  SUM(value) AS value,
  True AS include_house 
  FROM total_values
  GROUP BY 1,2
),
total_values_minus_net_value AS (
  SELECT
  l.date,
  'TOTAL-ASSETS-MINUS-NET-ASSETS' AS category,
  l.value - r.value AS value,
  True AS include_house 
  FROM total_values as l
  INNER JOIN net_value AS r ON l.date = r.date
  WHERE l.category = 'TOTAL-ASSETS'
  AND r.category IS NOT NULL
),


original_table_wo_ap AS (
  SELECT  
    KeyDate AS date,
    category,
    value,
    False AS include_house 
  FROM f_assets
  WHERE category NOT IN ('APARTMENT', 'MORTGAGE')
),
capital_market_value_wo_ap AS (
  SELECT
  KeyDate AS date,
  CASE
    WHEN category IN ('CAPITAL-ASSETS-PURCHASE-PRICE', 'UNREALIZED-CAPITAL-GAINS') THEN 'CAPITAL-ASSETS-VALUE'
  END AS category,
  SUM(value) as value,
  False AS include_house 
  FROM f_assets
  WHERE category IN ('CAPITAL-ASSETS-PURCHASE-PRICE', 'UNREALIZED-CAPITAL-GAINS')
  GROUP BY 1,2
),
_total_values_wo_ap AS (
  SELECT
  KeyDate AS date,
  CASE
    WHEN category IN ('CAPITAL-ASSETS-PURCHASE-PRICE', 'UNREALIZED-CAPITAL-GAINS', 'CASH', 'OTHER-ASSETS') THEN 'TOTAL-ASSETS'
    WHEN category IN ('OTHER-LOANS', 'STUDENT-LOAN') THEN 'TOTAL-LIABILITIES'
    WHEN category IN ('APARTMENT', 'MORTGAGE') THEN 'APARTMENT-NET-VALUE'
  END AS category,
  SUM(value) as value,
  False AS include_house 
  FROM f_assets
  WHERE category IN ('CAPITAL-ASSETS-PURCHASE-PRICE', 'UNREALIZED-CAPITAL-GAINS', 'CASH', 'OTHER-ASSETS', 'OTHER-LOANS', 'STUDENT-LOAN', 'APARTMENT', 'MORTGAGE')
  GROUP BY 1,2
),
total_values_wo_ap AS (
  SELECT
  date,
  CASE
    WHEN category IN ('APARTMENT-NET-VALUE', 'TOTAL-ASSETS') THEN 'TOTAL-ASSETS'
    WHEN category IN ('TOTAL-LIABILITIES') THEN 'TOTAL-LIABILITIES'
  END AS category,
  SUM(value) as value,
  False AS include_house 
  FROM _total_values_wo_ap
  GROUP BY 1,2
),
net_value_wo_ap AS (
  SELECT
  date,
  CASE 
    WHEN category IN ('TOTAL-ASSETS', 'TOTAL-LIABILITIES') THEN 'NET-ASSETS'
  END AS category,
  SUM(value) AS value,
  False AS include_house 
  FROM total_values_wo_ap
  GROUP BY 1,2
),
total_values_minus_net_value_wo_ap AS (
  SELECT
  l.date,
  'TOTAL-ASSETS-MINUS-NET-ASSETS' AS category,
  l.value - r.value AS value,
  False AS include_house 
  FROM total_values_wo_ap as l
  left join net_value_wo_ap as r on l.date= r.date
  WHERE l.category = 'TOTAL-ASSETS'
  AND r.category IS NOT NULL
),


concating AS (

SELECT
date, category, value, include_house FROM original_table WHERE category IS NOT NULL
UNION ALL
SELECT
date, category, value, include_house FROM capital_market_value WHERE category IS NOT NULL
UNION ALL
SELECT
date, category, value, include_house FROM total_values WHERE category IS NOT NULL
UNION ALL
SELECT
date, category, value, include_house FROM net_value WHERE category IS NOT NULL
UNION ALL
SELECT
date, category, value, include_house FROM total_values_minus_net_value WHERE category IS NOT NULL

UNION ALL
SELECT
date, category, value, include_house FROM original_table_wo_ap WHERE category IS NOT NULL
UNION ALL
SELECT
date, category, value, include_house FROM capital_market_value_wo_ap WHERE category IS NOT NULL
UNION ALL
SELECT
date, category, value, include_house FROM total_values_wo_ap WHERE category IS NOT NULL
UNION ALL
SELECT
date, category, value, include_house FROM net_value_wo_ap WHERE category IS NOT NULL
UNION ALL
SELECT
date, category, value, include_house FROM total_values_minus_net_value_wo_ap WHERE category IS NOT NULL
UNION ALL
SELECT
date, category, value, include_house FROM _total_values_wo_ap WHERE category = 'APARTMENT-NET-VALUE'
)


SELECT
date,
category,
value,
include_house,
CASE 
  WHEN (value > 0 AND LAG(value) OVER (PARTITION BY category, include_house ORDER BY date) > 0)
    OR (value < 0 AND LAG(value) OVER (PARTITION BY category, include_house ORDER BY date) < 0)
    THEN value / LAG(value) OVER (PARTITION BY category, include_house ORDER BY date)
  ELSE 1
END as diff_to_previous,
CASE 
  WHEN (value > 0 AND LAG(value) OVER (PARTITION BY category, include_house ORDER BY date) > 0)
    OR (value < 0 AND LAG(value) OVER (PARTITION BY category, include_house ORDER BY date) < 0)
    THEN value - LAG(value) OVER (PARTITION BY category, include_house ORDER BY date)
  ELSE 0
END as diff_delta_to_previous,
FROM concating
''', language='sql')