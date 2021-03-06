import sqlite3
import time
import matplotlib.pyplot as plt
import numpy as np

connection = None
cursor = None
uninformed = []
self = []
user = []

def stacked_bar_graph(first_stack, second_stack, third_stack):
    labels = ['SmallDB', 'MediumDB', 'LargeDB']
    width = 0.5
    fig, ax = plt.subplots()
    #Bar Data
    ax.bar(labels, first_stack, width, label = 'Uninformed')
    ax.bar(labels, second_stack, width, bottom = first_stack, label = 'Self-Optimized')
    ax.bar(labels, third_stack, width, bottom = np.array(first_stack) + np.array(second_stack), label='User-Optimized')

    ax.set_title('Q1 (Runtime in ms)')
    ax.legend()

    path = './{}A3chart.png'.format('Q1')
    plt.savefig(path)
    print('Chart saved to file {}'.format(path))
    
    plt.close()
    return

def connect(path):
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return

def uninformedOptimization():
    cursor.execute('PRAGMA automatic_index = FALSE;')

    cursor.executescript('''CREATE TABLE CustomersNew (
    customer_id TEXT,
    customer_postal_code INTEGER
    );

    INSERT INTO CustomersNew SELECT customer_id, customer_postal_code FROM Customers;

    ALTER TABLE Customers RENAME TO CustomersOriginal;
    ALTER TABLE CustomersNew RENAME TO Customers;
    
    CREATE TABLE SellersNew (
        seller_id TEXT,
        seller_postal_code INTEGER
    );

    INSERT INTO SellersNew SELECT seller_id, seller_postal_code FROM Sellers;

    ALTER TABLE Sellers RENAME TO SellersOriginal;
    ALTER TABLE SellersNew RENAME TO Sellers;

    CREATE TABLE OrdersNew (
        order_id TEXT,
        customer_id TEXT
    );

    INSERT INTO OrdersNew SELECT order_id, customer_id FROM Orders;

    ALTER TABLE Orders RENAME TO OrdersOriginal;
    ALTER TABLE OrdersNew RENAME TO Orders;

    CREATE TABLE Order_itemsNew (
        order_id TEXT,
        order_item_id INTEGER,
        product_id TEXT,
        seller_id TEXT
    );

    INSERT INTO Order_itemsNew SELECT order_id, order_item_id, product_id, seller_id FROM Order_items;

    ALTER TABLE Order_items RENAME TO Order_items_original;
    ALTER TABLE Order_itemsNew RENAME TO Order_items;  
    ''')


def selfOptimizedOptimization():
    global cursor
    cursor.execute('PRAGMA automatic_index = True')

    cursor.executescript('''DROP TABLE Customers;
    ALTER TABLE CustomersOriginal RENAME TO Customers;

    DROP TABLE Order_items;
    ALTER TABLE Order_items_original RENAME TO Order_items;

    DROP TABLE Orders;
    ALTER TABLE OrdersOriginal RENAME TO Orders;

    DROP TABLE Sellers;
    ALTER TABLE SellersOriginal RENAME TO Sellers
    ''')

def userOptimized():
    cursor.execute('PRAGMA automatic_index = true;')
    cursor.execute('CREATE INDEX cid_index ON Customers(customer_postal_code);')
    cursor.execute('CREATE INDEX oid_index ON Orders(customer_id);')

def query(randomPostalCode):
    cursor.execute('SELECT COUNT(*) FROM Customers C, Orders O WHERE C.customer_postal_code = :P AND C.customer_id = O.customer_id', {"P": randomPostalCode})

def executeQuery():
    total = 0
    results = []
    cursor.execute('SELECT customer_postal_code FROM Customers ORDER BY RANDOM() LIMIT 50')
    randomPostalCodes = cursor.fetchall()
    for i in range(50):
        startTime = time.time()
        query(randomPostalCodes[i][0])
        endTime = time.time()
        runTime = (endTime - startTime)*1000
        results.append(runTime)
        total += runTime

    return total/len(results)

def getData():
    global connection, cursor

    uninformedOptimization()
    querySmall1 = executeQuery()
    uninformed.append(querySmall1)
    print(querySmall1)

    selfOptimizedOptimization()
    querySmall2 = executeQuery()
    self.append(querySmall2)
    print(querySmall2)

    userOptimized()
    querySmall3 = executeQuery()
    user.append(querySmall3)
    print(querySmall3)

    cursor.execute('DROP INDEX oid_index')
    cursor.execute('DROP INDEX cid_index')
    connection.commit()

def main():
    global connection, cursor
    paths = ["./A3Small.db", "./A3Medium.db", "./A3Large.db"]
    
    for i in range(len(paths)):
        connect(paths[i])
        print("Connection to the database open.")
        getData()
        connection.commit()
        connection.close()
        print("Connection to the database closed.")
    
    stacked_bar_graph(uninformed, self, user)

    return


if __name__ == "__main__":
    main()
