#!/bin/bash

# Kill any process using the required ports
for port in 3200 3201 3202 3203; do
  fuser -k ${port}/tcp 2>/dev/null
done

pymon ./movie/movie.py &
PID1=$!
pymon ./schedule/schedule.py &
PID2=$!
pymon ./user/user.py &
PID3=$!
pymon ./booking/booking.py &
PID4=$!

wait $PID1 $PID2 $PID3 $PID4