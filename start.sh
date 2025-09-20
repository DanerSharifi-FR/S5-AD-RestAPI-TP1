#!/bin/bash

# Kill any process using the required ports
for port in 3200 3201 3202 3203; do
  fuser -k ${port}/tcp 2>/dev/null
done

python3 ./movie/movie.py &
PID1=$!
python3 ./schedule/schedule.py &
PID2=$!
python3 ./user/user.py &
PID3=$!
python3 ./booking/booking.py &
PID4=$!

wait $PID1 $PID2 $PID3 $PID4