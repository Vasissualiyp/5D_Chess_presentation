#!/usr/bin/env bash
SCENE_NAME="MultipleChessBoards"
PY_NAME="manim_base"
RES="1080p60"
watchexec -w src/${PY_NAME}.py \
    "clear; manim ./src/${PY_NAME}.py ${SCENE_NAME}; \
    hyprctl dispatch workspace 2; \
	hyprctl keyword animations:enabled 0; \
    pkill mpv; \
    mpv media/videos/${PY_NAME}/${RES}/${SCENE_NAME}.mp4 --loop &"
