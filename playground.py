#!/usr/bin/env python
# coding: utf-8

# In[2]:


# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = "all"


# In[3]:


# %pip install streamlit


# In[4]:


import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd

from PIL import Image
import colorsys
import csv
import os


# ---

# #### utilities 

# In[5]:


def generate_color_image(a, b, c, color_mode, size):
    # Convert HSL values to RGB values
    if color_mode == 'HSL':
        rgb = tuple(round(i * 255) for i in colorsys.hls_to_rgb(a, b, c))
    else:
        rgb = tuple(round(i * 255) for i in (a, b, c))
    
    # Create a new image witR the specified size and color
    image = Image.new('RGB', (int(size/1), int(size/1)), rgb)
    
    # Save the image as a PNG file
    # image.save('color.png', 'PNG')

    return image


# In[25]:


def clear_session():
    # Delete all the items in Session state
    for key in st.session_state.keys():
        del st.session_state[key]
    
    # Delete the colors.csv file if it exists
    try:
        os.remove('colors.csv')
    except:
        pass


# ---

# #### core logic

# In[24]:


def update_colors(colors, direction='Second'):
    global color_keys

    # update colors based only on the delta
    for key in color_keys:
        delta = (colors[key] - colors[key+'_prev'])
        if direction == 'Second':
            colors[key+'_a'] = max(colors[key+'_a']+delta*5, 1)
        else:
            colors[key+'_b'] = max(colors[key+'_b']+delta*2.5, 1)
        
    # save current colors into previous colors
    for key in color_keys:
        colors[key+'_prev'] = colors[key]

    # generate new colors from beta distribution
    for key in color_keys:
        colors[key] = np.random.beta(colors[key+'_a'], colors[key+'_b'])

    # check if colors.csv exists
    try:
        with open('colors.csv', 'r') as f:
            pass
    except FileNotFoundError:
        with open('colors.csv', 'w') as f:
            w = csv.DictWriter(f, colors.keys())
            w.writeheader()

    # save the colors to csv
    with open('colors.csv', 'a') as f:  # You will need 'wb' mode in Python 2.x
        w = csv.DictWriter(f, colors.keys())
        w.writerow(colors)


    # save everything in session state
    for key in color_keys:
        st.session_state[key] = colors[key]
        st.session_state[key+'_a'] = colors[key+'_a']
        st.session_state[key+'_b'] = colors[key+'_b']
        st.session_state[key+'_prev'] = colors[key+'_prev']
    
        


# In[ ]:





# ---

# #### streamlit wrappings

# In[ ]:


st.set_page_config(
    page_title="Color Mood",
    page_icon="🎨",
    # layout="wide",
)

st.markdown(f"""
    <style>
        .main .block-container{{
            padding-top: 1.5rem;
        }}
    </style>""",
    unsafe_allow_html=True,
)
st.title('Color of your :rainbow[Mood]')


# In[ ]:


# Initialization
color_schemes = {
    'RGB': ['R', 'G', 'B'],
    'HSL': ['H', 'S', 'L']
}

if 'color_mode' not in st.session_state:
    st.session_state['color_mode'] = 'RGB'
color_keys = color_schemes[st.session_state['color_mode']]

# color_keys = color_schemes['HSL']


colors = {}
delta = 0.1
# Intialize all, in all color schemes
for key in [value for _, vale in color_schemes.items() for value in vale]:
    if key not in st.session_state:
        st.session_state[key] = np.random.random()
        st.session_state[key+'_prev'] = np.random.random()
        st.session_state[key+'_a'] = 1
        st.session_state[key+'_b'] = 1

for key in [value for _, vale in color_schemes.items() for value in vale]:
    colors[key] = st.session_state[key]
    colors[key+'_prev'] = st.session_state[key+'_prev']
    colors[key+'_a'] = st.session_state[key+'_a']
    colors[key+'_b'] = st.session_state[key+'_b']

for key in color_keys:
    print("{}[a: {:.3f}, b: {:.3f}]".format(key, colors[key+'_a'], colors[key+'_b']), end=' ')
print()


# In[ ]:


st.write("Let's find your favourite color based on the mood you are in right now... ")

col1, col2 = st.columns([1, 1])
with col1:
    A, B, C = [colors[key+'_prev'] for key in color_keys]
    image = generate_color_image(A, B, C, st.session_state['color_mode'], 1024)
    st.image(
        image, 
        caption="[{:.2f}, {:.2f}, {:.2f}]".format(A, B, C),
        use_column_width="always",)
    st.button(
        "First",
        on_click=update_colors,
        args=(colors, 'First',),
        use_container_width=True,)

with col2:
    A, B, C = [colors[key] for key in color_keys]
    image = generate_color_image(A, B, C, st.session_state['color_mode'], 1024)
    st.image(
        image, 
        caption="[{:.2f}, {:.2f}, {:.2f}]".format(A, B, C),
        use_column_width="always",)
    st.button(
        "Second",
        on_click=update_colors,
        args=(colors, 'Second',),
        use_container_width=True,)
    
st.caption("Use arrow keys or click button to state which color you 'feel' more for")

with st.sidebar:
    color_key_index = st.radio(
        label = 'Color Scheme Mode', 
        options = ['RGB','HSL'],
        index = ['RGB','HSL'].index(st.session_state['color_mode']),
        horizontal=True,
    )

    color_keys = color_schemes[color_key_index]
    st.session_state['color_mode'] = color_key_index

    try:
        df = pd.read_csv('colors.csv')
        st.line_chart(df[color_keys])
    except:
        pass

    st.button(
        "Reset",
        on_click=clear_session,
        use_container_width=True,
    )


# In[ ]:


components.html(
    """
<script>
const doc = window.parent.document;
buttons = Array.from(doc.querySelectorAll('button[kind=secondary]'));
const First_button = buttons.find(el => el.innerText === 'First');
const Second_button = buttons.find(el => el.innerText === 'Second');
doc.addEventListener('keydown', function(e) {
    switch (e.keyCode) {
        case 37: // (37 = First arrow)
            First_button.click();
            break;
        case 39: // (39 = Second arrow)
            Second_button.click();
            break;
    }
});
</script>
""",
    height=0,
    width=0,
)


# In[ ]:





# In[ ]:




