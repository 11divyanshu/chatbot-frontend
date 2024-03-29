#imports
from flask import Flask, render_template, request
# from chatterbot import ChatBot
# from chatterbot.trainers import ChatterBotCorpusTrainer
import nltk
# nltk.download('punkt')
# nltk.download()
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
import random
import json
import pickle


app = Flask(__name__)
# #create chatbot
# englishBot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")
# trainer = ChatterBotCorpusTrainer(englishBot)
# trainer.train("chatterbot.corpus.english") #train the chatter bot for english
# #define app routes


with open("intents.json") as file:
		data = json.load(file)



# try:
# 	with open("data.pickle", "rb") as f:
# 		words, labels, training, output = pickle.load(f)
# except:
words = []
labels = []
docs_x = []
docs_y = []

for intent in data["intents"]:
	for pattern in intent["patterns"]:
		wrds = nltk.word_tokenize(pattern)
		words.extend(wrds)
		docs_x.append(wrds)
		docs_y.append(intent["tag"])

	if intent["tag"] not in labels:
		labels.append(intent["tag"])

words = [stemmer.stem(w.lower()) for w in words if w != "?"]
words = sorted(list(set(words)))

labels = sorted(labels)

training = []
output =[]

out_empty = [0 for _ in range(len(labels))]

for x, doc in enumerate(docs_x):
	bag = []

	wrds = [stemmer.stem(w) for w in doc]

	for w in words:
		if w in wrds:
			bag.append(1)
		else:
			bag.append(0)

	output_row = out_empty[:]
	output_row[labels.index(docs_y[x])] = 1

	training.append(bag)
	output.append(output_row)

training = numpy.array(training)
output = numpy.array(output)

	# with open("data.pickle", "wb") as f:
	# 	pickle.dump((words, labels, training, output), f)




# try:
# 	model.load("model.tflearn")
# except:
model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
model.save("model.tflearn")

def bag_of_words(s,cwords):
	bag = [0 for _ in range(len(words))]

	s_words = nltk.word_tokenize(s)
	s_words = [stemmer.stem(word.lower()) for word in s_words]

	for se in s_words:
		for i, w in enumerate(words):
			if w == se:
				bag[i] = 1

	return numpy.array(bag)

# def chat():
#
# 	while True:
# 		inp = input("You: ")
# 		if inp.lower() == "quit":
# 			break
#
# 		results = model.predict([bag_of_words(inp, words)])
# 		results_index = numpy.argmax(results)
# 		tag = labels[results_index]
#
# 		for tg in data["intents"]:
# 			if tg['tag'] == tag:
# 				responses = tg['responses']
#
# 		reply = random.choice(responses)






@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get")


#function for the bot response
def get_bot_response():
    userText = request.args.get('msg')
    results = model.predict([bag_of_words(userText, words)])
    results_index = numpy.argmax(results)
    tag = labels[results_index]

    for tg in data["intents"]:
        if tg['tag'] == tag:
            responses = tg['responses']

    reply = random.choice(responses)
    return reply


if __name__ == "__main__":
    app.run()
