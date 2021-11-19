# import the sqlite3 module so that we can use it in our python code
import sqlite3
# these two lines were added to remove a Gdk-CRITICAL error
# matplotlib.pyplot will allow us to create visualizations of our results
import matplotlib.pyplot as plt
import numpy as np

import time

# define global variables for our database connection and cursor
# these will be accessible by and consistent across all methods
connection = None
cursor = None

createView = '''CREATE VIEW OrderSize (oid, size)
        AS SELECT O.order_id, COUNT(O.order_item_id)
        FROM Order_items O
        GROUP BY O.order_id;'''

query = '''SELECT COUNT(oid), AVG(size) FROM OrderSize
           WHERE oid IN (
               SELECT O.order_id FROM Orders O, Customers C
               WHERE O.customer_id = C.customer_id
               AND O.order_id = oid
               AND C.customer_postal_code = :postal
           );
'''

# define method for connecting to database
def connect(path):
    # using global variables already defined in main method, not new variables
    global connection, cursor
    # create a connection to the sqlite3 database
    connection = sqlite3.connect(path)
    # create a cursor object which will be used to execute sql statements
    cursor = connection.cursor()
    # execute a sql statement to enforce foreign key constraint
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    # commit the changes we have made so they are visible by any other connections
    connection.commit()
    return

def Uninformed():
    global query, connection, cursor, createView

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

    ALTER TABLE Order_items RENAME TO Order_itemsOriginal;
    ALTER TABLE Order_itemsNew RENAME TO Order_items;  
    ''')

    print("got to tables made")

    cursor.execute("SELECT customer_postal_code FROM Customers ORDER BY RANDOM() LIMIT 50")
    codes = cursor.fetchall()

    print("codes selected")

    cursor.execute(createView)

    print("view created")
    results = []
    total = 0
    i = 0

    for code in codes:
        i = i + 1
        print("postal {}: {}".format(i,code[0]))
        start_time = time.time()
        cursor.execute(query,{'postal':code[0]})
        end_time = time.time()
        run_time = (end_time - start_time)*1000

        results.append(run_time)
        total = total + run_time

    average = total / len(results)

    print("average: {}".format(average))

    cursor.close()

    cursor = connection.cursor()

    cursor.executescript('''DROP VIEW OrderSize;
    DROP TABLE Order_items;
    ALTER TABLE Order_itemsOriginal RENAME TO Order_items;

    DROP TABLE Orders;
    ALTER TABLE OrdersOriginal RENAME TO Orders;
    
    DROP TABLE Sellers;
    ALTER TABLE SellersOriginal RENAME TO Sellers;

    DROP TABLE Customers;
    ALTER TABLE CustomersOriginal RENAME TO Customers;
    ''')
    connection.commit()

    return average

def Self_optimized():
    global cursor, connection, createView, query

    cursor.execute('PRAGMA automatic_index = TRUE;')

    cursor.execute(createView)

    cursor.execute("SELECT customer_postal_code FROM Customers ORDER BY RANDOM() LIMIT 50")
    codes = cursor.fetchall()

    results = []
    total = 0
    i = 0

    for code in codes:
        i = i + 1
        print("postal {}: {}".format(i,code[0]))

        start_time = time.time()
        cursor.execute(query,{'postal':code[0]})
        end_time = time.time()
        run_time = (end_time - start_time)*1000

        results.append(run_time)
        total = total + run_time

    average = total / len(results)

    cursor.close()

    cursor = connection.cursor()

    cursor.execute("DROP VIEW OrderSize;")

    return average

def User_optimized():
    global cursor, connection, createView, query

    cursor.execute('PRAGMA automatic_index = FALSE;')

    cursor.execute('CREATE INDEX oi_id_index ON Order_items(order_id,order_item_id,product_id,seller_id);')
    cursor.execute('CREATE INDEX oid_index ON Orders(order_id,customer_id);')
    cursor.execute('CREATE INDEX cid_index ON Customers(customer_id,customer_postal_code);')

    cursor.execute(createView)
    
    cursor.execute("SELECT customer_postal_code FROM Customers ORDER BY RANDOM() LIMIT 50")
    codes = cursor.fetchall()

    results = []
    total = 0
    i = 0

    for code in codes:
        i = i + 1
        print("postal {}: {}".format(i,code[0]))

        start_time = time.time()
        cursor.execute(query,{'postal':code[0]})
        end_time = time.time()
        run_time = (end_time - start_time)*1000

        results.append(run_time)
        total = total + run_time

    average = total / len(results)

    cursor.close()

    cursor = connection.cursor()

    cursor.executescript('''DROP VIEW OrderSize;
    DROP INDEX oi_id_index;
    DROP INDEX oid_index;
    DROP INDEX cid_index;''')

    return average

def stacked_bar_graph(first_stack, second_stack, third_stack):
    # labels = ['SmallDB','MediumDB','LargeDB']
    labels = ['SmallDB', 'MediumDB', 'LargeDB']
    width = 0.5
    fig, ax = plt.subplots()
    #Bar Data
    ax.bar(labels, first_stack, width, label = 'Uninformed')
    ax.bar(labels, second_stack, width, bottom = first_stack, label = 'Self-Optimized')
    ax.bar(labels, third_stack, width, bottom = np.array(first_stack) + np.array(second_stack), label='User-Optimized')

    ax.set_title('Q2 (Runtime in ms)')
    ax.legend()

    path = './{}A3chart.png'.format('Q2')
    plt.savefig(path)
    print('Chart saved to file {}'.format(path))
    
    plt.close()

    return

# define the main method that will run when our python program runs
def main():
    global connection, cursor
    # we will hard code the database name, could also get from user
    # db_paths = ["./A3Small.db","./A3Medium.db","./A3Large.db"]
    db_paths = ["./A3Small.db", "./A3Medium.db", "./A3Large.db"]
    uninformed_vals = []
    self_opt_vals = []
    user_opt_vals = []
    
    for path in db_paths:

        connect(path)
        results = Uninformed()
        uninformed_vals.append(results)
        print("scenario 1: {}".format(results))
        connection.close()

        connect(path)
        results = Self_optimized()
        self_opt_vals.append(results)
        print("scenario 2: {}".format(results))
        connection.close()

        connect(path)
        results = User_optimized()
        user_opt_vals.append(results)
        print("scenario 3: {}".format(results))
        connection.close()

    stacked_bar_graph(uninformed_vals,self_opt_vals,user_opt_vals)
    
    # close connection before exiting
    connection.close()
    return

# run main method when program starts
if __name__ == "__main__":
    main()