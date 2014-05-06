#!/usr/bin/python

from lxml import etree
import os, re, getopt
from copy import deepcopy
from sys import argv, stderr, exit

def is_valid_xml(from_file):
	input_dom = etree.parse(from_file)
	input_root = input_dom.getroot()
	
	return str(input_root.tag)=='xmeml'
	
def process_file(from_file, to_file):
	input_dom = etree.parse(from_file)
	input_root = input_dom.getroot()
	clip_list = input_root.xpath("/xmeml/sequence/media/video//track/clipitem[filter/effect/effectid='timeremap']")

	output_xml_stub = """<?xml version="1.0" encoding="UTF-8"?>
	<!DOCTYPE xmeml>
	<xmeml version="5">
			<sequence>
					<name>[THIS WILL BE FILLED IN]</name>
					<duration>[THIS WILL ALSO BE FILLED IN]</duration>
					<rate>
							<timebase>24</timebase>
							<ntsc>true</ntsc>
					</rate>
					<in>-1</in>
					<out>-1</out>
					<timecode>
							<string>00:59:50:00</string>
							<frame>86160</frame>
							<displayformat>NDF</displayformat>
							<rate>
									<timebase>24</timebase>
									<ntsc>true</ntsc>
							</rate>
					</timecode>
					<media>
							<video>
									<track>
											<enabled>true</enabled>
											<locked>false</locked>
									</track>
									<format>
											<samplecharacteristics>
													<width>1920</width>
													<height>1080</height>
													<pixelaspectratio>square</pixelaspectratio>
													<rate>
															<timebase>24</timebase>
															<ntsc>true</ntsc>
													</rate>
													<codec>
															<appspecificdata>
																	<appname>Final Cut Pro</appname>
																	<appmanufacturer>Apple Inc.</appmanufacturer>
																	<data>
																			<qtcodec/>
																	</data>
															</appspecificdata>
													</codec>
											</samplecharacteristics>
									</format>
							</video>
							<audio>
									<track>
											<enabled>true</enabled>
											<locked>false</locked>
									</track>
							</audio>
					</media>
			</sequence>
	</xmeml>
	"""

	output_root = etree.XML(output_xml_stub)
	output_track = output_root.xpath("/xmeml/sequence/media/video/track")[0]

	clip_nodes = []

	def sort_on_start_time(item1, item2):
		#print "%s:%s %s:%s return:%s" % (item1.get("id"), int(item1.xpath("start")[0].text), item2.get("id"), int(item2.xpath("start")[0].text), int(item2.xpath("start")[0].text) - int(item1.xpath("start")[0].text))
		return int(item1.xpath("start")[0].text) - int(item2.xpath("start")[0].text)

	for index, clip in enumerate(clip_list):
		file_el = clip.xpath("file")[0]
	
		if len(file_el.xpath("pathurl"))==0:
			full_file_el = input_root.xpath("//clipitem[file/@id='%s']/file[pathurl!='']" % file_el.get("id"))[0] 
			clip.replace(file_el, deepcopy(full_file_el))
		
		clip_nodes.append(clip)

	clip_nodes.sort(sort_on_start_time)

	total_duration = 0

	for index, clip in enumerate(clip_nodes):
		start_el = clip.xpath("start")[0]
		end_el = clip.xpath("end")[0]
	
		timeline_clip_duration = int(end_el.text) - int(start_el.text)

		start_el.text = str(total_duration)
		total_duration += timeline_clip_duration
		end_el.text = str(total_duration)

		print "inserting %s at %s:%s" % (clip.xpath("name")[0].text, start_el.text, end_el.text)
	
		output_track.insert(index, clip)


	output_root.xpath("/xmeml/sequence/duration")[0].text = str(total_duration)
	output_root.xpath("/xmeml/sequence/name")[0].text = "%s-RETIMED CLIPS" % input_root.xpath("/xmeml/sequence/name")[0].text

	#print etree.tostring(output_root, pretty_print=True)
	etree.ElementTree(output_root).write(to_file, pretty_print=True, xml_declaration=True, encoding='UTF-8')

if __name__ == "__main__":	
	if len(argv) < 3:
		print >>stderr, "usage: %s timeline_xml_input timeline_xml_output" % argv[0]
		exit(1)
		
	process_file(argv[1], argv[2])
	