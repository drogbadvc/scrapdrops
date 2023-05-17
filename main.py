import requests
from bs4 import BeautifulSoup
import shutil


def get_last_element_text(soup, css_class):
    elements = soup.find_all(class_=css_class)
    if elements:
        return elements[-1].get_text()
    return None


def download_audio(audio_src, file_path):
    response_audio = requests.get(audio_src, stream=True)
    if response_audio.status_code == 200:
        with open(file_path, "wb") as file:
            shutil.copyfileobj(response_audio.raw, file)
        print("Téléchargement terminé.")
    else:
        print("Impossible de télécharger le fichier audio.")


def scrape_translation(url):
    response = requests.get(url)

    if response.status_code != 200:
        print("La requête a échoué avec le code d'état", response.status_code)
        return

    soup = BeautifulSoup(response.content, "html.parser")

    last_sentence = get_last_element_text(soup, "particle-text")
    result = []

    if last_sentence:
        result.append(last_sentence)
    else:
        print("Aucun élément correspondant trouvé.")

    audio_tags = soup.find_all("audio")
    if audio_tags:
        audio_src = audio_tags[-1].get("src")
        if audio_src:
            file_name = f'audio/{result[0]}.mp3'
            download_audio(audio_src, file_name)
        else:
            print("Attribut 'src' non trouvé dans la balise 'audio'.")

    for container in soup.find_all(class_="fancy-language-container"):
        if container.get_text() == "French":
            next_div = container.find_next(class_="word-in-other-languages-word")
            if next_div:
                word_text = next_div.get_text()
                result.append(word_text)

    print(','.join(result))

    for word in soup.find_all(class_="topic-row-second-word"):
        topic_links = word.find_all(class_="topic-word-link")
        for link in topic_links:
            link_url = f"https://languagedrops.com{link['href']}"
            response_inner = requests.get(link_url)
            if response_inner.status_code != 200:
                print("La requête a échoué avec le code d'état", response_inner.status_code)
                continue

            inner_soup = BeautifulSoup(response_inner.content, "html.parser")

            last_sentence = get_last_element_text(inner_soup, "particle-text")
            result_inner = []

            if last_sentence:
                result_inner.append(last_sentence)
            else:
                print("Aucun élément correspondant trouvé.")

            audio_tags = inner_soup.find_all("audio")
            if audio_tags:
                audio_src = audio_tags[-1].get("src")
                if audio_src:
                    file_name = f'audio/{result_inner[0]}.mp3'
                    download_audio(audio_src, file_name)
                else:
                    print("Attribut 'src' non trouvé dans la balise 'audio'.")

            for container in inner_soup.find_all(class_="fancy-language-container"):
                if container.get_text() == "French":
                    next_div = container.find_next(class_="word-in-other-languages-word")
                    if next_div:
                        word_text = next_div.get_text()
                        result_inner.append(word_text)

            print(','.join(result_inner))


url = "https://languagedrops.com/word/en/english/korean/translate/at_the_airport/"
scrape_translation(url)
