#!/bin/bash
# usage: runq.sh  (reads queue.txt of json paths; appends "id dur" to done.txt)
cd "$(dirname "$0")"
worker(){ while true; do
  f=$(flock queue.lock bash -c 'f=$(head -n1 queue.txt); [ -n "$f" ] && sed -i 1d queue.txt; echo $f')
  [ -z "$f" ] && break
  if out=$(timeout 600 python3 video3.py "$f" 2>>err.log); then echo "$out" >> done.txt; else echo "$f" >> failed.txt; fi
done; }
worker & worker & wait
echo ALLDONE >> done.txt
