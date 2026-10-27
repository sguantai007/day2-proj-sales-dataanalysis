"""
Day 2 - Sales Analytics Without Pandas
Squad Python Specialization - Data Science, AI & Analytics

Tasks 1-7 use only the standard library. pandas is allowed in task 8, to check your work.
"""
import csv
from pathlib import Path
import pandas as pd

DATA_PATH = Path("data") / "electronics_sales.csv"


def read_sales(path: Path = DATA_PATH) -> list[dict[str, str]]:
    """Read the CSV with the csv module and return the raw rows."""
    with path.open('r', newline='') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        print(f'Rows read: {len(rows)}')
        print(f'Column names: {reader.fieldnames}')

    return rows


def parse_number(value: str) -> float | None:
    """Convert a messy numeric string to a float, or return None if it cannot be trusted."""
    if value is None:
        return None

    value = value.strip()

    if value == '' or value.upper() == 'N/A':
        return None

    if value.lower() == 'two':
        return 2.0

    value = value.replace(',', '')
    value = value.replace('KES', '').strip()

    try:
        return float(value)
    except ValueError:
        return None


def convert_rows(rows: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    """Return (clean_rows, skipped_rows). Clean rows have numeric quantity, unit price and revenue."""
    clean_rows = []
    skipped_rows = []

    for row in rows:
        quantity = parse_number(row['quantity'])
        unit_price = parse_number(row['unit_price_kes'])

        if quantity is None:
            row['reason'] = 'Missing or invalid quantity'
            skipped_rows.append(row)
            continue
        if quantity<= 0 or not quantity.is_integer():
            row['reason'] = 'Quantity must be positive'
            skipped_rows.append(row)
            continue
        if unit_price is None:
            row['reason'] = 'Missing or invalid unit price'
            skipped_rows.append(row)
            continue
        if unit_price <=0:
            row['reason'] = 'Unit price must be positive'
            skipped_rows.append(row)
            continue

        row['quantity'] = int(quantity)
        row['unit_price_kes'] = unit_price
        row['revenue'] = row['quantity'] * row['unit_price_kes']

        clean_rows.append(row)

    return clean_rows, skipped_rows


def total_revenue(rows: list[dict]) -> float:
    '''Calculating from cleaned sales row'''
    total = 0

    for row in rows:
        total += row['revenue']
    return total
    


def revenue_by(rows: list[dict], field: str) -> dict[str, float]:
    """Total revenue grouped by any column (product, store, payment_method...)."""
    totals = {}

    for row in rows:
        name = row[field]
        revenue = row['revenue']

        if name in totals:
            totals[name] += revenue
        else:
            totals[name] = revenue
    return totals


def top_n(totals: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    """Return the n highest (key, value) pairs, highest first."""
    sorted_totals = sorted(
        totals.items(),
        key=lambda item: (-item[1], item[0])
    )
    return sorted_totals[:n]


def high_value(rows: list[dict], threshold: float) -> list[dict]:
    """Transactions whose revenue is at or above threshold (use a comprehension)."""
    return [row for row in rows if row['revenue'] >= threshold]


# Reusable statistics - implement these yourself, no statistics module.
def mean(values: list[float]) -> float:
    '''Finding the average'''
    if len(values) == 0:
        raise ValueError('Cannot calculate mean of an empty list')

    return sum(values) / len(values)


def median(values: list[float]) -> float:
    '''Finding the median'''
    if len(values) == 0:
        raise ValueError('Cannot calculate median of an empty list')

    sorted_values = sorted(values)
    middle = len(sorted_values) // 2

    if len(sorted_values) % 2 == 1:
        return sorted_values[middle]
    return (sorted_values[middle -1] + sorted_values[middle]) / 2



def minimum_maximum(values: list[float]) -> tuple[float, float]:
    '''find smallest and largest values without usin max() or min()'''
    if len(values) == 0:
        raise ValueError('Cannot find min or max of an empty list')

    smallest = values[0]
    largest = values[0]

    for value in values:
        if value < smallest:
            smallest = value

        if value > largest:
            largest = value

    return smallest, largest


def verify_with_pandas(path: Path, my_results: dict) -> dict:
    """Recompute the headline numbers with pandas and print whether each one matches."""
    df = pd.read_csv(path, dtype=str)

    def pandas_parse_number(value):
        if pd.isna(value):
            return None

        value = str(value).strip()

        if value == '' or value.upper() == 'N/A':
            return None
        if value.lower() == 'two':
            return 2.0

        value = value.replace(',', '')
        value = value.replace('KES','').strip()

        try:
            return float(value)
        except ValueError:
            return None

    df['quantity'] = df['quantity'].apply(pandas_parse_number)
    df['unit_price_kes'] = df['unit_price_kes'].apply(pandas_parse_number)

    df = df.dropna(subset=['quantity', 'unit_price_kes'])

    df = df[
        (df['quantity'] > 0)
        & (df['quantity'] % 1 == 0)
        & (df['unit_price_kes'] > 0)
    ].copy()

    df['revenue'] = df['quantity'] * df['unit_price_kes']

    verification = {}

    pandas_total = df['revenue'].sum()

    print(f'Pandas total revenue: KES {pandas_total:,.2f}')

    if 'total_revenue' in my_results:
        python_total = my_results['total_revenue']

        if abs(python_total - pandas_total) < 0.01:
            print('MATCH: Same total')
            verification['Total revenue'] = 'MATCH'
        else:
            print(f'MISMATCH. Python total: KES {python_total:,.2f}')
            verification['Total revenue'] = f'MISMATCH (Python: {python_total:,.2}, Pandas: {pandas_total:,.2})'


    if 'product_totals' in my_results:
        python_products = my_results['product_totals']
        pandas_products = df.groupby('product')['revenue'].sum().to_dict()
 
        same_products = python_products.keys() == pandas_products.keys() and all(
            abs(python_products[name] - pandas_products[name]) < 0.01
            for name in python_products
        )
 
        if same_products:
            print('MATCH: Same revenue by product')
            verification['Revenue by product'] = 'MATCH'
        else:
            print(f'MISMATCH. Python: {python_products}, pandas: {pandas_products}')
            verification['Revenue by product'] = f'MISMATCH (Python: {python_products}, pandas: {pandas_products})'

            
    if 'top_3' in my_results:
        python_top_3 = my_results['top_3']
        pandas_totals = df.groupby('product')['revenue'].sum().reset_index()
        pandas_totals = pandas_totals.sort_values(
            ['revenue', 'product'], ascending=[False, True]
        ).head(3)
        pandas_top_3 = list(zip(pandas_totals['product'], pandas_totals['revenue']))
 
        same_top_3 = len(python_top_3) == len(pandas_top_3) and all(
            py[0] == pd_[0] and abs(py[1] - pd_[1]) < 0.01
            for py, pd_ in zip(python_top_3, pandas_top_3)
        )
 
        if same_top_3:
            print('MATCH: Same top 3 products')
            verification['Top 3'] = 'MATCH'
        else:
            print(f'MISMATCH. Python: {python_top_3}, pandas: {pandas_top_3}')
            verification['Top 3'] = f'MISMATCH. (Python: {python_top_3}, pandas: {pandas_top_3})'
 
    if 'mean_median' in my_results:
        python_mean, python_median = my_results['mean_median']
        pandas_mean = df['revenue'].mean()
        pandas_median = df['revenue'].median()
 
        if abs(python_mean - pandas_mean) < 0.01 and abs(python_median - pandas_median) < 0.01:
            print('MATCH: Same mean and median')
            verification['Mean / median'] = 'MATCH'
        else:
            print(
                f'MISMATCH. Python: ({python_mean:,.2f}, {python_median:,.2f}), '
                f'pandas: ({pandas_mean:,.2f}, {pandas_median:,.2f})'
            )
            verification['Mean / median'] = (
                f'MISMATCH. Python: ({python_mean:,.2f}, {python_median:,.2f}), '
                f'pandas: ({pandas_mean:,.2f}, {pandas_median:,.2f})'
            )

    return verification
 



if __name__ == "__main__":
    sales = read_sales()

    clean_sales, skipped_sales =convert_rows(sales)

    revenue = total_revenue(clean_sales)
    print(f'Total revenue: KES {revenue:,.2f}')
    print(f'Row used: {len(clean_sales)}')
    print(f'Rows skipped: {len(skipped_sales)}')

    product_totals = revenue_by(clean_sales, 'product')

    print('Revenue by products:')
    for product, revenue in sorted(
        product_totals.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(f'{product}: KES {revenue:,.2f}')

    store_totals = revenue_by(clean_sales, 'store')

    print('Revenue by store:')
    for store, revenue in sorted(
        store_totals.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(f'{store} KES {revenue:,.2f}')

    payment_totals = revenue_by(clean_sales, 'payment_method')

    print('Revenue by payment method:')
    for payment, revenue in sorted(
        payment_totals.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(f'{payment} KES {revenue:,.2f}')

    top_products = top_n(product_totals, 3)

    print('Top 3 products by revenue:')
    for product, revenue in top_products:
        print(f'{product}: KES {revenue:,.2f}')

    high_sales = high_value(clean_sales, 50000)

    print('High value sales (KES 50,000 or more):')
    for row in high_sales:
        print(
            f'Sale ID: {row['sale_id']},'
            f'Store: {row['store']}, '
            f'Revenue: KES {row['revenue']:,.2f}'
        )

    print(f'Number of high value sales: {len(high_sales)}')

    high_value_by_store = {
        store: sum(row['store'] == store for row in high_sales)
        for store in {row['store'] for row in high_sales}
    }

    print('High value sales by store:')
    for store, count in sorted(high_value_by_store.items()):
        print(f'{store}: {count} sales')


    revenues = [row['revenue'] for row in clean_sales]

    print('Average transaction revenue:')
    if revenues:
        print(f'KES {mean(revenues):,.2f}')
    else:
        print('No valid sales available')

    print('Median transaction revenue:')
    if revenues:
        print(f'KES {median(revenues):,.2f}')
    else:
        print('No valid sales available')

    print('Minimum and maximum transaction revenue:')
    if revenues:
        smallest, largest = minimum_maximum(revenues)
        print(f'Minimum: KES {smallest:,.2f}')
        print(f'Maximum: KES {largest:,.2f}')
    else:
        print('No valid sales available')


    my_results = {
        'total_revenue': total_revenue(clean_sales),
        'product_totals': revenue_by(clean_sales, 'product'),
        'top_3': top_n(revenue_by(clean_sales, 'product'), 3),
        'mean_median': (
            mean(revenues),
            median(revenues)
        ),
        'minimum': smallest,
        'maximum': largest
    }

    print('===== pandas verification ====')

    verification = verify_with_pandas(DATA_PATH, my_results)
    

    output_folder = Path('output')
    output_folder.mkdir(exist_ok=True)

    with (output_folder / 'sales_report.txt').open('w') as file:
        print('Revenue by product (KES)', file=file)
        for product, revenue in sorted(
            product_totals.items(),
            key=lambda item: item[1],
            reverse=True
        ):
            print(f' {product:<24}{revenue:>14,.2f}', file=file)

        print('\nTop 3 products', file=file)
        for rank, (product, revenue) in enumerate(top_products, start=1):
            print(f' {rank}. {product} - KES {revenue:,.2f}', file=file)

        print(f'\nHigh value transactions(>= 50,000) : {len(high_sales)}', file=file)
        for row in high_sales:
            print(
                f' {row['sale_id']} {row['sale_date']} {row['store']} '
                f' {row['product']}  KES {row['revenue']:,.2f}',
                file=file
            )

        print('\nTransaction revenue statistics', file=file)
        print(f' mean : {mean(revenues):,.2f}', file=file)
        print(f' median : {median(revenues):,.2f}', file=file)
        print(f' min : {smallest:,.2f}', file=file)
        print(f' max: {largest:,.2f}',file=file)

        print('\n=== pandas verification ===', file=file)
        for label, result in verification.items():
            print(f'{label} : {result}', file=file)

    print('Report saved to output')


        
