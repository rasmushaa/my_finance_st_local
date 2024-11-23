import streamlit as st
import random



def valid_user_state():
    if 'user' not in st.session_state:
        st.switch_page('frontend/account/login.py')
    if not st.session_state['user'].is_logged_in():
        st.switch_page('frontend/account/login.py')


def validate_captcha_color(user_rgb, target_rgb, draw_new_color_if_failed):
    for user_value, target_value in zip(user_rgb, target_rgb):
        if target_value == 0:
            if user_value > 100:
                init_random_captcha_color(draw_new_color=draw_new_color_if_failed)
                st.rerun()
        elif target_value == 255:
            if user_value < 155:
                init_random_captcha_color(draw_new_color=draw_new_color_if_failed)
                st.rerun()


def init_random_captcha_color(draw_new_color: bool = False):
    if 'random_color' not in st.session_state:
        st.session_state['random_color'] = None
        draw_new_color = True # Force the new color in the first run

    possible_colors = {
        'Red': (255, 0, 0),
        'Green': (0, 255, 0),
        'Blue': (0, 0, 255),
        'Yellow': (255, 255, 0),
        'Magenta': (255, 0, 255),
        'Cyan': (0, 255, 255)
    }

    if draw_new_color:
        st.session_state['random_color'] = random.choice(list(possible_colors .items()))
        return st.session_state['random_color']
    else:
        return st.session_state['random_color']