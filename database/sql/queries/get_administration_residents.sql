SELECT Residents.*, Stations.name AS station
FROM Residents
INNER JOIN Stations 
ON Stations.stationID = Residents.stationID
ORDER BY Residents.room ASC;