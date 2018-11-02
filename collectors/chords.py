from bs4 import BeautifulSoup
import requests
import utils


class ChordCollector:
    def __init__(self, config):
        self._base_uri = config["base_uri"]

    def _get_html(self, url, params=None, headers=None):
        response = requests.get(url=url, params=params, headers=headers)
        response.raise_for_status()
        return response.content

    def _format(self, str):
        words = utils.simplify_str(str).split(" ")
        return "-".join(words)

    def collect(self, artist_name, song_name):
        url = self._base_uri.format(self._format(artist_name),
                                    self._format(song_name))
        html_content = self._get_html(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        return [chord.text for chord in soup.select('#core u')]
