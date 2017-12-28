try:
    import Image
except ImportError:
    from PIL import Image, ImageEnhance, ImageGrab
import pytesseract
import webbrowser
from googleapiclient.discovery import build
import os
from datetime import datetime
import re
import sys, tty, termios
from API_Pass import google_cse_id, google_cse_api_key

# Google Custom Search
g_cse_api_key = google_cse_id
g_cse_id = google_cse_api_key

def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))

def google_search(query, start):
	service = build("customsearch", "v1", developerKey=g_cse_api_key)
	res = service.cse().list(q=query, cx=g_cse_id, start=start).execute()
	return res

def retrieve_q_and_a(text):
	question_answers = text.split('?')
	if len(question_answers) > 2:
		corrString = ''
		for x in range(len(question_answers) - 1):
			corrString += question_answers[x]
		question_answers = [corrString, question_answers[len(question_answers) - 1]]
	question = question_answers[0].replace('\n', ' ')
	answers = question_answers[1].split('\n')
	answers = [ans.strip() for ans in answers]
	answers = [x for x in answers if x != '']
	print(answers)
	return question, answers

def naive_approach(question):
	url = "https://www.google.com.tr/search?q={}".format(question)    
	webbrowser.open(url)

# Google Question and count number of each result
def metric1Func(question, answers):
	met1 = [0, 0, 0]
	res = google_search(question, None)
	items = str(res['items']).lower()
	#print(items)
	met1[0] = items.count(answers[0].lower())
	met1[1] = items.count(answers[1].lower())
	met1[2] = items.count(answers[2].lower()) 
	return met1

# Google Question and each specific Answer and count total results
def metric2Func(question, answers):
	met2 = [0, 0, 0]
	res0 = google_search(question + ' "' + answers[0] + '"', None)
	res1 = google_search(question + ' "' + answers[1] + '"', None)
	res2 = google_search(question + ' "' + answers[2] + '"', None)
	return [int(res0['searchInformation']['totalResults']), int(res1['searchInformation']['totalResults']), int(res2['searchInformation']['totalResults'])]

def predict(metric1, metric2, answers):
	max1 = metric1[0]
	max2 = metric2[0]
	for x in range(1, 3):
		if metric1[x] > max1:
			max1 = metric1[x]
		if metric2[x] > max2:
			max2 = metric2[x]
	if metric1.count(0) == 3:
		return answers[metric2.index(max2)]
	elif metric1.count(max1) == 1:

		if metric1.index(max1) == metric2.index(max2):
			return answers[metric1.index(max1)]
		else:
			percent1 = max1 / sum(metric1)
			percent2 = max2 / sum(metric2)
			if percent1 >= percent2:
				return answers[metric1.index(max1)]
			else:
				return answers[metric2.index(max2)]
	elif metric1.count(max1) == 3:
		return answers[metric2.index(max2)]
	else:
		return answers[metric2.index(max2)]
		

def q_analysis():
	startTime = datetime.now()
	image = Image.open('testimages/hq_dollar_no_background.PNG')
	#image = ImageGrab.grab(bbox=(1050, 350, 1850, 1300))
	Contrast = ImageEnhance.Contrast(image)
	image = Contrast.enhance(3)

	# Raw output
	ocr_output = pytesseract.image_to_string(image)
	ocr_output = ocr_output.encode("ascii", errors="ignore").decode()

	# Question/Answer Parsed
	question, answers = retrieve_q_and_a(ocr_output)
	question = question.replace("\"", '')

	naive_approach(question)
	met1 = metric1Func(question, answers)
	met2 = metric2Func(question, answers)
	print(met1)
	print(met2)
	notify(question, predict(met1, met2, answers))
	print(datetime.now() - startTime)

fd = sys.stdin.fileno()
old = termios.tcgetattr(fd)
while True:
	print("Waiting....")
	tty.setcbreak(sys.stdin)
	key = ord(sys.stdin.read(1))  # key captures the key-code 
	if key==32:
		print("Running Question Analysis")
		q_analysis()
		
	if key == 113:
		termios.tcsetattr(fd, termios.TCSADRAIN, old)
		sys.exit(0)

