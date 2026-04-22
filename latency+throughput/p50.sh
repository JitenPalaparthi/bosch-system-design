#!/bin/bash
# Script: p50_ping.sh
# Purpose: Ping a host multiple times and calculate the p50 (median) latency.

# --- Input Validation ---
if [ $# -lt 2 ]; then
    echo "Usage: $0 <host> <count>"
    echo "Example: $0 google.com 10"
    exit 1
fi

HOST="$1"
COUNT="$2"

# Ensure COUNT is a positive integer
if ! [[ "$COUNT" =~ ^[0-9]+$ ]] || [ "$COUNT" -le 0 ]; then
    echo "Error: count must be a positive integer."
    exit 1
fi

# --- Ping and Extract Latencies ---
# Using LC_ALL=C to ensure consistent decimal format
LATENCIES=$(ping -c "$COUNT" "$HOST" 2>/dev/null | \
    grep 'time=' | \
    sed -E 's/.*time=([0-9.]+) ms/\1/' )

# Check if we got any results
if [ -z "$LATENCIES" ]; then
    echo "Error: Unable to ping $HOST or no latency data found."
    exit 1
fi

# --- Sort and Calculate Median (p50) ---
# Convert to sorted list
SORTED=$(echo "$LATENCIES" | sort -n)

# Count number of samples
N=$(echo "$SORTED" | wc -l)

# Find median index
if (( N % 2 == 1 )); then
    # Odd count → middle value
    MEDIAN=$(echo "$SORTED" | awk "NR == (N+1)/2 {print}")
else
    # Even count → average of two middle values
    M1=$(echo "$SORTED" | awk "NR == N/2 {print}")
    M2=$(echo "$SORTED" | awk "NR == N/2 + 1 {print}")
    MEDIAN=$(awk "BEGIN {print ($M1 + $M2)/2}")
fi

# --- Output ---
echo "Host: $HOST"
echo "Pings: $N"
echo "Latencies (ms): $SORTED"
echo "p50 (Median) latency: ${MEDIAN} ms"
