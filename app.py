import os
import glob
import json
from pytube import YouTube
import streamlit as st
from yt.yt_manager import (
    get_authenticated_service,
    get_my_channel_details,
    upload_yt_video,
    category_dict,
)

from urllib.parse import urlparse
from style import css
from llm import YouTubeAssistant


# Constants for file paths
CHANNELS_PATH = "channels"
CHANNELS_JSON_PATH = "channels.json"
VIDEOS_PATH = "./videos"


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


# Function to get authorized channels
def get_channels():
    files = os.listdir(CHANNELS_PATH)
    channels = [
        file.replace("-oauth2.json", "")
        for file in files
        if file.endswith("-oauth2.json")
    ]
    return channels


# Functions to handle channels data
def write_channel_data(channel_name, channel_details):
    channels = get_all_channels()
    channels[channel_name] = channel_details
    with open(CHANNELS_JSON_PATH, "w") as file:
        json.dump(channels, file)


def get_all_channels():
    try:
        with open(CHANNELS_JSON_PATH, "r") as file:
            channels = json.load(file)
        return channels
    except FileNotFoundError:
        return {}


def get_channel_data(channel_name):
    channels = get_all_channels()
    return channels.get(channel_name, None)


def update_channel_data(channel_name):
    channel = fetch_channel_details(channel_name, refresh=True)
    if channel:
        channel_details = {
            "thumbnail": channel.snippet.thumbnails.high.url,
            "title": channel.snippet.title,
            "subs": channel.statistics.subscriberCount,
            "views": channel.statistics.viewCount,
            "video": channel.statistics.videoCount,
            "description": channel.snippet.description,
        }
        write_channel_data(channel_name, channel_details)
        st.sidebar.success("Refreshed, please reload the page!", icon="✅")


# Function to fetch channel details
def fetch_channel_details(channel_name, refresh=False):
    if refresh:
        youtube = get_authenticated_service(channel_name)
        if youtube:
            return get_my_channel_details(youtube)
    else:
        return get_channel_data(channel_name)


# Function to display specific information
def display_info(label, value, placeholder, cols=[1, 3]):
    col1, col2 = placeholder.columns(cols)
    col1.subheader(label)
    col2.subheader(value)


# Function to display channel information
def display_channel_info(channel, placeholders):
    placeholders[0].image(channel["thumbnail"], width=150)
    display_info("Name:", channel["title"], placeholders[1])
    display_info("Subs:", channel["subs"], placeholders[2])
    display_info("Video:", channel["video"], placeholders[3])
    display_info("Views:", channel["views"], placeholders[4])
    display_info("Desc:", channel["description"], placeholders[5])


# Function to manage channel
def manage_channel():
    st.sidebar.divider()
    clm1, clm2 = st.sidebar.columns(2)
    with clm1:
        refresh = st.button(label="Refresh", use_container_width=True)
        if refresh:
            update_channel_data(st.session_state.current_channel)
    with clm2:
        remove = st.button(label="Remove", type="primary", use_container_width=True)
        if remove:
            pass
    st.sidebar.divider()


# Function to authorize new channel
def authorize_channel():
    channel_name = st.sidebar.text_input(
        label="Channel Temp Name",
        placeholder="Channel temp name..",
        label_visibility="hidden",
    )
    auth_btn = st.sidebar.button("Add", use_container_width=True)
    if auth_btn:
        if channel_name:
            update_channel_data(channel_name)


# Function to download video from URL
def download_video(video_url):
    with st.spinner("Downloading video..."):
        try:
            files = glob.glob(f"{VIDEOS_PATH}/*")
            for f in files:
                os.remove(f)
            yt = YouTube(video_url)
            stream = yt.streams.get_highest_resolution()
            stream.download(output_path=VIDEOS_PATH)

            video_details = {
                "Title": yt.title,
                "Description": yt.description,
                "Length": yt.length,
                "Thumbnail": yt.thumbnail_url,
                "Views": yt.views,
                "Rating": yt.rating,
            }
            print(video_details)
            return yt, f"{VIDEOS_PATH}/{stream.default_filename}", video_details
        except Exception as e:
            st.error(f"Error downloading video: {e}")
            return None, None, None


def display_video_details(assistant, yt):
    if yt is not None:
        video_details = st.session_state["video_details"]

        if "title" not in st.session_state:
            st.session_state.title = video_details.get("Title", "")
        else:
            st.session_state.title = video_details.get("Title", "")
        if "description" not in st.session_state:
            st.session_state.description = video_details.get("Description", "")
        else:
            st.session_state.description = video_details.get("Description", "")
        if "tags" not in st.session_state:
            st.session_state.tags = ""
        else:
            st.session_state.tags = ""

        col1, col2 = st.columns([3, 1])
        video_title = col1.text_input(
            "Enter video title",
            placeholder="Enter video title",
            value=st.session_state.title,
            label_visibility="collapsed",
        )
        title_gen = col2.button("Generate Title", use_container_width=True)

        if title_gen:
            st.session_state.title = assistant.generate_title(video_title)
            st.experimental_rerun()

        col1, col2 = st.columns([3, 1])
        video_description = col1.text_area(
            "Enter video description",
            placeholder="Enter video description",
            value=st.session_state.description,
            label_visibility="collapsed",
        )
        desc_gen = col2.button("Generate Description", use_container_width=True)

        if desc_gen:
            st.session_state.description = assistant.generate_description(
                video_description
            )
            st.experimental_rerun()

        cl1, cl2 = st.columns([3, 1])
        video_tags = cl1.text_input(
            "Enter video tags",
            placeholder="Enter video tags",
            value=st.session_state.tags,
            label_visibility="collapsed",
        )
        tags_gen = cl2.button("Generate Tags", use_container_width=True)

        if tags_gen:
            st.session_state.tags = assistant.generate_tags(
                video_tags, st.session_state["category"]
            )
            st.experimental_rerun()

        with st.form(key="upload_video"):
            upload_button = st.form_submit_button(
                "Upload", use_container_width=True, type="primary"
            )

        return upload_button
    return None


