import sys
import json
from subprocess import call
import urllib
import os

class Slides():
    """ Class for processing audio of slides extracted from Coggle JSON file"""

    def stem(self, file_name):
        return ".".join(file_name.split(".")[0:len(file_name.split("."))-1]) 

    def write_audio_say(self, file_name, text_to_speak, language, on_slide, on_block):
        """Use Mac say command to create .m4a files and ffmpeg to convert them to .mp3"""
        cmd = ["say", '\"' + text_to_speak + '\"', "-v", language, "-o", "s" + 
                str(on_slide) + "_" + str(on_block) + ".m4a", "--file-format=m4af"]
        call(cmd)
        output_file = "audio/" + self.stem(file_name) +"_output.json/s" + str(on_slide) + "_" + str(on_block) + ".mp3"
        cmd = ["ffmpeg", "-y", "-i", "s" + 
                str(on_slide) + "_" + str(on_block) + ".m4a", output_file]
        call(cmd)
        cmd = ["rm", "s" + 
                str(on_slide) + "_" + str(on_block) + ".m4a"]
        call(cmd)
        return output_file


    def write_audio_google(self, file_name, text_to_speak, language, on_slide, on_block):
        """Use Google Text-to-Speech to create .mp3 files"""
        print "To .mp3: " + text_to_speak
        q = urllib.urlencode({"q":text_to_speak.encode('utf-8')})
        cmd = ["wget", "-q", "-U", "Mozilla", 
               'http://www.translate.google.com/translate_tts?ie=UTF-8&tl=' + language + '&' + q,
               "-O", "audio/" + self.stem(file_name) +"_output.json/s" + str(on_slide) + "_" + str(on_block) + ".mp3"]
        call(cmd)
        return "s" + str(on_slide) + "_" + str(on_block) + ".mp3"


    def write_audio(self, file_name, text_to_speak, language, on_slide, on_block, tts_engine):
        """Call appropriate write_audio method"""
        if tts_engine == 'say':
            return self.write_audio_say(file_name, text_to_speak, language, on_slide, on_block)    
        if tts_engine == 'google':
            return self.write_audio_google(file_name, text_to_speak, language, on_slide, on_block)

    def read_and_parse(self, file_name_or_url):
        """Makes calls to output an .mp3 file for each block and one for the full slide"""
        d = {}
        if file_name_or_url.startswith("http"):
            # make URL to fetch from Coggle api
            h,t = os.path.split(file_name_or_url)
            print "\nUse the URL below to fetch the JSON for your Coggle."
            print "https://coggle.it/api/1/diagrams/{}/nodes".format(t)
            print "\nSave the result to a file and run "
            print "python cogglejson2mp3.py <file name>\n"
            return
        else:
            file_name = file_name_or_url
            with open(file_name) as json_data:
                d = json.load(json_data)

        coggle_nodes = d[0]["children"]

        default_language = "Alex" # alternative is "en-ca" for example
        default_tts_engine ="say" # alternative is "google"
        default_block_type = "words" # alternative is "mixed" words and phonemes
        # set defaults and reset to (overriding) defaults, if any
        for node in coggle_nodes:
            if node["offset"]["x"] < 0:
                if node["text"].startswith("language:"):
                    default_language = node["text"][9:].strip()
                if node["text"].startswith("tts_engine:"):
                    default_tts_engine = node["text"][11:].strip()
                if node["text"].startswith("block-type:"):
                    default_block_type = node["text"][11:].strip()

        # extract and sort on y the text from slides with positive x
        slides = []
        for node in coggle_nodes:
            if node["offset"]["x"] > 0:
                # filter any improper slides
                text = node["text"]
                if text.startswith("![uploaded image](") and (text.find("\n") > 0):
                    image = text[18:text.find(")")]
                    words = text[text.find("\n")+1:]
                    slides.append((node["offset"]["y"],image,words))
        slides.sort(key=lambda tup: tup[0])

        output = {"slides": []}
        for on_slide, slide in enumerate(slides):
            output["slides"].append({"slide" : []})
            text_to_speak = ""
            # split blocks on [ ] or space
            if slide[2].find("[") >= 0:
                blocks = []
                text_to_parse = slide[2]
                left_bracket = text_to_parse.find("[")
                while left_bracket >= 0:
                    # add any words to left of [
                    words = text_to_parse[:left_bracket].split()
                    for word in words:
                        blocks.append(word.strip())
                    right_bracket = text_to_parse.find("]", left_bracket)
                    if right_bracket > 0:
                        blocks.append(text_to_parse[left_bracket+1:right_bracket].strip())
                        text_to_parse = text_to_parse[right_bracket+1:]
                        left_bracket = text_to_parse.find("[")
                    else:
                        blocks.append(text_to_parse[left_bracket+1:].strip())
                        text_to_parse = ""
                        left_bracket = -1
                remaining_blocks = text_to_parse.strip().split()
                for block in remaining_blocks:
                    blocks.append(block.strip())
            else:
                blocks = slide[2].split()
                blocks = [block.strip() for block in blocks]

            for on_block, block in enumerate(blocks):
                # pass defaults through to blocks
                language   = default_language
                tts_engine = default_tts_engine
                block_type = default_block_type
                text_to_speak += block + " "
                output["slides"][on_slide]['slide'].append({})
                output["slides"][on_slide]['slide'][on_block]['img'] = slide[1]
                output["slides"][on_slide]['slide'][on_block]['text'] = block
                output["slides"][on_slide]['slide'][on_block]['audio'] = \
                         self.write_audio(file_name, block, language, on_slide, on_block + 1, tts_engine)

            output["slides"][on_slide]['audio'] = self.write_audio(file_name, text_to_speak, language, on_slide, 0, tts_engine)

        with open(self.stem(file_name) + '_output.json', 'w') as outfile:
            json.dump(output, outfile)


def main(argv):
    if len(argv) < 2:
        print "Usage: python cogglejson2mp3.py <json file>"
        print "   or: python cogglejson2mp3.py <Coggle URL>"
        print "       .mp3 files output to <json file> or <Coggle code> subfolder of audio folder"
    else:
        slides = Slides()
        # Make sure audio folder exists
        if not os.path.exists("./audio"):
            os.makedirs("./audio")
        if not os.path.exists("./audio/" + slides.stem(argv[1]) + "_output.json"):
            os.makedirs("./audio/" + slides.stem(argv[1]) + "_output.json")
        # As a convenience, make sure corresponding images folder also exists
        if not os.path.exists("./images"):
            os.makedirs("./images")
        if not os.path.exists("./images/" + slides.stem(argv[1]) + "_output.json"):
            os.makedirs("./images/" + slides.stem(argv[1]) + "_output.json")
        slides.read_and_parse(argv[1])

if __name__ == "__main__":
    main(sys.argv)

