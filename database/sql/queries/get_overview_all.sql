SELECT Residents.name AS residentName, 
Residents.room AS residentRoom
, Orders.* 
FROM Residents
INNER JOIN Orders
ON Orders.residentID = Residents.residentID
WHERE Orders.date = ? 
ORDER BY Residents.room ASC