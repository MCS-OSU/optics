#!/bin/bash

if [[ $1 == yes ]] ||  [[ $1 == no ]];then
    echo "it was yes or no"
elif  [[ $1 == yep ]]; then
    echo "too casual - exiting"
    exit 1
else
    echo "was something different"
fi
echo "final line here"
