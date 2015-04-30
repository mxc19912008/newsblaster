# Article Annotator Server
#
# @Author - Ramzi Abdoch
#
# This server is meant to facilitate human
# annotation of HTML articles for use in the
# Newsblaster system.
#
# Flow:
#   1. users start the server by calling
#		- python annotator.py <source_dir> <dest_dir>
#		- <source_dir> is the directory where your HTML files reside
#		- <dest_dir> is the directory where .annotation files are saved
#	2. users can request /todo or /done to see a list
#		of articles that need annotation and have been
#		annotated already
#	3. from the /todo page, users can select an article and route to
#		/annotate/<article_path>
#		- <article_path> is the path of the article in the <source_dir>
#

# To iterate through folder
import sys
import os
import re

source_dir = sys.argv[1]
dest_dir = sys.argv[2]

from flask import Flask
from flask import render_template
from flask import request
app = Flask(__name__)

@app.route('/')
def home():
	files = list()

	for filename in os.listdir(source_dir):
		files.append(filename)

	return render_template('todo.html', files=files)

# List unannotated articles
@app.route('/todo')
def todo(files=None):
	files = list()

	for filename in os.listdir(source_dir):
		files.append(filename)

	return render_template('todo.html', files=files)

# List annotated articles
@app.route('/done')
def done(files=None):
	files = list()

	for filename in os.listdir(dest_dir):
		files.append(filename)

	return render_template('done.html', files=files)

# Annotate an article
@app.route('/annotate/<article_path>')
def annotate(article_path):

	# Correct path
	path = os.path.join(source_dir, article_path)

	# Open file
	fo = open(path)
	contents = fo.read();

	# Close opened file
	fo.close()

	# Pick <body> out of HTML
	b = re.search(r"<body[^>]*>(.*?)</body>", contents, re.DOTALL)
	body = b.group(1)
	body = body.decode('utf-8')

	# Replace links (<a>) with <a-disabled>
	body = re.sub(r"<a([^>]*)>(.*?)</a>", r"<a-disabled \1>\2</a-disabled>", body, flags=re.DOTALL|re.MULTILINE)
	#body = body.replace("</a>", "</a-disabled>")

	# Render Annotator + Article
	return render_template('annotator.html', filename=article_path, contents=body)

# View an annotated article
@app.route('/view/<article_path>')
def view(article_path):
	# Correct path
	path = os.path.join(dest_dir, article_path)

	# Open file
	fo = open(path)
	contents = fo.read()

	# Close opened file
	fo.close()

	# Pick <body> out of HTML
	b = re.search(r"<body[^>]*>(.*?)</body>", contents, re.DOTALL)
	body = b.group(1)
	body = body.decode('utf-8')

	# Render Annotator + Article
	return render_template('view.html', filename=article_path, contents=body)

# Save annotated articles
@app.route('/save/', methods=['POST'])
def save():
	# Correct path
	article_path = request.form['filename']
	path = os.path.join(dest_dir, article_path + u".annotation")

	# Pick <head> out of HTML
	original_file_path = os.path.join(source_dir, article_path + u".html")
	of = open(original_file_path)

	# Read original_file
	of_contents = of.read()

	h = re.search(r"<head[^>]*>(.*?)</head>", of_contents, re.DOTALL)
	head = h.group(1)
	head = "<head>\n" + head + "\n</head>"

	# Create file
	fo = open(path, "wb+")

	# Write files to disk
	contents = request.form['content']
	body = contents.encode('utf-8')

	body = "<body>\n" + body + "\n</body>"

	# Write head + annotation in .annotation
	print head
	print body

	fo.write(head)
	fo.write(body)

	# Close file
	fo.close()

	# Find out where we are in the list of articles to complete
	files = os.listdir(source_dir)
	file_idx = files.index(article_path + u".html")

	# Delete source file
	done_file = os.path.join(source_dir, article_path + u".html")
	os.remove(done_file)

	# If not the last article
	if(file_idx != len(files)):
		# Iterate to next article
		next_file = files[file_idx + 1]

		# Return url of next article for redirect
		return "http://localhost:5000/annotate/" + next_file
	else:
		# Return list of finished articles
		return "http://localhost:5000/done"

	return u"NULL"

# Skip Article (and delete file)
@app.route('/skip/', methods=['POST'])
def skip():
	# Correct path
	article_path = request.form['filename']

	# Find out where we are in the list of articles to complete
	files = os.listdir(source_dir)
	file_idx = files.index(article_path + u".html")

	# Delete source file
	done_file = os.path.join(source_dir, article_path + u".html")
	os.remove(done_file)

	# If not the last article
	if(file_idx != len(files)):
		# Iterate to next article
		next_file = files[file_idx + 1]

		# Return url of next article for redirect
		return "http://localhost:5000/annotate/" + next_file
	else:
		# Return list of finished articles
		return "http://localhost:5000/done"

	return u"NULL"

if __name__ == '__main__':
    app.run(debug=True)