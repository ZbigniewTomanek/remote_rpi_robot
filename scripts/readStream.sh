#!/bin/bash

F_NAME="fifo264"
PORT_NUM=5777

if [ -p $F_NAME ]
then
	rm $F_NAME
fi

mkfifo $F_NAME
nc -l -v -p $PORT_NUM > $F_NAME
