#!/bin/bash
file=$1
outfile=${file%.*}.wav

ffmpeg -i $file -acodec pcm_s16le -ac 1 -ar 16000 $outfile
