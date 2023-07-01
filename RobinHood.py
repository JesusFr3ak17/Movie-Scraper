import requests
from bs4 import BeautifulSoup
import streamlit as st
import re
from urllib.parse import urlparse
import time
import itertools
# Function to extract all movies from the search result
@st.cache_data
def extract_movies(search_term):
    all_movie_list = {}
    strip_search = str.lower(search_term[0])
    url = "https://newtoxic.com/TV_Series/" + strip_search + ".php"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    movie_present = False
    for link in soup.find_all('a'):
        href = link.get('href')
        text = link.get_text()
        if href and search_term.lower() in href.lower():
            all_movie_list[text] = href
        elif search_term.lower() in text.lower():
            all_movie_list[text] = href
            movie_present = href
    if movie_present == False:
        last_index = int(soup.find('ul', {'data-role': 'listview'}).find_all('a')[-1].text)
        other_pages = ["%.2d" % i for i in range(1, last_index)]
        for i in other_pages:
            url = "https://newtoxic.com/TV_Series/" + strip_search + i + ".php"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                text = link.get_text()
                if href and search_term.lower() in href.lower():
                    all_movie_list[text] = href
                    movie_present = True
                    break
                elif search_term.lower() in text.lower():
                    all_movie_list[text] = href
                    movie_present = True
                    break
            if movie_present == True:
                break
    return all_movie_list

# Function to get seasons for a movie
@st.cache_data
def get_seasons(url):
    response = requests.get(url)
    search_response = BeautifulSoup(response.text, 'html.parser')
    seasons = []
    for link in search_response.find('ul', {'data-role': 'listview'}).find_all('a'):
        href = link.get('href')
        text = link.get_text()
        if 'Season' in text:
            seasons.append((text, href))
    return seasons

@st.cache_data
def all_movies_nkiri(search_term):
    url = "https://nkiri.com/?s=" + str(search_term) + "&post_type=post"
    all_movie_list = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    primary_div = soup.find('div', {'id': 'primary', 'class': 'content-area clr'})
    secondary_div = soup.find_all('div', {'class': 'search-entry-inner clr'})
    for divs in secondary_div:
        image = divs.find('div', {'class': 'thumbnail'})
        src = image.find('img')
        src = src['src']
        #print(src)
        h2 = divs.find('h2', {'class': 'search-entry-title entry-title'})
        a_tag = h2.find('a')
        text = a_tag.text
        href = a_tag['href']
        all_movie_list[text] = (href, src)
    return all_movie_list

@st.cache_data
def all_episodes_nkiri(url):
    all_episodes = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    episode_details = []
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    elementor_button = soup.find_all('div', {'class': 'elementor-button-wrapper'})    
    for elements in elementor_button:
        download_link = elements.find('a')
        download_link = download_link['href']
        span = elements.find('span')
        span = span.text
        span = span.replace(" ", "").replace("\n", "").replace("\t", "").replace("'", "")
        file_name = download_link.split("/")[-1].replace(".html", "")
        if "howtodownload" not in str.lower(span) and "cantdownload?" not in str.lower(span):
            #print(str(movie_name))
                #print(file_name)
                #print(download_link)
                #print('\n\n')
            episode_details.append((file_name, download_link))
    all_episodes[file_name] = episode_details
                
    return all_episodes

# Streamlit app code
st.set_page_config(page_title="RobinHood 🗡️", page_icon="🗡️")

# Page Title
st.title("RobinHood 🗡️")

# Description
st.write("Stream hassle-free with RobinHood - Your one-click destination for movies")
with st.expander('What is RobinHood?'):
    st.markdown(f"<p>Step into the realm of <strong>RobinHood</strong>, the ultimate gathering place for movie enthusiasts. With just one click, you can unlock a treasure trove of the latest and greatest films from around the world. Whether you're in the mood for action, romance, comedy, or drama, <strong>RobinHood</strong> has got you covered. Say goodbye to endless browsing and frustrating downloads - with <strong>RobinHood</strong>, your movie experience is just a click away!</p><p>Developed by <strong>Oluwadolapo Salako</strong>, find me on <a href='https://linkedin.com/in/oluwadolapo-salako' target='_blank'>LinkedIn</a>.</p>", unsafe_allow_html=True)


# Search box

#select_vendor = st.radio('Select download source: ', ('ToxicWap', '02TV series', 'NetNaija', 'Nkiri'), index=0)
select_vendor = st.radio('Select download source: ', ('Nkiri', 'ToxicWap'), index=0)

if select_vendor == 'ToxicWap':
    search_term = st.text_input("Search for a movie")
    st.markdown(f"<p><i> To guarantee speed and efficient resource usage, search results are limited to just 5 (five).</i></p>", unsafe_allow_html=True)
# Search button
    if search_term:
        # Perform search and display results
        # Perform search and display results
        with st.spinner(f"Fetching results for '{search_term}' ... ") :
