#!/bin/bash

for i in $(seq 1 5)
do
    for viewer in $(echo 10 45 70)
    do
	for j in $(echo balloning-viewersburst$viewer-thresh400-increase0 balloning-viewersburst$viewer-thresh200-increase0 balloning-viewersburst$viewer-thresh50-increase0)
	do
	    # ls $j ballooning-lowthresh-viewers$viewer*
	    mv ballooning-lowthresh-viewers$viewer*/$(ls -1 ballooning-lowthresh-viewers$viewer* | head -n1) $j
	done
    done
done
