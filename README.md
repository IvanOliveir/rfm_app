# RFM_app

Recency, frequency, monetary value is a marketing analysis tool used to identify a company's or an organization's best customers by using certain measures. 

The RFM model is based on three quantitative factors:

- **Recency:** How recently a customer has made a purchase
- **Frequency:** How often a customer makes a purchase
- **Monetary Value:** How much money a customer spends on purchases

## Customer Clusters
The moment of the customer defined as:

- **Vips:** The customers with max score in RFV
- **Valiosos:** The least percentual of customers with 20% of the revenue
- **Potenciais:** 30% of the customers with the highest revenue
- **Descompromissados:** The rest of the customers

## Customer moment
- **Entrantes:** 0 - 30 days
- **Manutenção:** 31 - 100 days
- **Recuperação:** 101 - 200 days
- **Inativo:** 200 days > 

### Recency

The shorter the time, the more valuable

| Group | Range                       |
|-------|-----------------------------|
| 4     | <= 45 days                  |
| 3     | > 45 days and <= 75 days    |
| 2     | > 75 days and <= 120 days   |
| 1     | > 120 days                  |

### Frequency

The more orders, the more valuable

| Group | Range                        |
|-------|------------------------------|
| 4     | > 5 orders                   |
| 3     | > 3 orders and <= 5 orders   |
| 2     | > 1 orders and <= 3 orders   |
| 1     | <= 1 order                   |

### Monetary

The higher the value, the more valuable

| Group | Range                      |
|-------|----------------------------|
| 4     | > R$ 1.266,50              |
| 3     | > R$ 560,40 <= R$ 1.266,50 |
| 2     | > R$270,00 <= R$560,40      |
| 1     | <= R$270,00                |
