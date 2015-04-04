# words_and_pictures
Python and Javascript to make and play talking pictures.

Create simple, interactive reading lessons with words and pictures by creating three things:

- pictures
- words
- audio files of/from the words

The pictures are grouped on *slides*.

The words (or phonemes) are separated into *blocks*.

See [demo](http://jg1141.github.io/) with 16 slides, telling a "Pink Shoes" adventure story. 

Other demos show presentation of [phonemes](http://jg1141.github.io//?json=phonemes_output.json/) and [multiple languages](http://jg1141.github.io//?json=languages_output.json/).

##JSON Format for Linking Pictures (img) to Words (text)

Example input (test.json):

```json
{
  "block-type" : "words",
  "language-default" : "en-uk",
  "slides" : [
    {
      "slide" : [
        {
          "img" : "img1.png",
          "text" : "This is a"
        },
        {
          "img" : "img2.png",
          "text" : "demo slide."
        }
      ]
    }
  ],
  "tts-engine" : "google"
}
```

Use

> $ python json2mp3.py test.json

to use the *Google Translate Text-to-Speech API* to create .mp3 files into the audio folder (subfolder ```<your json file name>```).

On a Mac, use ```"tts-engine" : "say"``` to use the *say* utility and *ffmpeg* to create .mp3 files from the words and add the file names (with key of "audio") to each block. Output goes into *test_output.json* or (```<your file name stem>_output.json```).

Prefer your own voice? Use a sound file editor to create .mp3 files with names following the pattern of s + slide_block + .mp3:

- s0_0.mp3 for full audio of first slide
- s0_1.mp3 for audio of first block of words on first slide
- s0_2.mp3 for audio of second block of words on first slide
- ...
- s1_0.mp3 for full audio of second slide
- s1_1.mp3 for audio of first block of words on second slide
- s1_2.mp3 for audio of second block of words on second slide


##Playing with Cloned Repo

With Python 2:

```
$ git clone https://github.com/jg1141/words_and_pictures.git
$ cd words_and_pictures
$ python -m SimpleHTTPServer
```

Open your web browser to [http://localhost:8000/](http://localhost:8000/).
