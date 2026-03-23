import base64
from pathlib import Path

import cairosvg
import streamlit as st
from lxml import etree

IMAGE_STYLES = {
    'Stacked': 'EHRI_stacked_main-template.svg',
    'Stacked - limited space': 'EHRI_stacked_main_ls-template.svg',
    'Inline': 'EHRI_inline_main-template.svg',
    'Inline - limited space': 'EHRI_inline_main_ls-template.svg',
    'No Tagline': 'EHRI_no_tag-template.svg',
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

DEFAULT_SOLID_BACKGROUND = {
    'Default': False,
    'Block': True,
    'Monochrome': True,
    'Reverse': False
}


def get_base64_image(file):
    """Reads a file and returns its base64 string."""
    binary_data = file.getvalue()
    base64_data = base64.b64encode(binary_data).decode()
    return base64_data


def svg_update(svg_string, css_string, pad_amount):
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(svg_string.encode('utf-8'), parser)

    viewbox_raw = root.get("viewBox")
    if pad_amount > 0:
        if viewbox_raw:
            x, y, w, h = map(float, viewbox_raw.split())

            new_x, new_y = x - pad_amount, y - pad_amount
            new_w, new_h = w + (2 * pad_amount), h + (2 * pad_amount)

            root.set("viewBox", f"{new_x} {new_y} {new_w} {new_h}")
            width = float(root.get("width"))
            new_img_h = width * (new_h / new_w)
            root.set("height", str(new_img_h))

            # Find the element with ID 'rectbg' and set it's X and Y to negative
            # pad_amount
            rectbg = root.xpath(f"//*[@id='rectbg']")
            if rectbg:
                target = rectbg[0]
                target.set('x', '-50%')
                target.set('y', '-50%')
                target.set('width', '200%')
                target.set('height', '200%')

    # Find the element with ID 'style1' and set its CSS:
    style1 = root.xpath(f"//*[@id='style1']")
    if style1:
        # root.xpath always returns a list, so we take the first match
        target = style1[0]

        # 2. Replace the text content
        target.text = etree.CDATA(css_string)

    # 5. Convert back to string
    return etree.tostring(root, pretty_print=True, encoding='unicode')


if __name__ == "__main__":
    st.set_page_config(layout="wide", initial_sidebar_state=400, page_title="EHRI Logo Generator")

    with st.sidebar as sidebar:
        st.title("EHRI Logo Generator")

        image_style = st.selectbox("Choose an image style", IMAGE_STYLES.keys())
        logo_style = st.segmented_control("Choose a colour style", COLORS.keys(), default='Default')
        template = Path(f'variants/base/{IMAGE_STYLES[image_style]}').read_text()

        primary_color = COLORS[logo_style]
        opaque_insert = st.checkbox("Semi-opaque letter insert", value=True)
        solid_background = st.checkbox("Solid background", value=DEFAULT_SOLID_BACKGROUND[logo_style])
        border = st.number_input("Edge padding", min_value=0, max_value=100, step=1)
        opacity_level = 0.69 if logo_style in ['Default'] else 0.4
        insert_opacity = opacity_level if opaque_insert else 1
        insert_color = INSERT_COLORS_OPAQUE[logo_style] if opaque_insert else INSERT_COLORS[logo_style]
        background_opacity = 1.0 if solid_background else 0.0
        background_color = BACKGROUND_COLORS[logo_style]

    svg_css = f"""
        .cls-1 {{
            display:inline;
          fill:{primary_color};
          fill-opacity:1;
        }}
        .cls-2 {{
            fill:{insert_color};
          fill-opacity:1;
          opacity:{insert_opacity};
        }}
        .cls-bg {{
            fill:{background_color};
            fill-opacity:{background_opacity};
        }}
    """

    edited = svg_update(template, svg_css, border)

    # print(edited)
    st.markdown("#### SVG Preview")
    col1, col2 = st.columns([0.4, 0.6], gap=None)

    preview_background = col2.segmented_control("Preview background", ["Checkerboard", "Solid", "Image"],
                                                default="Checkerboard")
    preview_img = None
    if preview_background == "Image":
        preview_img = col2.file_uploader("Select a preview background image", ["png", "jpeg", "jpg"],
                                         max_upload_size=10)
    preview_color = None
    if preview_background == "Solid":
        preview_color = col2.color_picker("Select preview background colour", value=BACKGROUND_COLORS[logo_style])

    b64 = base64.b64encode(edited.encode('utf-8')).decode("utf-8")
    background_css_class = 'checkerboard'
    background = f"""
            <div class="background {background_css_class}">
                <img src="data:image/svg+xml;base64,{b64}" />
            </div>
    """
    styles = f"""
        <style>
            .checkerboard,
            img
             {{
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
            }}
            
            .background img {{
                width: 100%;
                height: auto;
                background-image: none;
            }}
            
        </style>
    """

    st.markdown(styles, unsafe_allow_html=True)

    if preview_img:
        bin_str = get_base64_image(preview_img)
        page_bg_img = f'''
            <style>
            .background {{
                background-image: url("data:image/png;base64,{bin_str}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            </style>
            '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    elif preview_color:
        page_bg_color = f"""
        <style>
        .background {{
            background-color: {preview_color};
            background-image: none;
        }}
        </style>
        """
        st.markdown(page_bg_color, unsafe_allow_html=True)

    col1.markdown(background, unsafe_allow_html=True)

    st.markdown('---')
    st.markdown("### Export PNG Image")

    export_col1, export_col2 = st.columns(2)

    target_width = export_col2.number_input("Target Width (px)", min_value=1, max_value=1920, value=1024)
    png_data = cairosvg.svg2png(bytestring=edited, output_width=target_width)
    export_col1.image(png_data, caption=f"Scaled to {target_width}px wide")

    export_col2.download_button(
        label="Download Scaled PNG",
        data=png_data,
        file_name=f"ehri-logo-{logo_style.lower()}-scaled_{target_width}px.png",
        mime="image/png"
    )

    export_col2.download_button(
        label="Download SVG",
        data=edited,
        file_name=f"ehri-logo-{logo_style.lower()}.svg",
        mime="image/svg+xml"
    )
