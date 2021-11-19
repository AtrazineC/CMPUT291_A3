# Group 23
- Lora Ma (lora)
- Benjamin Kong (bkong)
- Jordan Rusk (rusk)

We declare that we did not collaborate with anyone outside our own group in this assignment.

# Resources used:
<List Here>

# Indices Created:
## Query 1:
We executed the following SQL query:

SELECT COUNT(*) 
FROM Customers C, Orders O 
WHERE C.customer_postal_code == randomPostalCode 
AND C.customer_id == O.customer_id

In the above query, randomPostalCode is the randomly selected postal code.

We assumed SQLite would create an index for Customers.customer_id since it is a primary key, but this would not help us with Customer.customer_postal_code = randomPostalCode. We chose to create an index on Customers.customer_postal_code and Orders.customer_id which allows us to avoid accessing Cusomers.

## Query 2:
We executed the following SQL query:

SELECT COUNT(oid), AVG(size) FROM OrderSize
WHERE oid IN (
	SELECT O.order_id FROM Orders O, Customers C
	WHERE O.customer_id = C.customer_id
	AND O.order_id = oid
	AND C.customer_postal_code = randomPostalCode
)

In the above query, randomPostalCode is the randomly selected postal code.

TODO: Explain why we chose the indices we used.

## Query 3:
We executed the following SQL query:

SELECT COUNT(order_id), (COUNT(order_item_id)/COUNT(DISTINCT order_item_id)) as average FROM Order_items
WHERE order_id IN (
	SELECT O.order_id FROM Orders O, Customers C
        WHERE O.customer_id = C.customer_id
        AND O.order_id = order_id
        AND C.customer_postal_code = :postal
)
GROUP BY order_id;

TODO

## Query 4:
We executed the following SQL query:

SELECT COUNT(DISTINCT s.seller_postal_code) 
FROM Orders O, Sellers S, Order_items I 
WHERE O.order_id = randomOrderId
AND O.order_id = I.order_id 
AND S.seller_id = I.seller_id

In the above query, randomOrderId is the randomly selected order id.

TODO: Explain why we chose the indices we used.
