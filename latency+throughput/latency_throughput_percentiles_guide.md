# Latency, Throughput, p50, p95, p99, p999 — Practical Guide

## 1) What is latency?

**Latency** is the time taken for a request or operation to complete.

Examples:
- A user clicks **Login** and gets a response in **120 ms**.
- A database query finishes in **8 ms**.
- A network packet reaches another machine in **2 ms** one-way or **4 ms round trip**.

In simple terms:

```text
Latency = Time taken to complete one request / one operation
```

### Common places where latency appears
- Network calls between services
- API gateway to backend service
- Database queries
- Disk I/O
- Cache reads/writes
- Message broker publish/consume
- DNS lookup
- TLS handshake

### Units used
- **seconds (s)**
- **milliseconds (ms)** → 1 second = 1000 ms
- **microseconds (us)** → 1 ms = 1000 us

---

## 2) What is throughput?

**Throughput** is the amount of work completed in a unit of time.

Examples:
- **1000 requests/second** handled by an API
- **500 MB/s** disk read speed
- **200 messages/second** consumed from Kafka
- **1 Gbps** network transfer rate

In simple terms:

```text
Throughput = Number of successful operations per second
```

### Latency vs Throughput
They are related, but they are not the same.

- **Latency** = how long one request takes
- **Throughput** = how many requests can be completed per second

A system can:
- have **low latency and low throughput**
- have **high throughput but bad tail latency**
- look good on average but fail under bursts

---

## 3) Why average latency is not enough

Suppose you sent 100 requests.

- 90 requests finished in **10 ms**
- 9 requests finished in **100 ms**
- 1 request finished in **3000 ms**

Average may still look acceptable, but one user had a terrible experience.

That is why we use **percentiles**.

---

## 4) What are p50, p90, p95, p99, p999?

A percentile tells you how many requests were completed **within** a particular latency value.

### p50
Also called **median**.

```text
p50 = 50% of requests completed in this time or less
```

If p50 is **20 ms**, half the requests finished in **20 ms or below**.

### p90
```text
p90 = 90% of requests completed in this time or less
```

### p95
```text
p95 = 95% of requests completed in this time or less
```

### p99
```text
p99 = 99% of requests completed in this time or less
```

### p999
Also written as **p99.9**.

```text
p999 = 99.9% of requests completed in this time or less
```

This is a **tail latency** metric. It helps detect rare but painful slow requests.

---

## 5) Example to understand percentiles

Assume 10 request latencies in ms:

```text
5, 6, 7, 8, 9, 10, 12, 20, 100, 500
```

- **p50** is around middle → about **9–10 ms**
- **p90** is near the 9th value → about **100 ms**
- **p99** will be near the worst end → close to **500 ms** in this tiny sample

This tells us:
- Most requests are fast
- A few requests are very slow
- Tail latency is poor

---

## 6) Why p95, p99, p999 matter

### p50 tells typical behavior
Useful for understanding the experience of the “average” user.

### p95 shows the slow edge of normal traffic
Useful for production SLO/SLA analysis.

### p99 shows tail latency
Useful because distributed systems often fail in the tail.

### p999 shows rare worst-case behavior
Useful for:
- high-scale systems
- trading systems
- low-latency platforms
- systems where a tiny slow fraction still hurts many users

### In distributed systems
If one user request touches multiple services, the slowest downstream dependency can dominate total latency.

Example:
- API gateway
- auth service
- user service
- cache
- database

Even if each service is “mostly fast,” the combined **tail** may become very bad.

---

## 7) Reasons to calculate p50, p95, p99, p999

You calculate these to:

1. **Measure real user experience**
   - Average hides outliers.

2. **Detect tail latency problems**
   - GC pauses
   - slow DB queries
   - network jitter
   - retries
   - queue buildup
   - lock contention

3. **Set SLOs and SLAs**
   - Example: “p95 latency must stay below 200 ms.”

4. **Compare systems correctly**
   - Two systems may have the same average latency but very different p99.

5. **Capacity planning**
   - Load increases often damage p95/p99 before averages move much.

6. **Performance tuning**
   - Helps identify whether optimization improved the common case or only the median.

7. **Understand burst behavior**
   - Short spikes can damage p99/p999 badly.

---

