import sys
import json
from subprocess import call

class Slides():
	""" Class for processing audio of slides extracted from JSON file"""

	def write_audio(self, text_to_speak, on_slide, on_block):
		cmd = ["say", '\"' + text_to_speak + '\"', "-o", "s" + 
		        str(on_slide) + "_" + str(on_block) + ".m4a", "--file-format=m4af"]
		print(cmd)
		call(cmd)
		output_file = "s" + str(on_slide) + "_" + str(on_block) + ".mp3"
		cmd = ["ffmpeg", "-y", "-i", "s" + 
		        str(on_slide) + "_" + str(on_block) + ".m4a", output_file]
		print(cmd)
		call(cmd)
		cmd = ["rm", "s" + 
		        str(on_slide) + "_" + str(on_block) + ".m4a"]
		print(cmd)
		call(cmd)
		return output_file

	def read_and_parse(self,file):
		d = {}
		with open(file) as json_data:
			d = json.load(json_data)
		print d
		print d[0]['slide'][0]['img']
		on_slide = 0
		on_block = 0
		text_to_speak = ""
		for slide in d:
			for block in slide['slide']:
				print block
				if block['text']:
					text_to_speak += block['text'] + " "
					on_block += 1
					d[on_slide]['slide'][on_block-1]['audio'] = \
					 self.write_audio(block['text'], on_slide, on_block)

			d[on_slide]['audio'] = self.write_audio(text_to_speak, on_slide, 0)
			print json.dumps(d)
			with open('test_output.json', 'w') as outfile:
			    json.dump(d, outfile)
			on_slide += 1
			on_block = 0
			text_to_speak = ""


def main(argv):
    slides = Slides()
    slides.read_and_parse(argv[1])

if __name__ == "__main__":
    main(sys.argv)

