import sqlite3
import pandas as pd

df = pd.read_csv("data/german_credit.csv")
# "default" is a reserved word in SQL, so rename the column
df = df.rename(columns={"default": "is_default"})

conn = sqlite3.connect("data/loans.db")        # creates a small database file
df.to_sql("loans", conn, if_exists="replace", index=False)  # one table: loans

def run(title, sql):
    print("\n" + title)
    print(pd.read_sql_query(sql, conn).to_string(index=False))

run("1. Overall", """
SELECT COUNT(*) AS loans, ROUND(AVG(is_default), 3) AS default_rate
FROM loans""")

run("2. Default rate by purpose (groups with 20+ loans)", """
SELECT purpose, COUNT(*) AS loans, ROUND(AVG(is_default), 3) AS default_rate
FROM loans
GROUP BY purpose
HAVING COUNT(*) >= 20
ORDER BY default_rate DESC""")

run("3. Default rate by checking account status", """
SELECT checking_status, COUNT(*) AS loans, ROUND(AVG(is_default), 3) AS default_rate
FROM loans
GROUP BY checking_status
ORDER BY default_rate DESC""")

run("4. Default rate by age band", """
SELECT CASE WHEN age < 25 THEN '<25'
            WHEN age < 35 THEN '25-34'
            WHEN age < 50 THEN '35-49'
            ELSE '50+' END AS age_band,
       COUNT(*) AS loans, ROUND(AVG(is_default), 3) AS default_rate
FROM loans
GROUP BY age_band
ORDER BY age_band""")

run("5. Average loan size: defaulters (1) vs others (0)", """
SELECT is_default, ROUND(AVG(credit_amount)) AS avg_amount, ROUND(AVG(duration), 1) AS avg_months
FROM loans
GROUP BY is_default""")

conn.close()