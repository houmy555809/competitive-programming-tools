#!/bin/bash

if ! [ -d $HOME/.cpt ]; then
    mkdir $HOME/.cpt
fi
cp -r $(pwd)/* $HOME/.cpt
mv $HOME/.cpt/main.py $HOME/.cpt/cpt

chmod a+x $HOME/.cpt/cpt $HOME/.cpt/judgers/*.py
cat >>$HOME/.bashrc <<-EOF
export PATH="$PATH:$HOME/.cpt"
EOF
source $HOME/.bashrc