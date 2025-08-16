#!/bin/bash

# Test response times for mining status API

echo "🔍 Testing API response times..."
echo "================================"

for i in {1..10}; do
    echo -n "Test $i: "
    start_time=$(date +%s.%N)
    
    response=$(curl -s -w "%{http_code}" http://localhost:8001/api/mining/status)
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    echo "${duration}s (HTTP: ${response: -3})"
    sleep 0.5
done

echo ""
echo "📊 Average response should be under 0.1s for real-time updates"