# Function to handle video upload
def upload_video(upload_button):
    if upload_button:
        with st.spinner("Uploading.."):
            current_channel = st.session_state["current_channel"]
            selected_category = st.session_state["category"]
            category_id = category_dict[selected_category]
            video_file = st.session_state["video_file"]
            title = st.session_state["new_title"]
            desc = st.session_state["new_desc"]
            tags = st.session_state["new_tags"].split(",")

            youtube = get_authenticated_service(current_channel)
            status, msg = upload_yt_video(
                youtube, video_file, title, desc, tags, category_id
            )
            if status == "success":
                st.balloons()
                st.success(msg, icon="✅")
            else:
                st.warning(msg, icon="⚠️")


def main():
    if "video_url" not in st.session_state:
        st.session_state["video_url"] = None
    if "video_file" not in st.session_state:
        st.session_state["video_file"] = None
    if "yt" not in st.session_state:
        st.session_state["yt"] = None
    if "video_details" not in st.session_state:
        st.session_state["video_details"] = None
    if "api_key" not in st.session_state:
        st.session_state[
            "api_key"
        ] = "openai api key here"
    if "input_label" not in st.session_state:
        st.session_state["input_label"] = "Enter youtube video url 👇"
    if "input_placeholder" not in st.session_state:
        st.session_state["input_placeholder"] = "video url.."

    assistant = YouTubeAssistant(st.session_state["api_key"])

    apptitle = "Youtube Automation"
    st.set_page_config(page_title=apptitle, page_icon=":red_circle:")
    st.title("Youtube Bot")
    style_markdown = st.sidebar.markdown(css, unsafe_allow_html=True)

    platform = st.radio(
        "Platform",
        ("Youtube", "Instagram"),
        index=1,
        key="platform",
        label_visibility="collapsed",
        horizontal=True,
    )
    if platform == "Instagram":
        st.session_state["input_label"] = "Enter instagram username 👇"
        st.session_state["input_placeholder"] = "username.."
    else:
        st.session_state["input_label"] = "Enter youtube video url 👇"
        st.session_state["input_placeholder"] = "video url.."

    col1, col2 = st.columns([3.5, 0.5])
    video_url = col1.text_input(
        st.session_state["input_label"],
        placeholder=st.session_state["input_placeholder"],
    )
    submit_url = col2.button("Submit", key="Submit", use_container_width=True)

    if submit_url:
        if video_url == None or video_url == "":
            st.error("Video url or username is not provided!")
        elif platform == "Youtube" and video_url:
            # Save the video URL in the session state when the submit button is clicked
            st.session_state["video_url"] = video_url

            # Download video
            yt, video_path, video_details = download_video(
                st.session_state["video_url"]
            )

            st.session_state["video_file"] = video_path
            st.session_state["video_details"] = video_details
            st.session_state["yt"] = yt
        elif platform == "Instagram" and video_url:
            if is_valid_url(video_url):
                st.error("It is not valid instagram username!")
            else:
                pass

    # Display the video
    if st.session_state["video_file"]:
        st.video(st.session_state["video_file"])

    # Display inputs for video details with default values
    upload_button = display_video_details(assistant, st.session_state["yt"])

    # Handle video upload
    upload_video(upload_button)

    # Get list of authorized channels and create select box
    authorized_channels = get_channels()
    if authorized_channels:
        current_channel = st.sidebar.selectbox(
            "Authorized Channels",
            tuple(authorized_channels),
            key="current_channel",
        )
        channel = fetch_channel_details(st.session_state.current_channel)
        if channel:
            placeholders = [st.sidebar.empty() for _ in range(6)]
            display_channel_info(channel, placeholders)

        # Channel management
        manage_channel()

    # Authorize a new channel
    authorize_channel()

    # Category
    default_index = list(category_dict.keys()).index("Sports")
    selected_category = st.sidebar.selectbox(
        "Select a Category",
        options=list(category_dict.keys()),
        index=default_index,
        key="category",
    )

    # API Key input
    st.sidebar.text_input(
        label="Api Key",
        placeholder="OpenAI key",
        type="password",
        label_visibility="hidden",
        value=st.session_state["api_key"],
    )


if __name__ == "__main__":
    main()
