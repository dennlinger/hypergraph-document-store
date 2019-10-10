#!/bin/bash


for window in 0 1 2 5;
do
    python3 GenerateNewSchema.py --window-size $window --entities-only false --prefix full
done;

