# Importing necessary libraries and modules
from flask import Flask, request
import boto3
from io import BytesIO
import pymongo as pym
from bson.objectid import ObjectId
import pytesseract
from PIL import ImageEnhance, ImageFilter, Image
import re
from yake import KeywordExtractor
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
  PDFInfoNotInstalledError,
  PDFPageCountError,
  PDFSyntaxError
)
import json
import os
import spacy
from textblob import TextBlob
import PyPDF2
import io
from wordfreq import zipf_frequency
import nltk
from nltk.tokenize import word_tokenize
from dotenv import load_dotenv
from time import process_time
from utils import message, keyword_from_search
from helpers import update as helper_update
from helpers import ranking as helper_ranking
import logging
import auth 
from Crypto.Cipher import AES
import datetime
from flask_cors import CORS
from utils.extract_summary import make_summary
from utils.gpt_text_generation import get_judgement, get_title_date_parties
import traceback

# Load environment variables from a .env file
load_dotenv()

# Retrieve environment variables for MongoDB, AWS S3, and other configurations
MONGO_URI = os.getenv("MONGO_URI")
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
APP_SECRET = os.getenv("APP_SECRET")
NONCE = os.getenv("NONCE")

# Create a Flask application
app = Flask(__name__) 

# Enable Cross-Origin Resource Sharing (CORS) for the Flask app
CORS(app)

# Configure logging for the application
logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Connect to MongoDB using the provided URI
client = pym.MongoClient(MONGO_URI)
db = client["diversion"]
documents_collection = db["documents"]
users_collection = db["users"]

# Load the SpaCy English model
nlp = spacy.load("en_core_web_sm")