## 8) Important terms related to latency

### Response time
Often used interchangeably with latency for APIs.

### Round-trip time (RTT)
Time for a packet/request to go and come back.

### Jitter
Variation in latency over time.

### Tail latency
Latency seen in the worst small fraction of requests, such as p99 or p999.

### Service time
Actual time spent processing.

### Wait time / queue time
Time spent waiting before processing starts.

### End-to-end latency
Total time from client request to final response.

---

## 9) General formula intuition

For a stable system, throughput and latency are often discussed using queueing intuition.

A useful idea:

```text
As utilization approaches 100%, latency rises sharply.
```

This is why a system may look fine at 40% load and terrible at 85% load.

---

## 10) Network latency commands on Mac and Linux

## A) ping
Basic RTT measurement.

```bash
ping google.com
```

Limit the count:

### Linux
```bash
ping -c 20 google.com
```

### macOS
```bash
ping -c 20 google.com
```

What it gives:
- per-packet latency
- min/avg/max
- packet loss

Good for:
- network reachability
- rough RTT

Not enough for:
- p95/p99 for real HTTP traffic
- server-side latency

---

## B) traceroute / tracepath
Find where latency increases across hops.

### macOS / Linux
```bash
traceroute google.com
```

If `traceroute` is not installed on Linux:

```bash
sudo apt install traceroute
```

Alternative on Linux:

```bash
tracepath google.com
```

---

## C) curl timing for HTTP latency
Use `curl` to measure DNS, connect, TLS, TTFB, and total time.

```bash
curl -o /dev/null -s -w 'dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s ttfb=%{time_starttransfer}s total=%{time_total}s\n' https://example.com
```

Useful fields:
- `time_namelookup` → DNS time
- `time_connect` → TCP connect time
- `time_appconnect` → TLS handshake time
- `time_starttransfer` → TTFB
- `time_total` → full request time

Run multiple times:

```bash
for i in {1..20}; do
  curl -o /dev/null -s -w '%{time_total}\n' https://example.com
 done
```

Save results:

```bash
for i in {1..100}; do
  curl -o /dev/null -s -w '%{time_total}\n' https://example.com
 done > latency.txt
```

---

## 11) Throughput commands on Mac and Linux

## A) Throughput using `curl` download speed

```bash
curl -o /dev/null -s -w 'size=%{size_download} bytes speed=%{speed_download} bytes/s total=%{time_total}s\n' https://speed.hetzner.de/100MB.bin
```

This shows:
- download size
- transfer speed
- total time

---

## B) Network throughput using `iperf3`
Best for raw network throughput testing between two systems.

### Install
#### macOS
```bash
brew install iperf3
```

#### Ubuntu/Debian
```bash
sudo apt update && sudo apt install -y iperf3
```

#### RHEL/CentOS
```bash
sudo yum install -y iperf3
```

### Run server on one machine
```bash
iperf3 -s
```

### Run client on another machine
```bash
iperf3 -c <server-ip>
```

### Reverse direction
```bash
iperf3 -c <server-ip> -R
```

### Multiple streams
```bash
iperf3 -c <server-ip> -P 4
```

This gives:
- bandwidth / throughput
- retransmits
- sender/receiver performance

---

## 12) HTTP throughput + percentiles using benchmarking tools

For real API throughput and latency percentiles, use tools like:
- **wrk**
- **hey**
- **ab** (ApacheBench)
- **vegeta**

`wrk`, `hey`, and `vegeta` are more useful for modern testing.

---

## 13) Using `wrk` for latency and throughput

## Install
### macOS
```bash
brew install wrk
```

### Ubuntu/Debian
```bash
sudo apt update && sudo apt install -y wrk
```

### If not available
Build from source.

### Basic command
```bash
wrk -t4 -c100 -d30s https://example.com
```

Meaning:
- `-t4` → 4 threads
- `-c100` → 100 connections
- `-d30s` → run for 30 seconds

Typical output includes:
- requests/sec → throughput
- transfer/sec → data throughput
- avg latency
- stdev
- max latency

### With latency distribution
```bash
wrk -t4 -c100 -d30s --latency https://example.com
```

This gives percentile-style latency distribution.

Good for:
- throughput testing
- latency testing under concurrency

---

