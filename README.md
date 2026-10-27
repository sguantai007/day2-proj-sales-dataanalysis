# Day 2 – Sales Analytics Without Pandas

Analyses the September 2026 electronics sales file (`electronics_sales.csv`) using only the Python standard library then the results are rechecked using pandas. 

## Approach

1. **Read** – `read_sales` loads the CSV with `csv.DictReader`. Every value arrives as text, and the row and column counts are printed.
2. **Clean** – `parse_number` turns a messy text value into a number or `None`.  `convert_rows` splits the rows into `clean_rows` (with `revenue = quantity × unit price`) and `skipped_rows` (each with a `reason`).
3. **Analyse** – `total_revenue`, `revenue_by` (a plain dict, used for product, store and payment method), `top_n` (sorted with a key function), `high_value` (a list comprehension), a dict comprehension for high-value sales per store, and hand-written `mean`, `median` and `minimum_maximum` (the task is to tackle the questions without the `statistics` module).
4. **Verify** – `verify_with_pandas` re-reads the CSV, applies the same cleaning rules with pandas, and compares the total, revenue by product, top 3, and mean/median. It prints MATCH or MISMATCH for each and returns the results.
5. **Report** – the results are printed to the screen and the main sections are saved to `output/sales_report.txt`.


## Rules for bad numeric values

Only `quantity` and `unit_price_kes` are numeric. The task presented was : **repair a value only when its meaning is unambiguous; skip the row when information is missing**. 

| Rule | Example | Result |
|---|---|---|
| Surrounding spaces are removed | any | – |
| Thousands commas are removed | S-3017 unit price `38,999` | 38999 |
| The currency label `KES` is removed | S-3029 unit price `KES 18999` | 18999 |
| The word `two` becomes 2 (both upper and lowercase) | S-3006 quantity `two` | 2 |

### Skipped (row is excluded, with a reason)

| Rule | Reason recorded | Example | Assumption|
|---|---|---|---|
| Quantity is blank, `N/A` or not a number | Missing or invalid quantity | S-3035 (blank) | We cannot guess a quantity value as it would affect the revenue calculates |
| Quantity is zero, negative, or not a whole number | Quantity must be positive | none in this file | We cannot logically have negative or half of these items |
| Unit price is blank, `N/A` or not a number | Missing or invalid unit price | S-3030 (`N/A`), S-3039 (blank) | We cannot guess the price of an item unless its provided |
| Unit price is zero or negative | Unit price must be positive | none in this file | Price cannot logically be 0 or negative |
Result: **50 rows read, 47 used, 3 skipped** (S-3030, S-3035, S-3039). The three repaired rows (S-3006, S-3017, S-3029) stay in every total.

The pandas check applies these same rules, so both sides use the same set of 47 rows.

## Tie-breaking

`top_n` sorts with the key `(-revenue, name)`: highest revenue first, and products with equal revenue in alphabetical order. The ranking is therefore the same on every run. There are no ties in this data.

## Assumptions

- **Revenue** is `quantity × unit_price_kes` for each row. No discounts, tax or returns are applied.
- **Currency** is KES throughout, as the column name says.
- **Each row is one transaction.** I checked that no `sale_id` appears twice, so there is no duplicate handling.
- **Skipped rows are excluded from every figure**: totals, groupings, top 3, high-value list and statistics.
- **No values are filled in** from other rows or from averages.
- **Dates are shown as written and not parsed.** All fall between 2026-09-01 and 2026-09-30.
- **High-value** means a transaction whose revenue (quantity × price, not the unit price alone) is **at or above** KES 50,000.

## Results

- Total revenue: **KES 1,317,210.00**
- Top 3 products: HP 15 Laptop (389,994.00), Hisense 43in Smart TV (272,993.00), Lenovo Tab M10 (199,992.00)
- High-value transactions (equal or more than KES 50,000): 5 (Kisumu Mega Plaza 2; Nairobi CBD, Nakuru Westside and Westgate 1 each)
- Per-transaction revenue: mean 28,025.74, median 10,998.00, min 1,499.00, max 259,996.00

As in most cases, the median is a better metric to consider as the mean has been skewed by a few large sales.

## pandas verification

All four checks (total revenue, revenue by product, top 3, mean/median) print **MATCH**, so there is no mismatch to explain.

## Output

`output/sales_report.txt` contains: revenue by product, the top 3 products, the high-value transactions (id, date, store, product, amount), the transaction revenue statistics, and the pandas verification results.