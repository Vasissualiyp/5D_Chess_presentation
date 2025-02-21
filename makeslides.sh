#!/usr/bin/env bash

SLIDES_FILE="./src/presentation1.py"
#PRESENTATION_NAME="PresentationSlides1_2"
#PRESENTATION_NAME="PresentationSlides_3"
PRESENTATION_NAME="PresentationSlides_4"
HTML_NAME="slides.html"

manim -ql $SLIDES_FILE $PRESENTATION_NAME #--disable_caching
manim-slides convert $PRESENTATION_NAME $HTML_NAME
