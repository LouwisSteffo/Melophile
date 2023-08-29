
#This is a song recommendation app where you will get songs as per your favourite genre
# I will give the code in the description section

import streamlit as st
st.set_page_config(page_title="Melophile", layout="wide" , page_icon="🎵")
import spotipy as sp
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import streamlit.components.v1 as components

@st.cache_data
def load_data():
    df = pd.read_csv("data/filtered_track_df.csv")
    df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
    exploded_track_df = df.explode("genres")
    return exploded_track_df

genre_names = ['Dance Pop', 'Electronic', 'Electropop', 'Hip Hop', 'Jazz', 'K-pop', 'Latin', 'Pop', 'Pop Rap', 'R&B', 'Rock']
audio_feats = ["acousticness", "danceability", "energy", "instrumentalness", "tempo"]

exploded_track_df = load_data()

def n_neighbors_uri_audio(genre, start_year, end_year, test_feat):
    genre = genre.lower()
    genre_data = exploded_track_df[(exploded_track_df["genres"]==genre) & (exploded_track_df["release_year"]>=start_year) & (exploded_track_df["release_year"]<=end_year)]
    genre_data = genre_data.sort_values(by='popularity', ascending=False)[:500]

    neigh = NearestNeighbors()
    neigh.fit(genre_data[audio_feats].to_numpy())

    n_neighbors = neigh.kneighbors([test_feat], n_neighbors=len(genre_data), return_distance=False)[0]

    uris = genre_data.iloc[n_neighbors]["uri"].tolist()
    audios = genre_data.iloc[n_neighbors][audio_feats].to_numpy()
    return uris, audios

def page():
    melophile_logo = "https://raw.githubusercontent.com/LouwisSteffo/AIWEB/main/Melophile.png"
    col1, mid, col2 = st.columns([1,1,20])
    with col1:
        st.image(melophile_logo, width=100)
    with col2:
        st.title('Melophile')
    
    title = "Melophile"

    st.write("Find Song You Want To Listen To By Entering Your Favourite Genre And Customizing The Features Of The Song You Want To Listen To And We Will Recommend You Songs Based On Your Input Features And Genre You Entered ") 
    st.markdown("##")
    
    user_input = st.sidebar.number_input("How many songs do you want to recommend?", min_value=1, max_value=20, value=4, step=1)

    with st.container():
        col1, col2,col3,col4 = st.columns((2,0.5,0.5,0.5))
        with col3:
            st.sidebar.markdown("***Choose your genre:***")
            genre = st.sidebar.radio(
                "",
                genre_names, index=genre_names.index("Pop"))
        with col1:
            st.markdown("***Choose features to customize:***")
            start_year, end_year = st.slider(
                'Select the year range',
                1990, 2019, (2015, 2019)
            )
            acousticness = st.slider(
                'Acousticness',
                0.0, 1.0, 0.5)
            danceability = st.slider(
                'Danceability',
                0.0, 1.0, 0.5)
            energy = st.slider(
                'Energy',
                0.0, 1.0, 0.5)
            instrumentalness = st.slider(
                'Instrumentalness',
                0.0, 1.0, 0.0)
            tempo = st.slider(
                'Tempo',
                0.0, 244.0, 118.0)

    tracks_per_page = user_input
    test_feat = [acousticness, danceability, energy, instrumentalness, tempo]
    uris, audios = n_neighbors_uri_audio(genre, start_year, end_year, test_feat)

    tracks = []
    for uri in uris:
        track = """<iframe src="https://open.spotify.com/embed/track/{}" width="260" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""".format(uri)
        tracks.append(track)

    if 'previous_inputs' not in st.session_state:
        st.session_state['previous_inputs'] = [genre, start_year, end_year] + test_feat
    
    current_inputs = [genre, start_year, end_year] + test_feat
    if current_inputs != st.session_state['previous_inputs']:
        if 'start_track_i' in st.session_state:
            st.session_state['start_track_i'] = 0
        st.session_state['previous_inputs'] = current_inputs

    if 'start_track_i' not in st.session_state:
        st.session_state['start_track_i'] = 0
    
    with st.container():
        col1, col2, col3 = st.columns([2,1,2])
        if st.button("Search For Another Song"):
            if st.session_state['start_track_i'] < len(tracks):
                st.session_state['start_track_i'] += tracks_per_page

        current_tracks = tracks[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
        current_audios = audios[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
        if st.session_state['start_track_i'] < len(tracks):
            for i, (track, audio) in enumerate(zip(current_tracks, current_audios)):
                if i%2==0:
                    with col1:
                        st.title("Song {}".format(i+1))
                        components.html(
                            track,
                            height=400,
                        )
                else:
                    with col3:
                        st.title("Song {}".format(i+1))
                        components.html(
                            track,
                            height=400,
                        )
        else:
            st.write("No songs left to recommend")
            
            
            
    hide_footer_style = """
    <style>
    .reportview-container .main footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_footer_style, unsafe_allow_html=True)

page()
