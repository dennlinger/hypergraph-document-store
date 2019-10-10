#!/bin/bash

for window in 0 1 2 5 10 20;
do
    python3 GenerateNewSchema.py --window-size $window
done;

