#
# lora lab 11 MA5.py
# I declare that I did not collaborate with anyone in this micro-assignment. 
# Besides the lab and class notes, I used the following resources: 
# N/A
# 
import sqlite3
import time

connection = None
cursor = None


def connect(path):
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()
    return

def uniformedOptimization():
    cursor.execute('PRAGMA automatic_index = False')

    cursor.execute('CREATE TABLE "CustomersNew" ("customer_id" TEXT,"customer_postal_code" INTEGER);')
    cursor.execute('INSERT INTO CustomersNew SELECT customer_id, customer_postal_code FROM Customers;')
    cursor.execute('ALTER TABLE Customers RENAME TO CustomersOriginal;')
    cursor.execute('ALTER TABLE CustomersNew RENAME TO Customers;')

    cursor.execute('CREATE TABLE "Order_items_new" ("order_item_id" INTEGER, "order_id" TEXT, "product_id" TEXT, "seller_id" TEXT);')
    cursor.execute('INSERT INTO Order_items_new SELECT order_item_id, order_id, product_id, seller_id FROM Order_items')
    cursor.execute('ALTER TABLE Order_items RENAME TO Order_items_original;')
    cursor.execute('ALTER TABLE Order_items_new RENAME TO Order_items;')

    
    cursor.execute('CREATE TABLE "OrdersNew" ("order_id" TEXT, "customer_id" TEXT);')
    cursor.execute('INSERT INTO OrdersNew SELECT order_id, customer_id FROM Orders;')
    cursor.execute('ALTER TABLE Orders RENAME TO OrdersOriginal;')
    cursor.execute('ALTER TABLE OrdersNew RENAME TO Orders;')

    cursor.execute('CREATE TABLE "SellersNew" ("seller_id" TEXT, "seller_postal_code" INTEGER);')
    cursor.execute('INSERT INTO SellersNew SELECT seller_id, seller_postal_code FROM Sellers;')
    cursor.execute('ALTER TABLE Sellers RENAME TO SellersOriginal;')
    cursor.execute('ALTER TABLE SellersNew RENAME TO Sellers;')


def selfOptimizedOptimization():
    cursor.execute('DROP TABLE Customers;')
    cursor.execute('ALTER TABLE CustomersOriginal RENAME TO Customers;')

    cursor.execute('DROP TABLE Order_items;')
    cursor.execute('ALTER TABLE Order_items_original RENAME TO Order_items;')
    
    cursor.execute('DROP TABLE Orders;')
    cursor.execute('ALTER TABLE OrdersOriginal RENAME TO Orders;')

    cursor.execute('DROP TABLE Sellers;')
    cursor.execute('ALTER TABLE SellersOriginal RENAME TO Sellers;')
    cursor.execute('PRAGMA automatic_index = True')
    
def query1():
    cursor.execute('SELECT customer_postal_code FROM Customers ORDER BY RANDOM() LIMIT 1')
    randomPostalCode=cursor.fetchall()[0][0]
    cursor.execute('SELECT COUNT(*) FROM Customers C, Orders O WHERE C.customer_postal_code == :P AND C.customer_id == O.customer_id', {"P": randomPostalCode})
    count = randomPostalCode=cursor.fetchall()[0][0]

def executeQuery1():
    total = 0
    results = []
    for i in range(50):
        startTime = time.time()
        query1()
        endTime = time.time()
        runTime = (endTime - startTime)*1000
        results.append(runTime)
        total += runTime

    return total/len(results)
    

def getData():
    global connection, cursor
    uniformedOptimization()
    query1Small1 = executeQuery1()
    print(query1Small1)
    selfOptimizedOptimization()
    query1Small2 = executeQuery1()
    print(query1Small2)
    connection.commit()

def main():
    global connection, cursor
    path = "./A3Small.db"
    connect(path)
    print("Connection to the database open.")
    getData();
    connection.commit()
    connection.close()
    print("Connection to the database closed.")
    return


if __name__ == "__main__":
    main()
