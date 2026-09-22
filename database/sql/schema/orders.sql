CREATE TABLE IF NOT EXISTS Orders(
    orderID INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    lunch VARCHAR(50),
    dinner VARCHAR(50),
    halfPortion BOOLEAN,
    noSoup BOOLEAN,
    notes VARCHAR(100),
    residentID INTEGER REFERENCES Residents(residentID),
    UNIQUE (residentID, date)
);