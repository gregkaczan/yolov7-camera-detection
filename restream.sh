#!/bin/sh
ffmpeg  \
-i rtsp://u:p@192.168.1.2:554 \
-f lavfi -i anullsrc  \
-filter_complex  \
" [0:v] setpts=PTS-STARTPTS,setsar=1[upperleft]; \
  [1:v] setpts=PTS-STARTPTS,setsar=1[upperright];  \
  [2:v] setpts=PTS-STARTPTS,setsar=1[lowerright];  \
  [3:v] setpts=PTS-STARTPTS,setsar=1[lowerleft];  \
  [upperleft][upperright]hstack[a];[lowerright][lowerleft]hstack[b];[a][b]vstack[base]"  \
-map [base]  \
-map 2 -f rtsp rtsp://localhost:8554/mystream
