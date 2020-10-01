#!/bin/sh

# Simple GUI using zenity, useful for nautilus integration

PIN=`zenity --entry --title="Enter your PIN" --text="PIN:" --hide-text`
RES=`pdf-sign.py $1 --pin="$PIN" 2>&1`

if [ $? -eq 0 ]
then
	DIALOG=--info
else
	DIALOG=--error
fi

zenity $DIALOG --title="pdf-sign" --text="$RES" --width=300
