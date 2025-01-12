#!/usr/bin/env bash
SCENE_NAME="MultipleChessBoards"
PY_NAME="manim_base"
PY_LOC="./src/${PY_NAME}.py"
WATCHFLAG=0

get_value() {
	# Get value of a certain parameter form the python manim code
	grep "$1" "$PY_LOC" | awk -F'=' '{print $2}' | sed 's/ //'
}

HEIGHT=$(get_value "pixel_height")
FPS=$(get_value "frame_rate")
RES="${HEIGHT}p${FPS}"

MANIM_COMMAND="manim ./src/${PY_NAME}.py ${SCENE_NAME} --disable_caching"

if [[ $WATCHFLAG -eq 1 ]]; then
    watchexec -w src/${PY_NAME}.py \
        "clear; ${MANIM_COMMAND} \
        hyprctl dispatch workspace 2; \
    	hyprctl keyword animations:enabled 0; \
        pkill mpv; \
        mpv media/videos/${PY_NAME}/${RES}/${SCENE_NAME}.mp4 --loop &"
else 
        clear; ${MANIM_COMMAND} 
        pkill mpv; 
        mpv media/videos/${PY_NAME}/${RES}/${SCENE_NAME}.mp4 --loop &
fi