# Configure Boto3 to interact with AWS S3
s3 = boto3.client("s3", region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# Load stopwords from a JSON file
final_stop = json.load(open("stopwords.json", "r"))['stopwords']

# Define a testing route to check if the server is running
@app.route("/", methods=["GET"])
def default():  
  return message.message(200, "Welcome to the eFaisla API")

# Define a route for autocomplete keyword suggestions
@app.route("/autocomplete", methods=["GET"])
def autocomplete():
  try:
    # Authorization check
    # a = auth.authorize(request, APP_SECRET, NONCE, users_collection)
    # if a['error']:
    #   return message.message_error(a['code'], a['message'], a['err']) 

    # Initialize default values for limit and sort
    limit = -1
    sort = False

    # Get query parameters
    if 'limit' in request.args:
      limit = int(request.args['limit'])

    if 'sort' in request.args:
      sort = str(request.args['sort'])

    # Retrieve all documents with keywords from MongoDB
    cursor = documents_collection.find({"keywords": { '$exists': True }})
    items = list(cursor)
    total_keywords = []

    # Aggregate all keywords from the documents
    for i in items:
      total_keywords += i['keywords']  

    # Remove duplicates and limit the number of keywords
    unique_keywords = list(set(total_keywords))[:limit]

    # Sort keywords if specified
    if sort.lower() == 'true':
      unique_keywords = sorted(unique_keywords)

    # Prepare response data
    data = {
      'keywords': unique_keywords,
      'count': len(unique_keywords),
      'sort': sort
    }

    if limit != -1:
      data['limit'] = limit

    return message.message_custom(data, 200, "Keywords for autocomplete") 
  except Exception as e:
    return message.message_error(500, str(e), "Internal Server Error")

# Define a route to update keywords and clean text for a document
@app.route("/update", methods=["POST"])
def add_keyword_and_cleantext():
  try:
    # Authorization check
    # a = auth.authorize(request, APP_SECRET, NONCE, users_collection)
    # if a['error']:
    #   return message.message_error(a['code'], a['message'], a['err']) 

    # Initialize default values for spell check and OCR
    spell = False
    ocr = False

    try:
      # Get document ID from the request
      id = request.json['id']
    except:
      return message.message_error(400, "ID is a required field", "Bad Request")

    # Check if spell check is specified
    if 'spell' in request.json and request.json['spell'].lower() == 'true':
      spell = True

    try:
      # Retrieve the document from MongoDB
      docs = documents_collection.find_one({"_id": ObjectId(id)})['documents']
    except:
      return message.message_error(404, "Document not found", "Not Found")

    clean_t = ""
    for doc in docs:
      # Fetch the document from AWS S3
      obj = s3.get_object(Bucket=bucket_name, Key=doc['url'].split("/")[-1])
      fs = obj['Body'].read()

      # Read the document using PyPDF2
      pdfReader = PyPDF2.PdfFileReader(io.BytesIO(fs))
      if len(pdfReader.getPage(0).extractText()) == 0:
        # Perform OCR if the document is not readable
        ocr = True
        clean_t += helper_update.return_string_from_path(fs)
      else:
        for i in range(pdfReader.numPages):
          clean_t += pdfReader.getPage(i).extractText().replace("\n", " ")

    if spell:
      clean_t = helper_update.spell_check(clean_t)

    # Extract keywords and clean the text
    keywords_manual = helper_update.check_manual_keywords(clean_t)
    keyword_corpus = helper_update.distill_string(clean_t)
    key = helper_update.return_keyword(keyword_corpus, 30)
    keys = keywords_manual + key

    # Generate summary and extract document metadata using GPT-3
    summary = make_summary(clean_t)
    txt = " ".join(clean_t.split(" ")[:300])
    gpt3_response = get_title_date_parties(txt)

    try:
      # Update the document in MongoDB
      documents_collection.update_one(
        {"_id": ObjectId(id)}, 
        {
          '$set': {
            "keywords": keys, 
            "cleanText": clean_t, 
            "summary": summary,
            "title": gpt3_response.get("title", ''),
            "parties": gpt3_response.get("parties", ''),
            "court": gpt3_response.get("court", ''),
            "date": gpt3_response.get("date", ''),
          }
        }, 
        upsert=True
      )

      data = {      
        "url": docs[0]['url'],
        "spellCheck": spell,
        "ocr": ocr,
        "cleanedText": clean_t,
        "keywords": keys,   
        "summary": summary,        
        "title": gpt3_response.get("title", ''),
        "parties": gpt3_response.get("parties", ''),
        "court": gpt3_response.get("court", ''),
        "date": gpt3_response.get("date", ''),        
      }
      return message.message_custom(data, 200, "Document updated")    
    except Exception as e:
      print(e)
      return message.message_error(500, str(e), "Internal Server Error")
  except Exception as e:
    print(e)
    return message.message_error(500, str(e), "Internal Server Error")

# Define a route to search for keywords in the database
@app.route("/search", methods=["POST"])
def search_keywords():
  try:
    # Authorization check
    # a = auth.authorize(request, APP_SECRET, NONCE, users_collection)
    # if a['error']:
    #   return message.message_error(a['code'], a['message'], a['err']) 

    top = 5
    order_matters = True

    data = request.json

    flag_use_gpt = False
    try:
      # Get keywords from search string using GPT-3
      if isinstance(data["search_key"], str):
        txt = data["search_key"].split()
        gpt_res = get_judgement(txt)
        search_key = keyword_from_search.keyword_from_search_sentence(gpt_res)
        flag_use_gpt = True
      else:
        search_key = keyword_from_search.keyword_from_search_sentence(data["search_key"])
    except Exception as e:             
      print(e)
      return message.message_error(400, "search_key is a required field", "Bad Request")

    if 'top' in data:
      top = data["top"]
    if 'order_matters' in data and data["order_matters"].lower() == 'false':
      order_matters = False

    # Search for documents containing the keywords in MongoDB
    keywords_dataset_cursor = documents_collection.find({"keywords": { '$in': search_key }})
    items = list(keywords_dataset_cursor)

    docs = {}
    all_docs = {}

    for i in items:
      curr_key = str(i['_id'])
      docs[curr_key] = i['keywords']
      all_docs[curr_key] = i
      all_docs[curr_key]["_id"] = str(all_docs[curr_key]["_id"])
      for elements in all_docs[curr_key]['documents']:
        if "_id" in elements:
          elements["_id"] = str(elements["_id"])

    ranking = {}
    for itr in docs.keys():        
      ranking[itr] = 0

    try:
      for itr in search_key:
        if order_matters:
          helper_ranking.make_ranking(docs, itr, search_key.index(itr), ranking)
        else:
          helper_ranking.make_ranking(docs, itr, 1, ranking)

      sorted_ranking = helper_ranking.sort_dict(ranking)
      top_n_ranked_docs = list(sorted_ranking.keys())[:top]
      top_n_ranked_final = [all_docs[itr] for itr in top_n_ranked_docs]

      if len(top_n_ranked_final) == 0:
        return message.message_error(404, "No documents found", "Not Found")

      data = {
        "docs": top_n_ranked_final,
        "count": len(top_n_ranked_final)
      }
      
      if flag_use_gpt:
        data["gpt_res"] = gpt_res

      return message.message_custom(data, 200, "Successfully searched with the keyword")
    except Exception as e:
      print(e)
      return message.message_error(500, str(e), "Internal Server Error")
  except Exception as e:
    print(e)
    return message.message_error(500, str(e), "Internal Server Error")

# Define a route to get an authorization token
@app.route("/getauthtoken", methods=["POST"])
def get_auth_token():
  try:
    data = request.json

    if not request.json or "username" not in data or "password" not in data:
      return message.message_error(400, "Username and Password are required fields", "Bad Request")

    username = data["username"]
    password = data["password"]

    cursor = users_collection.find({"username": username, "password": password})
    users = list(cursor)

    if len(users) == 0:
      return message.message_error(401, "Invalid Credentials", "Unauthorized")

    key = APP_SECRET.encode('utf-8')
    cipher = AES.new(key, AES.MODE_EAX, nonce=NONCE.encode('utf-8'))

    encr_object = {
      "username": username,
      "expiry": datetime.datetime.timestamp(datetime.datetime.now()) + 60*60*24*5 
    }
    encr_string = json.dumps(encr_object)
    ciphertext, tag = cipher.encrypt_and_digest(encr_string.encode('utf-8'))

    data = {    
      'token': ciphertext.hex(),
      'tag': tag.hex()
    }
    return message.message_custom(data, 200, "Authorization Successful")
  except Exception as e:
    return message.message_error(500, str(e), "Internal Server Error")

# Define a route to upload a document to the database
@app.route('/upload', methods=['POST'])
def upload():
  try:
    # Authorization check
    # a = auth.authorize(request, APP_SECRET, NONCE, users_collection)
    # if a['error']:
    #   return message.message_error(a['code'], a['message'], a['err']) 

    if "user_file" not in request.files:
      return message.message_error(400, "No `user_file` in request", "Bad Request")

    file = request.files["user_file"]
    if file.filename == "":
      return message.message_error(400, "No selected file", "Bad Request")

    if file:
      if file.filename.split('.')[-1] not in ['pdf']:
        return message.message_error(400, "File format not supported", "Bad Request")

      try:
        licenseID = str(request.query_string).split("=")[1].split("\'")[0]
        s3.upload_fileobj(
          file,
          bucket_name,
          file.filename,
          ExtraArgs={                    
              "ContentType": file.content_type 
          }
        ) 
        file_url = "https://{}.s3.amazonaws.com/{}".format(bucket_name, file.filename)

        document = {
          "licenseID": licenseID,
          "documents": [
            {                        
              "url": file_url,
              "fileType": "application/pdf"
            }
          ]
        }
        doc = documents_collection.insert_one(document)

        data = {          
          'licenseID': licenseID,
          'document': document.get('documents')[0],
          'documentID': str(doc.inserted_id)
        }
        return message.message_custom(data, 200, "File uploaded successfully")
      except Exception as e:
        print(traceback.format_exc())        
        return message.message_error(500, str(e), "Internal Server Error")

    else:
      return message.message_error(400, "No file found", "Bad Request")
  except Exception as e:
    return message.message_error(500, str(e), "Internal Server Error")

# Define a route to fetch all documents of a user by license ID
@app.route("/alldocuments", methods=["POST"])
def all_documents():
  try:    
    if not request.json or "licenseID" not in request.json:
      return message.message_error(400, "licenseID is a required field", "Bad Request")

    cursor = documents_collection.find({"licenseID": request.json["licenseID"]}, {"_id": 0})
    items = list(cursor)

    if len(items) == 0:
      return message.message_error(404, "No documents found", "Not Found")

    data = {'docs': items}
    return message.message_custom(data, 200, "Docs fetched for licenseID: " + request.json["licenseID"])
  except Exception as e:
    print(e)
    return message.message_error(500, str(e), "Internal Server Error")

# Run the Flask application
if __name__ == '__main__':
  app.run('0.0.0.0', port=5000, debug=True)
