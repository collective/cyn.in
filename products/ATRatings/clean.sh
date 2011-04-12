#!/bin/sh

#clean package
for i in `find . -name "*~"`; do rm $i; done
for i in `find . -name "*.pyc"`; do rm $i; done
for i in `find . -name "!*"`; do rm $i; done
for i in `find . -name "#*"`; do rm $i; done
for i in `find . -name "*.tmp"`; do rm $i; done
