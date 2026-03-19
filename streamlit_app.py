import streamlit as st
import cairosvg

import base64
import re
from pathlib import Path

IMAGE_STYLES = {
    'Stacked': 'EHRI_stacked_main-template.svg',
    'Stacked - limited space': 'EHRI_stacked_main_ls-template.svg',
    'Inline': 'EHRI_inline_main-template.svg',
    'Inline - limited space': 'EHRI_inline_main_ls-template.svg',
}

DEFAULT_COLOR = '#472c56'

COLORS = {
    'Default': DEFAULT_COLOR,
    'Block': '#ffffff',
    'Monochrome': '#000000',
    'Reverse': '#ffffff'
}

INSERT_COLORS = {
    'Default': '#7e6b89',
    'Block': '#ffffff',
    'Monochrome': '#ffffff',
    'Reverse': '#ffffff'
}

INSERT_COLORS_OPAQUE = {
    'Default': DEFAULT_COLOR,
    'Block': '#ffffff',
    'Monochrome': '#ffffff',
    'Reverse': '#ffffff'
}

BACKGROUND_COLORS = {
    'Default': '#ffffff',
    'Block': DEFAULT_COLOR,
    'Monochrome': '#ffffff',
    'Reverse': '#000000'
}

DEFAULT_TRANSPARENT_BACKGROUND = {
    'Default': True,
    'Block': False,
    'Monochrome': False,
    'Reverse': True
}

def pad_svg_viewbox(svg_str, pad_amount):
    """
    Expands the viewBox of an SVG string by a uniform integer amount.
    - Decreases min-x and min-y by pad_amount.
    - Increases width and height by 2 * pad_amount.
    """
    # 1. Find the viewBox attribute using a regex
    viewbox_pattern = r'viewBox\s*=\s*["\'](-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)["\']'
    match = re.search(viewbox_pattern, svg_str)

    if not match:
        return "Error: No viewBox found in SVG string."

    # 2. Extract current coordinates (x, y, width, height)
    x, y, w, h = map(float, match.groups())

    # 3. Calculate new padded coordinates
    new_x = x - pad_amount
    new_y = y - pad_amount
    new_w = w + (pad_amount * 2)
    new_h = h + (pad_amount * 2)

    # 4. Replace the old viewBox with the new one
    new_viewbox_str = f'viewBox="{new_x} {new_y} {new_w} {new_h}"'
    updated_svg = re.sub(viewbox_pattern, new_viewbox_str, svg_str)

    return updated_svg

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.title("EHRI Logo Generator")

    with st.sidebar as sidebar:

        image_style = st.selectbox("Choose an image style", IMAGE_STYLES.keys())

        logo_style = st.selectbox("Choose a colour style", COLORS.keys())

        TEMPLATE = Path(f'variants/base/{IMAGE_STYLES[image_style]}').read_text()

        primary_color = COLORS[logo_style]

        opaque_insert = st.checkbox("Opaque insert", value=True)

        transparent_background = st.checkbox("Transparent background", value=DEFAULT_TRANSPARENT_BACKGROUND[logo_style])

        border = st.number_input("Border size", min_value=0, max_value=100, step=1)

        opacity_level = 0.69 if logo_style in ['Default'] else 0.4

        insert_opacity = opacity_level if opaque_insert else 1

        insert_color = INSERT_COLORS_OPAQUE[logo_style] if opaque_insert else INSERT_COLORS[logo_style]

        background_opacity = 0.0 if transparent_background else 1.0

        background_color = BACKGROUND_COLORS[logo_style]

    edited = pad_svg_viewbox(TEMPLATE.replace('PRIMARY_COLOR', primary_color)\
        .replace('INSERT_COLOR', insert_color)\
        .replace('INSERT_OPACITY', str(insert_opacity))\
                 .replace('BG_COLOR', background_color)\
                 .replace('BG_OPACITY', str(background_opacity)), border)


    print(edited)

    b64 = base64.b64encode(edited.encode('utf-8')).decode("utf-8")

    background_css_class = 'checkerboard' if transparent_background else 'solid'

    background = f"""
            <div class="background {background_css_class}">
                <img src="data:image/svg+xml;base64,{b64}" />
            </div>
    """


    styles = f"""
        <style>
            .solid {{
                background-color: {BACKGROUND_COLORS.get(logo_style, 'none')};
            }}
            .checkerboard {{
              background-size: 10px 10px;
              background-position: 0 0, 5px 5px;
              background-image: 
                linear-gradient(45deg, #ccc 25%, transparent 25%, transparent 75%, #ccc 75%, #ccc 100%), 
                linear-gradient(45deg, #ccc 25%, white 25%, white 75%, #ccc 75%, #ccc 100%);
            }}

            .background {{
                display: flex;
                flex-direction: row;
                width: 350px;
                height: 250px;
                align-items: center;
                justify-content: center;
            }}
            img {{
                border-radius: 0 !important;
              background-size: 10px 10px;
              background-position: 0 0, 5px 5px;
              background-image: 
                linear-gradient(45deg, #ccc 25%, transparent 25%, transparent 75%, #ccc 75%, #ccc 100%), 
                linear-gradient(45deg, #ccc 25%, white 25%, white 75%, #ccc 75%, #ccc 100%);
            }}
            
            .background img {{
                width: 100%;
                height: auto;
                background-image: none;
            }}
            
        </style>
    """

    st.markdown(styles, unsafe_allow_html=True)
    st.markdown(background, unsafe_allow_html=True)

    st.markdown('---')

    st.markdown("### Export PNG")

    # User input for target width
    target_width = st.number_input("Target Width (px)", min_value=1, max_value=1920, value=1024)

    # Perform conversion with custom width
    # CairoSVG handles the 'auto' height for you
    png_data = cairosvg.svg2png(bytestring=edited, output_width=target_width)

    st.image(png_data, caption=f"Scaled to {target_width}px wide")

    st.download_button(
        label="Download Scaled PNG",
        data=png_data,
        file_name=f"scaled_{target_width}px.png",
        mime="image/png"
    )