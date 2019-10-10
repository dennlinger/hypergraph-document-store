#!/bin/bash
n_docs=(25000 50000 75000 100000 0)
port=(5433 5434 5435 5436 5437)
name=(test25000 test50000 test75000 test100000 testfull)
for n in `seq 0 4` ; do
  python3 CreateAllTables.py -n ${n_docs[n]} -r False -d True -v False -p ${port[n]} --name ${name[n]}
done;
