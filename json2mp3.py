import sys
import json
from subprocess import call
import urllib
import os

class Slides():
	""" Class for processing audio of slides extracted from JSON file"""

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

	def read_and_parse(self, file_name):
		"""Makes calls to output an .mp3 file for each block and one for the full slide"""
		d = {}
		with open(file_name) as json_data:
			d = json.load(json_data)

		# set defaults and reset to (overriding) defaults, if any	
		default_tts_engine ="say" # alternative is "google"
		default_language = "Alex" # alternative is "en-ca" for example
		default_block_type = "words" # alternative is "mixed" words and phonemes

		if "language-default" in d:
			default_language = d["language-default"]
		if "tts-engine" in d:
			default_tts_engine = d["tts-engine"]
		if "block-type" in d:
			default_block_type = d["block-type"]

		for on_slide, slide in enumerate(d["slides"]):
			text_to_speak = ""
			for on_block, block in enumerate(slide['slide']):

				# pass defaults through to blocks
				language   = default_language
				tts_engine = default_tts_engine
				block_type = default_block_type

				if "language" in block:
					language = block["language"]
				if "tts-engine" in block:
					tts_engine = block["tts-engine"]
				if "block-type" in block:
					block_type = block["block-type"]

				if "text" in block:
					text_to_speak += block['text'] + " "
					if "phoneme" in block:
						tts_input = "[[inpt PHON]] " + block["phoneme"] 
						d["slides"][on_slide]['slide'][on_block]['audio'] = \
						 self.write_audio(file_name, tts_input, language, on_slide, on_block + 1, tts_engine)
					else:
						d["slides"][on_slide]['slide'][on_block]['audio'] = \
						 self.write_audio(file_name, block['text'], language, on_slide, on_block + 1, tts_engine)
				elif "phoneme" in block:
					tts_input = "[[inpt PHON]] " + block["phoneme"] 
					d["slides"][on_slide]['slide'][on_block]['text'] = block["phoneme"]
					d["slides"][on_slide]['slide'][on_block]['audio'] = \
						 self.write_audio(file_name, tts_input, language, on_slide, on_block + 1, tts_engine)
					text_to_speak = tts_input + " "

			if "word" in slide:
				d["slides"][on_slide]['audio'] = self.write_audio(file_name, slide["word"], language, on_slide, 0, tts_engine)
			else:
				d["slides"][on_slide]['audio'] = self.write_audio(file_name, text_to_speak, language, on_slide, 0, tts_engine)

		with open(self.stem(file_name) + '_output.json', 'w') as outfile:
		    json.dump(d, outfile)


def main(argv):
	if len(argv) < 2:
		print "Usage: python json2mp3.py <json file>"
		print "       .mp3 files output to <json file> subfolder of audio folder"
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

