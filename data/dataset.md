## Dataset

About
This dataset is designed for bankruptcy prediction concerning American public companies. It includes detailed accounting data for companies listed on the New York Stock Exchange (NYSE) and NASDAQ from 1999 to 2018. The dataset identifies companies as bankrupt if their management filed for Chapter 11 (reorganisation) or Chapter 7 (cessation of operations) of the Bankruptcy Code. A label of '1' signifies bankruptcy in the fiscal year prior to filing, while '0' indicates normal operation. This dataset is notable for being complete, with no missing values, synthetic entries, or imputed additions.
Columns
company_name: The name of the company. This column can be optionally removed.
status_label: The target column indicating the company's status, either 'alive' or 'failed' (bankrupt).
year: The fiscal year to which the accounting data corresponds, ranging from 1999 to 2018.
X1 (Current assets): All assets expected to be sold or used in standard business operations within the next year.
X2 (Cost of goods sold): The total amount paid directly related to the sale of products.
X3 (Depreciation and amortisation): The loss of value of tangible (depreciation) and intangible (amortisation) fixed assets over time.
X4 (EBITDA): Earnings before interest, taxes, depreciation, and amortisation, serving as a measure of overall financial performance.
X5 (Inventory): The accounting of items and raw materials used in production or sold by the company.
X6 (Net Income): The overall profitability of a company after all expenses and costs have been deducted from total revenue.
X7 (Total Receivables): The balance of money owed to a firm for goods or services delivered or used but not yet paid for by customers.
X8 (Market value): The price of an asset in a marketplace, specifically referring to market capitalisation for publicly traded companies.
X9 (Net sales): The sum of a company's gross sales minus returns, allowances, and discounts.
X10 (Total assets): All assets, or items of value, owned by a business.
X11 (Total Long-term debt): A company's loans and other liabilities not due within one year of the balance sheet date.
X12 (EBIT): Earnings before interest and taxes.
X13 (Gross Profit): The profit a business makes after subtracting all costs related to manufacturing and selling its products or services.
X14 (Total Current Liabilities): The sum of accounts payable, accrued liabilities, and taxes such as bonds payable at year-end, salaries, and commissions remaining.
X15 (Retained Earnings): The amount of profit a company has left after paying all its direct costs, indirect costs, income taxes, and dividends to shareholders.
X16 (Total Revenue): The income a business has made from all sales before subtracting expenses, potentially including interest and dividends from investments.
X17 (Total Liabilities): The combined debts and obligations that the company owes to outside parties.
X18 (Total Operating Expenses): The expenses a business incurs through its normal business operations.