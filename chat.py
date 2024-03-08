import random
import json
import smtplib
from typing import Counter
import torch
from pymongo import MongoClient
import re
regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
sender = 'ds25@24livehost.com'
from email.message import EmailMessage
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# import app

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "SEO EXPERT"
try:
    conn = MongoClient()
    print("Connected successfully!!!")
    db = conn.database
    collection = db.chatBot
except:  
    print("Could not connect to MongoDB")
def sendMail(receiver):
    message = EmailMessage()
    message['Subject'] = 'conformation mail'
    message['From'] = sender
    message['To'] = receiver
    message.set_content("our tech team will contact you in 24hrs")
    try:
        smtpObj = smtplib.SMTP('mail.24livehost.com',587)
        smtpObj.login('ds25@24livehost.com','bgzBHKvXehNz')
        print("Login Success")
        smtpObj.sendmail(sender, receiver, str(message))
        smtpObj.close()         
        print ("Successfully sent email")
    except Exception as e:
        print(e)
        print ("Error: unable to send email")

def saveData(customer):
    global visitors
    visitors = customer
    collection.insert_one(customer)
    return "data save sucessfully"

def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if tag == 'greeting':
        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]
        if prob.item() > 0.75:
            for intent in intents['intents']:
                if tag == intent["tag"]: 
                    return random.choice(intent['responses'])

    elif tag == 'goodbye':
        if prob.item() > 0.75:
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    return random.choice(intent['responses'])
    
    # sendMail(visitors['email'])
    return f"Thank you {visitors['name']}.Our expert will contact you soon."
    

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        # sentence = "do you use credit cards?"
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print(resp)

