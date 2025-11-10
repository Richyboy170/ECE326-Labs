# ECE326 Lab 3 - Search Engine with PageRank

IP ADDRESS: http://204.236.209.159:8080

Instance ID:  i-0ee9470aa16dc1a09
Public IP:    204.236.209.159
Key file:     ece326-keypair.pem


We use Labs\benchmark_comparison.py to compare between Lab2 and Lab3. We added the source file in benchmarks to be the setup, but the actual place of the ran benchmark_comparison.py which used to generate Benchmark Comparison Report below is not at the place described

# ECE326 Labs - Benchmark Comparison Report

Lab 3 performs better than Lab 2, handling 183.79 requests per second compared to 165.14, with a faster average response time of 54.42ms versus 61.02ms. The most notable difference is in the 99th percentile latency, where Lab 3 achieves 66ms while Lab 2 takes 658.5ms, showing that Lab 3 maintains much more consistent performance under heavy load.