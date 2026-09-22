SELECT 
    Residents.residentID,
    Residents.name,
    Residents.room,
    Stations.name AS station,
    COUNT(DISTINCT Orders.date) AS order_count
FROM Residents
    INNER JOIN Stations ON Stations.stationID = Residents.stationID
    LEFT JOIN Orders ON Orders.residentID = Residents.residentID 
    AND Orders.date BETWEEN ? AND ?