# Get all movies for the search term
            all_movies = extract_movies(search_term)
        st.success('Done')
        if all_movies:
            all_movies = {k: v for k, v in all_movies.items() if k != '' and k != 'Next' and not k.isdigit()}
            all_movies = {k: v for k, v in itertools.islice(all_movies.items(), 5)}
            # Display all movies as buttons with their image and seasons
            for title, url in all_movies.items():
                season_url = url
                parsed_url = urlparse(season_url)
                site_name = parsed_url.hostname
                st.markdown(f"## {title}")
                # Get the image for the movie
                image_url = f"https://ratedwap.com/cms/sub_thumb/{title}.jpg"
                try:
                    image_response = requests.get(image_url)
                    image_bytes = image_response.content
                    st.image(image_bytes, use_column_width=True)
                except:
                    st.write("Image not available")

                # Get the seasons for the movie
                seasons = get_seasons(url)
                if len(seasons) == 0:
                    st.write('No season available')
                else:
                    for season in seasons:
                        with st.expander(f"Season {season[0]}"):
                            if st.button(f"Download {season[0]}", key=f"{title}-season-{season[0]}", use_container_width=True):
                            # Perform download logic for the season
                                st.write(f"{title} {season[0]} is selected.")  
                                urls = season[1]
                                new = 'https://' + str(site_name) + urls
                                season_explore = requests.get(new)
                                search_response = BeautifulSoup(season_explore.text, 'html.parser')
                                all_episodes = []
                                #all_episodes_with_download = []
                                #print(search_response)
                                try:
                                    for link in search_response.find('ul', {'data-role': 'listview'}).find_all('a'):
                                        href = link.get('href')
                                        text = link.get_text()
                                        season_download = 'https://' + str(site_name) + href
                                        episode_download = requests.get(season_download)
                                        episode_response = BeautifulSoup(episode_download.text, 'html.parser')
                                        a_tag = episode_response.find('a', text='Download')
                                        href = a_tag.get('href')
                                        download_link = 'https://' + str(site_name) + href
                                        all_episodes.append((text, download_link))
                                except:
                                    st.write('Movie Not Available')
                                    print(search_response)
                                    break
                                try:
                                    a_elements = search_response.find_all('a')
                                    numbers = [int(a.get_text()) for a in a_elements if a.get_text().isdigit()]
                                    # Find the highest number
                                    highest_number = max(numbers)
                                    all_elements = []
                                    for link in search_response.find_all('a'):
                                        if link.text.isdigit():
                                            all_elements.append(link.get('href'))
                                    for i in range(1, highest_number):
                                        url = 'https://' + str(site_name) + all_elements[i]
                                        response = requests.get(url)
                                        other_pages = BeautifulSoup(response.text, 'html.parser')
                                        for link in other_pages.find('ul', {'data-role': 'listview'}).find_all('a'):
                                            href = link.get('href')
                                            text = link.get_text()
                                            season_download = 'https://' + str(site_name) + href
                                            all_episodes.append((text, season_download))
                                except: 
                                    pass

        # Display the episodes only when the button is clicked
                                for episode in all_episodes:
                                    episode_name = episode[0]
                                    episode_link = episode[1]
                                    episode_response = requests.get(episode_link)
                                    episode_soup = BeautifulSoup(episode_response.text, 'html.parser')
                                    episode_download_links = episode_soup.find_all('a', string='Download')
                                    if episode_download_links:
                                        episode_href = episode_download_links[0]['href']
                                        episode_href = 'https://' + str(site_name) + episode_href
                                        episode_html = f'<a href="{episode_href}">{episode_name}</a>'
                                        st.markdown(episode_html, unsafe_allow_html=True)
                                    else:
                                        episode_html = f'<a href="{episode_link}">{episode_name}</a>'
                                        st.markdown(episode_html, unsafe_allow_html=True)


                # Display message if there are no search results
        if not all_movies:
            st.write("No movies found for the search term.")
elif select_vendor == 'Nkiri':
    search_term = st.text_input("Search for a movie")
    st.markdown(f"<p><i> To guarantee speed and efficient resource usage, search results are limited to just 5 (five).</i></p>", unsafe_allow_html=True)
# Search button
    if search_term:
        # Perform search and display results
        # Perform search and display results
        st.write(f"Search results for '{search_term}':")
# Get all movies for the search term
        all_movies = all_movies_nkiri(search_term)
        all_movies = {k: v for k, v in itertools.islice(all_movies.items(), 5)}
        if all_movies:
            # Display all movies as buttons with their image and seasons
            for title, details in all_movies.items():
                st.markdown(f"## {title}")
                # Get the image for the movie
                try:
                    image_response = requests.get(details[1])
                    image_bytes = image_response.content
                    st.image(image_bytes, use_column_width=True)
                except:
                    st.write("Image not available")

                # Get the seasons for the movie
                all_files = all_episodes_nkiri(details[0])
                if len(all_files) == 0:
                    st.write('No movies available')
                else:
                    for movie, link_tuple in all_files.items():
                        with st.expander(f"{title}"):
                            if st.button(f"Generate Download Link", key=f"{title}", use_container_width=True):
                            # Perform download logic for the season
                                for all_links in link_tuple:
                                    episode_html = f'<a href="{all_links[1]}">{all_links[0]}</a>'
                                    st.markdown(episode_html, unsafe_allow_html=True)


                # Display message if there are no search results
else:
    with st.spinner(text="Development in progress, use ToxicWap ... "):
        time.sleep(10000)
