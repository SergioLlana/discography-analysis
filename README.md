# Discography Analysis

The main purpose of this repository is to perform a comprehensive analysis of the discography of modern music bands, applying multivariate analysis, machine learning and natural language processing techniques.

All experiments have been performed using data collected with a homemade scrapper for the following three groups: Arctic Monkeys, The Last Shadow Puppets and Franz Ferdinand. Note that the first two bands share the same lead singer and main songwriter (Alex Turner), whereas the third band only shares the music style with the others.

## 1. Scrapper

The scrapper performs the following steps to create a data file for each band:
1. It makes use of Spotify's API to collect information about the entire discography of the group, plus some useful attributes provided by Spotify such as danceability or acousticness.
2. It connects to Genius' API to collect the lyrics of all songs in the discography.
3. Finally, it uses BeautifulSoup to extract the chord progression of all songs from the best rated post in UltimateGuitar.com

The result is a JSON file which contains a list of objects with the following format:

```
{
  "album": "AM",
  "index": 3,
  "id_spotify": "4FSm0Ca6Hzd7Vx7TpSfcSy",
  "name": "Arabella",
  "lyrics": "...",
  "artist": "Arctic Monkeys",
  "url": "https://genius.com/Arctic-monkeys-arabella-lyrics",
  "energy": 0.577,
  "chords": "...",
  "tempo": 180.045,
  "uri": "spotify:track:4FSm0Ca6Hzd7Vx7TpSfcSy",
  "track_number": 4,
  "acousticness": 0.0198,
  "duration_s": 207.35664,
  "danceability": 0.579,
  "key": 2.0,
  "year": 2013,
  "time_signature": 4.0,
  "valence": 0.453,
  "id_genius": 212611,
  "mode": 1.0
}
```

The code can be found in [data_retrieval.py](https://github.com/SergioLlana/discography-analysis/blob/master/data_retrieval.py) and in the _collector_ folder.

## 2. Album Similarity based on Chord Progressions

This experiment aims to compare the similarity between albums of our selected bands based their harmony (e.g. chord progressions) by modeling them as graphs. Then, we have compared three different ways of computing the pair-wise similarities between the graphs.

At this point, our data set contained just a list of songs, with their corresponding chord progression stored as an ordered list. In order to structure this information in the form of a graph, we grouped the songs by album and created a new graph per album. Then, a unique vertex was created for each distinct chord that appeared in any of the songs of the album. The edges were created in order to represent the consecutiveness of chords in a chord progression. The following figure shows an example of graph:

### Preprocessing

Since we needed to aggregate all songs of an album together to compare them later and songs could be in different keys, we decided to transposed them all to C. As our goal was to estimate the harmonic similarity of albums, the tonality was not important.

Our solution to detect the key of each song consisted on comparing the song’s sequence to different arrays of chords, each one containing the chords most frequently used when playing in each different key. Note that we have also normalized the existence of sharps and flats. We know that this method is rather naive and it should be improved in the future.

### Graph Similarity Methods

#### Similarity based on graph metrics

This first method is the simplest one. It consisted on computing several graph metrics such as the number of nodes and edges, diameter or clustering coefficient for each album. Then, the correlation matrix was computed to create a heat-map. Note that more complex metrics could have been used.

#### Neumann Kernels + Kendall's Tau

The second method was composed by three phases. Firstly, we computed the K and T correlation matrices with the
Neumann Kernel algorithm which gave us a ranking per album indicating the most important chords. Then, using the Kendall’s tau correlation coefficient, the distance between all pair-wise combination of albums was computed. Finally, in order to be able to compare the results with the previous method, the distance must be converted into a similarity measure.

#### Edit distance for graphs

This last method consisted on counting how many nodes and edges we must add/modify/remove to get from one graph to another. Because of the large computational cost of the method and the lack of time and resources for this project, there are no empirical results.

### Results

These are the results of method 1:

<p align="center"><img src="https://raw.githubusercontent.com/SergioLlana/discography-analysis/master/docs/images/plot1.png" width="75%"></p>

It can be seen how albums from _Arctic Monkeys_ (e.g. _AM_ and _Favourite Worst Nightmare_) seem to be quite similar. The same happens between _You Could Have It So Much Better_ and _Franz Ferdinand_, both from _Franz Ferdinand_.

These are the results of method 2:

<p align="center"><img src="https://raw.githubusercontent.com/SergioLlana/discography-analysis/master/docs/images/plot2.png" width="75%"></p>

Albums by _Arctic Monkeys_ keep looking quite similar between them, however the ones by _Franz Ferdinand_ do not appear to be as similar as with the previous method. It is worth noting that albums by _The Last Shadow Puppets_ are more similar to the ones by _Arctic Monkeys_ than to the ones by _Franz Ferdinand_, specially with _Tranquility Base Hotel & Casino_ which was also pointed out by music critics when it was released last year. Recall that this two groups share the same songwriter.

Note all insights should be interpreted with caution because of the amount of assumptions taken in the process and that we are only working with ”one musical dimension” by focusing on harmony. For further information, please read the [full report](https://github.com/SergioLlana/discography-analysis/blob/master/docs/Album%20Similarity%20based%20on%20Chord%20Progressions.pdf).

## 3. Album Similarity based on lyrics

TBD

## 4. Contact us

For further information, please email us:
* sergio.llanaperez@gmail.com
* pau.madrero@est.fib.upc.edu
