# Storage Performance Benchmarking Guide

## Key Metrics

- **Latency**: Time per IO (µs/ms)
- **Throughput**: MB/s or GB/s
- **IOPS**: IO operations per second
- **Percentiles**: p50, p95, p99, p999
- **Queue Depth**: Parallel IO requests

---

## Tool 1: fio (Recommended)

### Install

```bash
# Mac
brew install fio

# Ubuntu
sudo apt install fio

# RHEL/CentOS
sudo yum install fio
```

---

## Sequential Throughput Test

```bash
fio --name=seqwrite     --rw=write     --bs=1M     --size=1G     --runtime=30     --time_based     --group_reporting
```

---

## Random IOPS + Latency

```bash
fio --name=randread     --rw=randread     --bs=4k     --iodepth=32     --numjobs=4     --size=1G     --runtime=30     --time_based     --group_reporting     --percentile_list=50,90,95,99,99.9
```

---

## JSON Output

```bash
fio ... --output-format=json --output=result.json
cat result.json | jq '.jobs[0].read.clat_ns.percentile'
```

---

## Tool 2: dd (Quick Throughput)

### Linux

```bash
dd if=/dev/zero of=testfile bs=1G count=1 oflag=direct
dd if=testfile of=/dev/null bs=1G iflag=direct
```

### Mac

```bash
dd if=/dev/zero of=testfile bs=1024k count=1024
```

---

## Tool 3: iostat

```bash
iostat -x 1
```

---

## Tool 4: dstat

```bash
dstat -d --disk-util
```

---

## Tool 5: hdparm

```bash
sudo hdparm -Tt /dev/sda
```

---

## Tool 6: blktrace

```bash
sudo blktrace -d /dev/sda -o - | blkparse -i -
```

---

## Manual Percentile Calculation

```bash
awk '{print $1}' latency.log | sort -n > sorted.txt

N=$(wc -l < sorted.txt)
IDX=$(echo "$N * 0.99" | bc | cut -d'.' -f1)

sed -n "${IDX}p" sorted.txt
```

---

## Why Percentiles Matter

- Average latency is misleading
- Tail latency (p99) defines system behavior
- Critical for DB, Kafka, Search systems

---

## Best Practice Workloads

| Use Case | Pattern |
|----------|--------|
| DB | 4k random |
| Logs | sequential write |
| Analytics | large sequential read |
| Mixed | randrw 70/30 |

---

## Advanced Mixed Workload

```bash
fio --name=mixed     --rw=randrw     --rwmixread=70     --bs=4k     --iodepth=64     --numjobs=8     --size=2G     --runtime=60     --time_based     --percentile_list=50,95,99,99.9
```
