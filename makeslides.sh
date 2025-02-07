#!/usr/bin/env bash

SLIDES_FILE="./min_example.py"
PRESENTATION_NAME="Presentation1"
HTML_NAME="slides.html"

manim -pql $SLIDES_FILE $PRESENTATION_NAME
#manim-slides convert $PRESENTATION_NAME $HTML_NAME --open
