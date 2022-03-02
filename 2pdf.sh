#!/bin/bash

FILE=$1

a2ps --silent \
    --columns=1 \
    --rows=1 \
    --landscape \
    --chars-per-line=126 \
    --major=columns \
    -o /tmp/$FILE.ps $FILE

gs -sOutputFile=$FILE.pdf \
    -dNOPAUSE \
    -dBATCH \
    -g583x830 \
    -r72 \
    -sDEVICE=pdfwrite \
    -q  \
    -dSAFER /tmp/$FILE.ps

rm /tmp/$1.ps
rm $1
