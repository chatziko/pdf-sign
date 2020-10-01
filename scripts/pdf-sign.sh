#!/bin/sh

# Simple GUI using zenity, useful for nautilus integration

PIN=`zenity --entry --title="Enter your PIN" --text="PIN:" --hide-text`
RES=`pdf-sign.py $1 --pin="$PIN"`

zenity --info --title="pdf-sign" --text="$RES"
