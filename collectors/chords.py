from bs4 import BeautifulSoup
import operator
import requests
import utils
import json
import re

major_distances = [
    ('A'), ('A#', 'Bb'), ('B'), ('C'), ('C#', 'Db'), ('D'), ('D#', 'Eb'),
    ('E'), ('F'), ('F#', 'Gb'), ('G'), ('G#', 'Ab')
]

minor_distances = [
    ('F#m', 'Gbm'), ('Gm'), ('G#m', 'Abm'), ('Am'), ('Bbm', 'A#m'), ('Bm'),
    ('Cm'), ('C#m', 'Dbm'), ('Dm'), ('D#m', 'Ebm'), ('Em'), ('Fm')
]

flat_to_sharp = {
    "D": "C", "E": "D", "G": "F", "A": "G", "B": "A"
}

keys = {
  "C": ["C", "Cmaj7", "Dm", "Dm7", "Em", "Em7", "F", "Fmaj7", "G", "G7", "Am", "Am7", "Bdim"],
  "C#": ["C#", "C#maj7", "D#m", "D#m7", "E#m", "E#m7", "F#", "F#maj7", "G#", "G#7", "A#m", "A#m7", "B#dim"],
  "Db": ["Db", "Dbmaj7", "Ebm", "Ebm7", "Fm", "Fm7", "Gb", "Gbmaj7", "Ab", "Ab7", "Bbm", "Bbm7", "Cdim"],
  "D": ["D", "Dmaj7", "Em", "Em7", "F#m", "F#m7", "G", "Gmaj7", "A", "A7", "Bm", "Bm7", "C#dim"],
  "D#": ["D#", "D#maj7", "E#m", "E#m7", "F##m", "F##m7", "G#", "G#maj7", "A#", "A#7", "B#m", "B#m7", "C##dim"],
  "Eb": ["Eb", "Ebmaj7", "Fm", "Fm7", "Gm", "Gm7", "Ab", "Abmaj7", "Bb", "Bb7", "Cm", "Cm7", "Ddim"],
  "E": ["E", "Emaj7", "F#m", "F#m7", "G#m", "G#m7", "A", "Amaj7", "B", "B7", "C#m", "C#m7", "D#dim"],
  "F": ["F", "Fmaj7", "Gm", "Gm7", "Am", "Am7", "Bb", "Bbmaj7", "C", "C7", "Dm", "Dm7", "Edim"],
  "F#": ["F#", "F#maj7", "G#m", "G#m7", "A#m", "A#m7", "B", "Bmaj7", "C#", "C#7", "D#m", "D#m7", "E#dim"],
  "Gb": ["Gb", "Gbmaj7", "Abm", "Abm7", "Bbm", "Bbm7", "Cb", "Cbmaj7", "Db", "Db7", "Ebm", "Ebm7", "Fdim"],
  "G": ["G", "Gmaj7", "Am", "Am7", "Bm", "Bm7", "C", "Cmaj7", "D", "D7", "Em", "Em7", "F#dim"],
  "G#": ["G#", "G#maj7", "A#m", "A#m7", "B#m", "B#m7", "C#", "C#maj7", "D#", "D#7", "E#m", "E#m7", "F##dim"],
  "Ab": ["Ab", "Abmaj7", "Bbm", "Bbm7", "Cm", "Cm7", "Db", "Dbmaj7", "Eb", "Eb7", "Fm", "Fm7", "Gdim"],
  "A": ["A", "Amaj7", "Bm", "Bm7", "C#m", "C#m7", "D", "Dmaj7", "E", "E7", "F#m", "F#m7", "G#dim"],
  "A#": ["A#", "A#maj7", "B#m", "B#m7", "C##m", "C##m7", "D#", "D#maj7", "E#", "E#7", "F##m", "F##m7", "G##dim"],
  "Bb": ["Bb", "Bbmaj7", "Cm", "Cm7", "Dm", "Dm7", "Eb", "Ebmaj7", "F", "F7", "Gm", "Gm7", "Adim"],
  "B": ["B", "Bmaj7", "C#m", "C#m7", "D#m", "D#m7", "E", "Emaj7", "F#", "F#7", "G#m", "G#m7", "A#dim"],
  "Cm": ["Eb", "Ebmaj7", "Fm", "Fm7", "Gm", "Gm7", "G", "G7", "Ab", "Abmaj7", "Bb", "Bb7", "Cm", "Cm7", "Ddim"],
  "Gm": ["Bb", "Bbmaj7", "Cm", "Cm7", "Dm", "Dm7", "D", "D7", "Eb", "Ebmaj7", "F", "F7", "Gm", "Gm7", "Adim"],
  "Dm": ["F", "Fmaj7", "Gm", "Gm7", "Am", "Am7", "A", "A7", "Bb", "Bbmaj7", "C", "C7", "Dm", "Dm7", "Edim"],
  "Am": ["C", "Cmaj7", "Dm", "Dm7", "Em", "Em7", "E", "E7", "F", "Fmaj7", "G", "G7", "Am", "Am7", "Bdim"],
  "Em": ["G", "Gmaj7", "Am", "Am7", "Bm", "Bm7", "B", "B7", "C", "Cmaj7", "D", "D7", "Em", "Em7", "F#dim"],
  "Bm": ["D", "Dmaj7", "Em", "Em7", "F#m", "F#m7", "F#", "F#7", "G", "Gmaj7", "A", "A7", "Bm", "Bm7", "C#dim"],
  "F#m": ["A", "Amaj7", "Bm", "Bm7", "C#m", "C#m7", "C#", "C#7", "D", "Dmaj7", "E", "E7", "F#m", "F#m7", "G#dim"],
  "C#m": ["E", "Emaj7", "F#m", "F#m7", "G#m", "G#m7", "G#", "G#7", "A", "Amaj7", "B", "B7", "C#m", "C#m7", "D#dim"],
  "Dbm": ["E", "Emaj7", "F#m", "F#m7", "G#m", "G#m7", "G#", "G#7", "A", "Amaj7", "B", "B7", "C#m", "C#m7", "D#dim"],
  "Abm": ["B", "Bmaj7", "C#m", "C#m7", "D#m", "D#m7", "D#", "D#7", "E", "Emaj7", "F#", "F#7", "G#m", "G#m7", "A#dim"],
  "Ebm": ["Gb", "Gbmaj7", "Abm", "Abm7", "Bbm", "Bbm7", "Bb", "Bb7", "Cb", "Cbmaj7", "Db", "Db7", "Ebm", "Ebm7", "Fdim"],
  "Bbm": ["Db", "Dbmaj7", "Ebm", "Ebm7", "Fm", "Fm7", "F", "F7", "Gb", "Gbmaj7", "Ab", "Ab7", "Bbm", "Bbm7", "Cdim"],
  "Fm": ["Ab", "Abmaj7", "Bbm", "Bbm7", "Cm", "Cm7", "C", "C7", "Db", "Dbmaj7", "Eb", "Eb7", "Fm", "Fm7", "Gdim"]
}


class ChordTransposer:
    def __init__(self, key="C", preference="#"):
        self.preference = 0 if preference == "#" else 1
        self.target_key = key

    def _get_index(self, chord):
        distances = minor_distances if 'm' in chord else major_distances
        for chords in distances:
            if chord in chords:
                return distances.index(chords)

    def _get_key(self, index, is_minor):
        distances = minor_distances if is_minor else major_distances
        possible_keys = distances[index % len(distances)]
        return possible_keys[self.preference] if len(possible_keys) > 1 else possible_keys

    def _estimate_key(self, progression):
        counts = {key: len(set(progression).intersection(chords))
                  for key, chords in keys.items()}
        return max(counts.items(), key=operator.itemgetter(1))[0]

    def _half_tones_direction(self, source_key):
        source_index = self._get_index(source_key)
        target_index = self._get_index(self.target_key)
        return target_index - source_index

    def _flat_to_sharp(self, chord):
        if len(chord) > 1 and chord[1] == "b":
            root = chord[0]
            return flat_to_sharp[root] + "#" + chord[2:]
        else:
            return chord

    def _transpose_chord(self, source_chord, direction):
        variation = ""
        for v in ["5", "6", "7", "7b5", "dim", "aug", "maj", "sus2",
                  "sus4", "maj7", "dim7", "add6"]:
            if v in source_chord:
                variation = v
        base_chord = source_chord.strip(variation)

        source_index = self._get_index(base_chord)
        new_base = self._get_key(source_index + direction, 'm' in base_chord)
        return self._flat_to_sharp(new_base + variation)

    def transpose(self, chords):
        source_key = self._estimate_key(chords)
        direction = self._half_tones_direction(source_key)
        return [self._transpose_chord(chord, direction) for chord in chords]


class UltimateGuitarCollector:
    def __init__(self, config):
        self._base_uri = config["base_uri"]
        self._transposer = ChordTransposer("C")
        self._chord_pattern = r"(\[ch\])([A-G]+)(\/[A-G]*[b#])*([(?m)|(?m\d)" + \
                               "|(?b\d)|(?#\d)|(?maj\d)|(?add\d)|(?sus\d)|" + \
                               "(?aug)|(?aug\d)|(?dim)|(?dim\d)]*)" + \
                               "(\/[A-G]*[b#])*(\[\/ch\])"

    def _get_dict(self, url):
        response = requests.get(url=url)
        soup = BeautifulSoup(response.content, 'html.parser')
        script = soup.find('script', text=re.compile('window.UGAPP.store.page'))
        json_text = re.search(r'^\s*window\.UGAPP\.store\.page\s*=\s*({.*?})\s*;\s*$', \
                              script.string, flags=re.DOTALL | re.MULTILINE).group(1)
        return json.loads(json_text)

    def _format_uri(self, artist_name, song_name):
        artist = "+".join(artist_name.lower().split(" "))
        song = "+".join(song_name.lower().split(" "))
        artist_and_song = artist + "+" + song
        return self._base_uri.format(artist_and_song)

    def collect(self, artist_name, song_name):
        data = self._get_dict(self._format_uri(artist_name, song_name))

        if not data["data"].get("not_found", False):
            tabs = [tab for tab in data["data"]["results"]
                    if not tab.get("marketing_type")
                    and tab.get("type_name", "Other") == "Chords"]
        else:
            tabs = []

        for tab in tabs:
            chord_data = self._get_dict(tab["tab_url"])
            raw_chords = chord_data['data']['tab_view']['wiki_tab']['content']
            prog = re.compile(self._chord_pattern)
            result = prog.findall(raw_chords)

            chords = result
            for i in range(len(result)):
                value = result[i][1] + result[i][2] + result[i][3] + result[i][4]
                if "/" in value:
                    value = value.split("/")[0]
                elif "(2)" in value:
                    value = value.strip("(2)")
                chords[i] = value

            if [c.lower() for c in chords[:6]] == ["e", "a", "d", "g", "b", "e"]:
                chords = chords[6:]

            if chords:
                return ", ".join(self._transposer.transpose(chords))

        return ""
