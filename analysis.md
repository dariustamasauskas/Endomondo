
## Endomondo data analysis

Once the raw XML data was extracted and parsed into csv files, they were loaded into Google BigQuery. Now it is time to do some data analysis and try to answer some questions such as:
- What are the places with the most workouts?
- What kind of workout types were captured per each year?
- What are the monthly dynamics for each year and for each workout type?
- Which day of the week was the most popular for workouts?
- Which hour of the day was the most popular for workouts?
- What is the average workout distance, time and speed for each workout type?
- Which part of the workout has higher speed - start or end of the workout?

### What are the places with the most workouts?

As seen from the map below, the majority of workouts are in the Vilnius area. Red color marks the walking workouts, green color - running workouts, and the blue color - biking workouts.

![Workouts on the map](outputs/workouts_map.jpg)

```sql
SELECT
    CASE WHEN s.SportType = 'Other' THEN 'Walking' ELSE s.SportType END AS SportType,
    ST_GEOGPOINT(t.TrackingLongitude, t.TrackingLatitude) AS WorkoutCoord
FROM Endomondo.summary AS s
INNER JOIN Endomondo.tracking AS t
ON s.ActivityId = t.ActivityId
```

### What kind of workout types were captured per each year?

As seen from the table below, 2017 was the year with the most workouts captured, mostly walking and running (null marks total workouts). The most walking workouts were captured in 2018. The least total workouts were captured in 2019. We can also see that walking workouts were the most popular amongst other workout types, while biking workouts were very rare.

![Workouts per year](outputs/workouts_per_year.jpg)

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

### What are the monthly dynamics for each year and for each workout type?

In the following graph we can see that running workouts were captured specifically from May to September, all the 4 years and the most running workouts were captured in 2017.

![Monthly running](outputs/monthly_running.jpg)

Walking workouts were captured during other months, from March to December. We can see that the peak months were during May-June and the decrease on later months, with the exception in 2017.

![Monthly walking](outputs/monthly_walking.jpg)

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

### Which day of the week was the most popular for workouts?

We can see that Friday and Sunday were the two most popular days for doing workouts, Sunday being the most popular for running and Friday being the most popular for walking. The day with the least workouts was Saturday.

![Workouts per weekday](outputs/workouts_per_weekday.jpg)

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

### Which hour of the day was the most popular for workouts?

It is interesting to understand which hours of the day were the most popular for doing workouts. In the graph below we can see more evening workouts compared with the morning workouts (total count in bar charts). If we split workouts by type, we can see that running workouts were the most popular in the evenings, specifically around 7pm-8pm. Walking workouts were more popular in the middle and the end of the day.

As workout hours are captured in GMT, 2 hours were added to calculate the local time. Also, some coordinates were filtered out, specifically the coordinates with Longitude values less than 0.

![Workouts per hour](outputs/workouts_per_hour.jpg)

```sql
SELECT
    EXTRACT(hour FROM s.StartTime) + 2 AS WorkoutHour,
    COUNT(DISTINCT CASE WHEN s.SportType = 'Running' THEN s.ActivityId ELSE NULL END) AS RunningCount,
    COUNT(DISTINCT CASE WHEN s.SportType = 'Other' THEN s.ActivityId ELSE NULL END) AS WalkingCount,
    COUNT(DISTINCT CASE WHEN s.SportType = 'Biking' THEN s.ActivityId ELSE NULL END) AS BikingCount,
    COUNT(DISTINCT s.ActivityId) AS TotalCount
FROM Endomondo.summary AS s
INNER JOIN Endomondo.tracking AS t
ON s.ActivityId = t.ActivityId
WHERE t.TrackingLongitude > 0
GROUP BY 1
ORDER BY WorkoutHour
```

### What is the average workout distance, time and speed for each workout type?

The following table shows various statistics for each workout type through the years. We can see that biking workouts had the largest distance and speed. Running workouts were approximately around 4km of length during 2016, 2018 and 2019, with the exception in 2017, where the average distance was 6.6km. The running speed was pretty consistent during all the years and it was approximately 9.5 km/h. Walking workouts were approximately around 5km of length during 2016, 2018 and 2019, with the exception in 2017, where the average distance was 3.2km. Walking workout in 2017 were also the slowest and with the lowest duration.

![Workouts statistics](outputs/workouts_statistics.jpg)

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

### Which part of the workout has higher speed - start or end of the workout?

I wanted to understand if the higher speed of workout captured at the start of the workout or at the end of workout. I have split each workout even further - into 4 quartiles, instead of the halves.

As seen from the graph below, biking speed is decreasing quite significantly at the end of workout, from 15.3 km/h to 10.9 km/h, probably due to fatigue. Running workout speed is also decreasing, from 10 km/h to 9.4 km/h, but not so significantly as for biking workouts. Walking workouts speed, differently from biking and running, is quite stable at around 5.1-5.2 km/h.

![Workouts speeds](outputs/workouts_speeds.jpg)

```sql
WITH calculations as (
    SELECT
        ActivityID,
        TrackingID,
        COUNT(TrackingID) OVER (PARTITION BY ActivityID) AS TrackingsPerActivity,
        TrackingDistance - LAG(TrackingDistance) OVER (PARTITION BY ActivityID ORDER BY TrackingID) AS DistancePerID,
        EXTRACT(second FROM TrackingTime - LAG(TrackingTime) OVER (PARTITION BY ActivityID ORDER BY TrackingID)) AS TimePerID
    FROM Endomondo.tracking
)
SELECT
    CASE WHEN SportType = 'Other' THEN 'Walking' ELSE SportType END AS WorkoutType,
    CASE WHEN TrackingID / TrackingsPerActivity <= 0.25 THEN 'workout_1q'
         WHEN TrackingID / TrackingsPerActivity <= 0.5 THEN 'workout_2q'
         WHEN TrackingID / TrackingsPerActivity <= 0.75 THEN 'workout_3q'
         ELSE 'workout_4q'
    END AS WorkoutSplit,
    SUM(DistancePerID/1000) / SUM(TimePerID/3600) AS WorkoutSpeed
FROM calculations as c
INNER JOIN Endomondo.summary as s
ON c.ActivityID = s.ActivityID
GROUP BY 1,2
```