## 14) Using `hey` for p50, p95, p99

`hey` is simple and good for HTTP load testing.

## Install
### macOS
```bash
brew install hey
```

### Linux (Go required)
```bash
go install github.com/rakyll/hey@latest
```

Make sure Go bin is in PATH.

### Basic command
```bash
hey -n 1000 -c 50 https://example.com
```

Meaning:
- `-n 1000` → total 1000 requests
- `-c 50` → concurrency 50

It shows:
- total requests
- requests/sec → throughput
- fastest, slowest, average
- histogram
- latency distribution

This is one of the simplest ways to observe percentile-like results.

---

## 15) Using ApacheBench (`ab`)

## Install
### macOS
Usually available through Apache HTTP tools, or:
```bash
brew install httpd
```

### Ubuntu/Debian
```bash
sudo apt update && sudo apt install -y apache2-utils
```

### Run
```bash
ab -n 1000 -c 50 https://example.com/
```

Output includes:
- requests per second
- time per request
- transfer rate
- percentile table

Important percentile section may show something like:
- 50%
- 66%
- 75%
- 80%
- 90%
- 95%
- 98%
- 99%
- 100%

`ab` is older, but still useful for teaching.

---

## 16) Using `vegeta` for precise percentile analysis

## Install
### macOS
```bash
brew install vegeta
```

### Linux
Download binary from official release or install from source.

### Example
Create targets file:

```bash
echo "GET https://example.com/" > targets.txt
```

Run attack:

```bash
vegeta attack -duration=30s -rate=100 -targets=targets.txt > results.bin
```

Generate report:

```bash
vegeta report results.bin
```

Generate histogram:

```bash
vegeta report -type='hist[0,10ms,25ms,50ms,100ms,200ms,500ms,1s]' results.bin
```

This is excellent for:
- throughput
- latency distribution
- controlled rates
- repeatable load testing

---

## 17) Simple command to calculate p50, p95, p99, p999 from a file

Suppose `latency.txt` contains one latency value per line in seconds or milliseconds.

Example file:

```text
0.120
0.115
0.300
0.090
...
```

## Python command (works on Mac and Linux)

```bash
python3 - <<'PY'
import math

file_name = 'latency.txt'
with open(file_name) as f:
    vals = sorted(float(line.strip()) for line in f if line.strip())

if not vals:
    raise SystemExit('No values found')

def pct(data, p):
    idx = math.ceil((p/100) * len(data)) - 1
    idx = max(0, min(idx, len(data)-1))
    return data[idx]

for p in [50, 90, 95, 99, 99.9]:
    print(f'p{p}: {pct(vals, p)}')
PY
```

If your values are in seconds and you want milliseconds:

```bash
python3 - <<'PY'
import math

file_name = 'latency.txt'
with open(file_name) as f:
    vals = sorted(float(line.strip()) * 1000 for line in f if line.strip())

if not vals:
    raise SystemExit('No values found')

def pct(data, p):
    idx = math.ceil((p/100) * len(data)) - 1
    idx = max(0, min(idx, len(data)-1))
    return data[idx]

for p in [50, 90, 95, 99, 99.9]:
    print(f'p{p}: {pct(vals, p):.3f} ms')
PY
```

---

## 18) Collect latency using curl, then compute percentiles

### Step 1: Collect 1000 request latencies

```bash
for i in {1..1000}; do
  curl -o /dev/null -s -w '%{time_total}\n' https://example.com
 done > latency.txt
```

### Step 2: Calculate p50, p95, p99, p999

```bash
python3 - <<'PY'
import math

with open('latency.txt') as f:
    vals = sorted(float(x.strip()) * 1000 for x in f if x.strip())

def pct(a, p):
    i = math.ceil((p/100)*len(a)) - 1
    i = max(0, min(i, len(a)-1))
    return a[i]

print('samples:', len(vals))
print(f'p50  : {pct(vals, 50):.2f} ms')
print(f'p95  : {pct(vals, 95):.2f} ms')
print(f'p99  : {pct(vals, 99):.2f} ms')
print(f'p999 : {pct(vals, 99.9):.2f} ms')
print(f'min  : {min(vals):.2f} ms')
print(f'max  : {max(vals):.2f} ms')
print(f'avg  : {sum(vals)/len(vals):.2f} ms')
PY
```

