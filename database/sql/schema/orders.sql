CREATE TABLE IF NOT EXISTS Orders(
    orderID INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    lunch VARCHAR(50),
    dinner VARCHAR(50),
    halfPortion BOOLEAN,
    noSoup BOOLEAN,
    lunchHalfPortion BOOLEAN DEFAULT 0,
    dinnerHalfPortion BOOLEAN DEFAULT 0,
    lunchNoSoup BOOLEAN DEFAULT 0,
    dinnerNoSoup BOOLEAN DEFAULT 0,
    noDessert BOOLEAN DEFAULT 0,
    notes VARCHAR(100),
    lunchNotes VARCHAR(100) DEFAULT '',
    dinnerNotes VARCHAR(100) DEFAULT '',
    residentID INTEGER REFERENCES Residents(residentID),
    UNIQUE (residentID, date)
);