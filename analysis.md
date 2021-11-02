
## Endomondo data analysis

Once the raw XML data was extracted and parsed into csv files, they were loaded into Google BigQuery. Now it is time to do some data analysis and try to answer some questions such as:
- What are the places with the most workouts
- What kind of workout types were captured per each year
- What are the monthly dynamics for each year and for each workout type
- Which day of the week was the most popular for workouts
- Which hour of the day was the most popular for workouts
- What is the average workout distance, time and speed for each workout type
- Which part of the workout has higher speed - start or end of the workout

#### What are the places with the most workouts

As seen from the map below, the majority of workouts are in the Vilnius area. Red color marks the walking workouts, green color - running workouts, and the blue color - biking workouts.

```sql
SELECT
    CASE WHEN s.SportType = 'Other' THEN 'Walking' ELSE s.SportType END AS SportType,
    ST_GEOGPOINT(t.TrackingLongitude, t.TrackingLatitude) AS WorkoutCoord
FROM Endomondo.summary AS s
INNER JOIN Endomondo.tracking AS t
USING (ActivityId)
```

#### What kind of workout types were captured per each year

```sql
SELECT
    CASE WHEN SportType = 'Other' THEN 'Walking' ELSE SportType END AS SportType,
    SUM(CASE WHEN EXTRACT(year FROM StartDate) = 2016 THEN 1 ELSE 0 END) AS year_2016,
    SUM(CASE WHEN EXTRACT(year FROM StartDate) = 2017 THEN 1 ELSE 0 END) AS year_2017,
    SUM(CASE WHEN EXTRACT(year FROM StartDate) = 2018 THEN 1 ELSE 0 END) AS year_2018,
    SUM(CASE WHEN EXTRACT(year FROM StartDate) = 2019 THEN 1 ELSE 0 END) AS year_2019
FROM Endomondo.summary
GROUP BY ROLLUP(SportType)
```

#### What are the monthly dynamics for each year and for each workout type

```sql
SELECT
    CASE WHEN SportType = 'Other' THEN 'Walking' ELSE SportType END AS SportType,
    EXTRACT(month FROM StartDate) AS WorkoutMonth,
    SUM(CASE WHEN EXTRACT(year FROM StartDate) = 2016 THEN 1 ELSE 0 END) AS workouts_2016,
    SUM(CASE WHEN EXTRACT(year FROM StartDate) = 2017 THEN 1 ELSE 0 END) AS workouts_2017,
    SUM(CASE WHEN EXTRACT(year FROM StartDate) = 2018 THEN 1 ELSE 0 END) AS workouts_2018,
    SUM(CASE WHEN EXTRACT(year FROM StartDate) = 2019 THEN 1 ELSE 0 END) AS workouts_2019
FROM Endomondo.summary
GROUP BY 1, 2
ORDER BY WorkoutMonth
```

#### Which day of the week was the most popular for workouts

```sql
SELECT
    CASE WHEN SportType = 'Other' THEN 'Walking' ELSE SportType END AS SportType,
    SUM(CASE WHEN FORMAT_DATE('%A', StartDate) = 'Monday' THEN 1 ELSE 0 END) AS Monday,
    SUM(CASE WHEN FORMAT_DATE('%A', StartDate) = 'Tuesday' THEN 1 ELSE 0 END) AS Tuesday,
    SUM(CASE WHEN FORMAT_DATE('%A', StartDate) = 'Wednesday' THEN 1 ELSE 0 END) AS Wednesday,
    SUM(CASE WHEN FORMAT_DATE('%A', StartDate) = 'Thursday' THEN 1 ELSE 0 END) AS Thursday,
    SUM(CASE WHEN FORMAT_DATE('%A', StartDate) = 'Friday' THEN 1 ELSE 0 END) AS Friday,
    SUM(CASE WHEN FORMAT_DATE('%A', StartDate) = 'Saturday' THEN 1 ELSE 0 END) AS Saturday,
    SUM(CASE WHEN FORMAT_DATE('%A', StartDate) = 'Sunday' THEN 1 ELSE 0 END) AS Sunday
FROM Endomondo.summary
GROUP BY ROLLUP(SportType)
```

#### Which hour of the day was the most popular for workouts

```sql
SELECT
    EXTRACT(hour FROM s.StartTime) + 2 AS WorkoutHour,
    COUNT(DISTINCT CASE WHEN s.SportType = 'Running' THEN s.ActivityId ELSE NULL END) AS RunningCount,
    COUNT(DISTINCT CASE WHEN s.SportType = 'Other' THEN s.ActivityId ELSE NULL END) AS WalkingCount,
    COUNT(DISTINCT CASE WHEN s.SportType = 'Biking' THEN s.ActivityId ELSE NULL END) AS BikingCount,
    COUNT(DISTINCT s.ActivityId) AS TotalCount
FROM Endomondo.summary AS s
INNER JOIN Endomondo.tracking AS t
USING (ActivityId)
WHERE t.TrackingLongitude > 0
GROUP BY 1
ORDER BY WorkoutHour
```

#### What is the average workout distance, time and speed for each workout type

```sql
SELECT
    CASE WHEN SportType = 'Other' THEN 'Walking' ELSE SportType END AS SportType,
    EXTRACT(year FROM StartDate) AS WorkoutYear,
    COUNT(ActivityId) AS WorkoutCount,
    ROUND(AVG(TotalDistance/1000),1) as AvgWorkoutDistance,
    ROUND(AVG(TotalTime/3600),2) as AvgWorkoutTime,
    ROUND(AVG(TotalDistance/1000)/AVG(TotalTime/3600),2) as AvgWorkoutSpeed
FROM Endomondo.summary
GROUP BY 1, 2
ORDER BY SportType, WorkoutYear
```

#### Which part of the workout has higher speed - start or end of the workout

```sql
to be added
```
