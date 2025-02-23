#!/usr/bin/env bash

SLIDES_FILE="./src/presentation1.py"
#PRESENTATION_NAME="PresentationSlides1_2"
#PRESENTATION_NAME="PresentationSlides_3"
PRESENTATION_NAME="PresentationSlides_4"
HTML_NAME="slides.html"

manim -ql --verbosity DEBUG $SLIDES_FILE $PRESENTATION_NAME 1&>manim_log.out 2&>manim_log.err #--disable_caching
manim-slides convert --verbosity DEBUG $PRESENTATION_NAME $HTML_NAME 1&>>manim_log.out 2&>>manim_log.err  