---

## 19) Command to estimate throughput from total requests and total time

Basic formula:

```text
Throughput (RPS) = Total successful requests / Total time in seconds
```

Example:

```bash
python3 - <<'PY'
requests = 10000
time_seconds = 25
print('Throughput:', requests / time_seconds, 'requests/sec')
PY
```

But usually load tools already provide this directly.

Examples:
- `wrk` → Requests/sec
- `hey` → Requests/sec
- `ab` → Requests per second
- `iperf3` → bandwidth

---

## 20) Best practical commands

## For basic network latency
```bash
ping -c 20 google.com
```

## For HTTP timing breakdown
```bash
curl -o /dev/null -s -w 'dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s ttfb=%{time_starttransfer}s total=%{time_total}s\n' https://example.com
```

## For collecting many latency samples
```bash
for i in {1..1000}; do
  curl -o /dev/null -s -w '%{time_total}\n' https://example.com
 done > latency.txt
```

## For percentile calculation
```bash
python3 - <<'PY'
import math
with open('latency.txt') as f:
    vals = sorted(float(x.strip()) * 1000 for x in f if x.strip())
for p in [50,95,99,99.9]:
    idx = math.ceil((p/100)*len(vals)) - 1
    idx = max(0, min(idx, len(vals)-1))
    print(f'p{p}: {vals[idx]:.2f} ms')
PY
```

## For API throughput and latency distribution
```bash
wrk -t4 -c100 -d30s --latency https://example.com
```

## For simple request load test
```bash
hey -n 1000 -c 50 https://example.com
```

## For network throughput
```bash
iperf3 -c <server-ip>
```

---

## 21) How to interpret percentile numbers

Example result:

```text
p50  = 20 ms
p95  = 80 ms
p99  = 220 ms
p999 = 1200 ms
```

Interpretation:
- Most users are seeing very fast responses
- A small fraction sees noticeable slowness
- Rare requests are extremely slow
- The system has tail latency issues

Possible causes:
- GC pauses
- CPU contention
- disk I/O spikes
- database locks
- network retransmits
- retries/timeouts
- cold starts
- queue buildup

---

## 22) Common mistakes

1. **Looking only at average latency**
2. **Testing with too few samples**
3. **Ignoring concurrency effects**
4. **Ignoring warm-up/cold-start behavior**
5. **Mixing client-side and server-side metrics**
6. **Using ping to judge application performance**
7. **Not separating DNS/TLS/connect/app latency**

---

## 23) Recommended approach in real systems

1. Measure **end-to-end latency** from client side
2. Measure **server-side processing time**
3. Track **p50, p95, p99, p999**
4. Measure **throughput under different concurrency levels**
5. Monitor **CPU, memory, disk, network, queue depth** along with latency
6. Compare latency at:
   - idle load
   - normal load
   - peak load
   - overload

---

## 24) One-line summary

```text
Latency tells you how long one request takes.
Throughput tells you how many requests you can handle per second.
p50 shows typical latency.
p95/p99 show slow-request behavior.
p999 shows rare worst-case tail latency.
```

---

## 25) Quick cheat sheet

### Measure network latency
```bash
ping -c 20 host
```

### Measure HTTP breakdown
```bash
curl -o /dev/null -s -w 'dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s ttfb=%{time_starttransfer}s total=%{time_total}s\n' URL
```

### Save 1000 latency samples
```bash
for i in {1..1000}; do curl -o /dev/null -s -w '%{time_total}\n' URL; done > latency.txt
```

### Compute percentiles
```bash
python3 percentile.py
```

### Test API throughput + latency
```bash
wrk -t4 -c100 -d30s --latency URL
```

### Test simple HTTP load
```bash
hey -n 1000 -c 50 URL
```

### Test raw network throughput
```bash
iperf3 -c SERVER_IP
```

---

## 26) Suggested interview-style explanation

**Latency** is the time taken by one request to complete.
**Throughput** is how many such requests can be processed in a unit time.
**p50** is the median latency, **p95** and **p99** show the performance seen by slower requests, and **p999** captures rare tail events. In distributed systems, p99 and p999 are critical because a few slow dependencies can significantly affect end-to-end response time even when averages look healthy.

