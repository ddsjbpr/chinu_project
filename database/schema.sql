CREATE TABLE IF NOT EXISTS customers (
    customerNumber INTEGER PRIMARY KEY,
    customerName TEXT NOT NULL,
    contactLastName TEXT NOT NULL,
    contactFirstName TEXT NOT NULL,
    phone TEXT,
    addressLine1 TEXT,
    addressLine2 TEXT,
    city TEXT,
    state TEXT,
    postalCode TEXT,
    country TEXT,
    salesRepEmployeeNumber REAL,
    creditLimit REAL
);

CREATE TABLE IF NOT EXISTS orders (
    orderNumber INTEGER PRIMARY KEY,
    orderDate TEXT NOT NULL,
    requiredDate TEXT NOT NULL,
    shippedDate TEXT,
    status TEXT,
    comments TEXT,
    customerNumber INTEGER NOT NULL,
    FOREIGN KEY (customerNumber) REFERENCES customers(customerNumber)
);

CREATE TABLE IF NOT EXISTS payments (
    customerNumber INTEGER NOT NULL,
    checkNumber TEXT NOT NULL,
    paymentDate TEXT NOT NULL,
    amount REAL NOT NULL,
    PRIMARY KEY (customerNumber, checkNumber),
    FOREIGN KEY (customerNumber) REFERENCES customers(customerNumber)
);
