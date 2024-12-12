#!/bin/bash

export PATH=/usr/local/bin:$PATH

cd /Users/david/Documents 2> /dev/null

(jscli cmd.json -d | (wscli client tobias -p 9000 -s -t publisher_launcher 2> /dev/null > ws_fifo)) &
# wscli client tobias -p 9000 -s -t publisher_launcher 2> /dev/null > ws_fifo &

while true
do
	if read msg; then
		echo $msg

		if [ "$(echo $msg | jscli --get cmd | tr -d \")" == "run" ]
		then
			scenar=$(echo $msg | jscli --get scenar | tr -d \")
			/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --use-fake-device-for-media-stream --use-file-for-fake-video-capture=/Users/david/Documents/blue_sky_1080p25.y4m "https://medoozevm:8084/vm-publisher?autostart=true?scenar=$scenar" 2> /dev/null &
		fi

		if [ "$(echo $msg | jscli --get cmd | tr -d \")" == "stop" ]
		then
			pkill Google\ Chrome
		fi
	fi
done < ws_fifo
