## Imports
from flask import Flask, app, request
import boto3, botocore
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
from yake import KeywordExtractor
import re
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
import json
from flask_cors import CORS
from utils.extract_summary import make_summary
from utils.gpt_text_generation import get_judgement, get_title_date_parties
import traceback

## Getting ENV variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
APP_SECRET = os.getenv("APP_SECRET")
NONCE = os.getenv("NONCE")

## Creating Flask app
app = Flask(__name__) 

## Enabling CORS
CORS(app)

## Configuring Logging for the app
logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

## Connecting to MongoDB
client = pym.MongoClient(MONGO_URI)
db = client["diversion"]
documents_collection = db["documents"]
users_collection = db["users"]

## Configuring Spacy
nlp = spacy.load("en_core_web_sm")

## Configuring Boto3 to read from S3
bucket_name = BUCKET_NAME
s3=boto3.client("s3", region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

## Loading the manually curated keywords from json file
final_stop = json.load(open("stopwords.json", "r"))['stopwords']

"""
Testing Route
-----
get:
  description: Testing Route to check if the server is running
  responses:
    {Success}
    message (string): success message
"""
@app.route("/", methods=["GET"])
def default():  
  return message.message(200, "Welcome to the eFaisla API")


"""
Autocomplete Route
-----
get:
  description: Get all the keywords for autocomplete suggestions
  security:
    headers:
      {Required}
      - token (string) : token
      - tag (string) : tag
  request:
    {Optional}
    - limit (int) : Number of keywords to be returned
    - sort (true/false): Sort the keywords in ascending order
  responses:
    {Success}
    - keywords (list) : List of keywords
    - count (int) : Number of keywords
    - sort (true/false) : Sort the keywords in ascending order
    - limit (int) : Limit if specified
    {Error}
    - message (string) : Error message    
"""
@app.route("/autocomplete", methods=["GET"])
def autocomplete():
  try:
    ## Authorization check

    # a = auth.authorize(request, APP_SECRET, NONCE, users_collection)
    # if a['error'] == True:
    #   ## returning error if authorization fails
    #   return message.message_error(a['code'], a['message'], a['err']) 

    limit = -1
    sort = False

    ## getting the query parameters
    if 'limit' in request.args:
      limit = int(request.args['limit'])

    if 'sort' in request.args:
      sort = str(request.args['sort'])

    # getting all the documents with keywords
    cursor = documents_collection.find({"keywords": { '$exists': True }})
    items = list(cursor)
    total_keywords = []
    c = 0

    ## getting all the keywords from the documents
    for i in items:
      total_keywords += i['keywords']  

    ## removing duplicates
    unique_keywords = list(set(total_keywords))

    ## limiting the number of keywords
    unique_keywords = unique_keywords[:limit] 

    ## sorting the keywords if specified
    if sort.lower() == 'true':
      unique_keywords = sorted(unique_keywords)

    data = {
      'keywords':unique_keywords,
      'count':len(unique_keywords),
      'sort':sort
    }

    if limit != -1:
      data['limit'] = limit

    return message.message_custom(data, 200, "Keywords for autocomplete") 
  except Exception as e:
    return message.message_error(500, e, "Internal Server Error")


"""
Update Keywords Route
-----
post:
  description: Preprocess and update the clean text and keywords for a document
  security:
    headers:
      {Required}
      - token (string) : token
      - tag (string) : tag
  request:
    {Required}
    - id (string) : MongoDB ID of the document
    {Optional}
    - spell (true/false) : Spell check the extracted text
  responses:
    {Success}
    - url (string) : URL of the document
    - spellCheck (true): if spell check is performed
    - ocr (true/false): if ocr is performed
    - keywords (list): list of keywords found in the document
    - cleanText (string): cleaned extracted text from the document
    {Error}
    - message (string) : Error message
"""
@app.route("/update", methods=["POST"])
def add_keyword_and_cleantext():
  try:
    ## Authorization check

    # a = auth.authorize(request, APP_SECRET, NONCE, users_collection)
    # if a['error'] == True:
    #   ## returning error if authorization fails
    #   return message.message_error(a['code'], a['message'], a['err']) 

    spell = False
    ocr = False

    try:
      ## getting the query parameters
      id = request.json['id']
    except:
      ## returning error if id is not specified
      return message.message_error(400, "ID is a Required field", "Bad Request")


    ## checking if spell check is specified
    if 'spell' in request.json and request.json['spell'].lower() == 'true':
      spell = True

    try:
      ## fetching the document from the database
      docs = documents_collection.find_one({"_id": ObjectId(id)})['documents']
    except:
      return message.message_error(404, "Document not found", "Not Found")
    
    try:    
      clean_t = ""
      for doc in docs:
        ## Fetching the document from S3 bucket
        obj = s3.get_object(Bucket=bucket_name, Key=doc['url'].split("/")[-1])

        ## Reading the fetched document 
        fs = obj['Body'].read()            
        pdfReader = PyPDF2.PdfFileReader(io.BytesIO(fs)) 

        ## Checking if the document is readable or not
        if(len(pdfReader.getPage(0).extractText()) == 0):
          ## If not readable, performing OCR Detection
          ocr = True
          clean_t = clean_t + helper_update.return_string_from_path(fs)
        else:
          ## If readable, extracting the text                
          pdfReader = PyPDF2.PdfFileReader(io.BytesIO(fs)) 
          for i in range(0,pdfReader.numPages):
            clean_t = clean_t + pdfReader.getPage(i).extractText()
          clean_t = clean_t.replace("\n", " ")
    except Exception as e:
      print(e)
      ## returning error if the document is not found
      return message.message_error(500, "Error in reading the file", "Internal Server Error")
      
    
    ## Correcting the spelling if specified
    if spell == True:
      clean_t = helper_update.spell_check(clean_t)

    ## Extracting Manual Keywords
    keywords_manual = helper_update.check_manual_keywords(clean_t)

    ## Removing Symbols + hyphens + stop words + lemmatizing + removing non-english words
    keyword_corpus = helper_update.distill_string(clean_t)  

    ## Extracting the keywords from the corpus
    key = helper_update.return_keyword(keyword_corpus, 30)

    ## Adding the manual and extracted keywords
    keys = keywords_manual + key
    
    ## Summarizing using Cohere
    summary = make_summary(clean_t)
    
    ## Extracting title, etc from the document
    txt = " ".join(clean_t.split(" ")[:300])
    gpt3_response = get_title_date_parties(txt)
    # print(gpt3_response)
    try:
      ## Updating the document in the database
      documents_collection.update_one(
        {"_id": ObjectId(id)}, 
        {
          '$set': {
            "keywords": keys, 
            "cleanText": clean_t, 
            "summary": summary,
            "title": gpt3_response["title"] if 'title' in gpt3_response else '',
            "parties": gpt3_response["parties"] if 'parties' in gpt3_response else '',
            "court": gpt3_response["court"] if 'court' in gpt3_response else '',
            "date": gpt3_response["date"] if 'date' in gpt3_response else '',
            }
        }, 
        upsert= True
      )

      data = {      
        "url": docs[0]['url'],
        "spellCheck": spell,
        "ocr": ocr,
        "cleanedText": clean_t,
        "keywords": keys,   
        "summary": summary,        
        "title": gpt3_response["title"] if 'title' in gpt3_response else '',
        "parties": gpt3_response["parties"] if 'parties' in gpt3_response else '',
        "court": gpt3_response["court"] if 'court' in gpt3_response else '',
        "date": gpt3_response["date"] if 'date' in gpt3_response else '',        
      }
      return message.message_custom(data, 200, "Document updated")    
    except Exception as e:      
      print(e)
      return message.message_error(500, e, "Internal Server Error")
  except Exception as e:
    print(e)
    return message.message_error(500, e, "Internal Server Error")


"""
Search Route
-----
post:
  description: Search for a keyword in the database
  security:
    headers:
      {Required}
      - token (string) : token
      - tag (string) : tag
  request:
    {Required}
    - search_key (list(string)) : Keyword to be searched
    {Optional}
    - top (int) : Number of documents to be returned
    - order_matters (true/false) : If the order of the keywords entered matters
  responses:
    {Success}
    - docs:
      - {Schema of the document} (array of objects): List of documents
    - count (int) : Number of documents
    {Error}
    - message (string) : Error message
"""
@app.route("/search", methods=["POST"])
def search_keywords():
  try:
    ## Authorization check

    # a = auth.authorize(request, APP_SECRET, NONCE, users_collection)
    # if a['error'] == True:
    #   ## returning error if authorization fails
    #   return message.message_error(a['code'], a['message'], a['err']) 

    top = 5
    order_matters = True

    data = request.json
    # try:
    #   ## getting the query parameters
    #   search_key = data["search_key"]  
    # except:
    #   return message.message_error(400, "search_key is Required field", "Bad Request")

    flag_use_gpt = False
    try:
      # added to get keyword from sentence      
      if type(data["search_key"]) == str:
        # get first 300 words        
        txt = data["search_key"].split()
        gpt_res = get_judgement(txt)        
        
        search_key = keyword_from_search.keyword_from_search_sentence(gpt_res)        
        print(gpt_res, search_key)
        flag_use_gpt = True
      else:
        search_key = keyword_from_search.keyword_from_search_sentence(data["search_key"])
    except Exception as e:             
      print(e)
      return message.message_error(400, "search_key is Required field", "Bad Request")

    if 'top' in data:
      top = data["top"]  
    ## checking if order matters is specified
    if 'order_matters' in data and data["order_matters"].lower() == 'false':
      order_matters = False
      
    ## Searching for the keywords in the database
    keywords_dataset_cursor = documents_collection.find({"keywords": { '$in': search_key} })
    items = list(keywords_dataset_cursor)

    ## docs is the dictionary of only keywords with _id as key
    docs = {}
    ## all_docs is the list of all documents that contain the keywords with _id as key
    all_docs = {}

    ## Iterating through all the documents
    for i in items:
      curr_key = str(i['_id'])

      ## Adding the document to all_docs
      docs[curr_key] = i['keywords']
      all_docs[curr_key] = i

      ## Converting the _id to string
      all_docs[curr_key]["_id"] = str(all_docs[curr_key]["_id"])
      for elements in all_docs[curr_key]['documents']:
        if "_id" in elements:
          elements["_id"] = str(elements["_id"])

    ## Ranking is a dictionary of _id as key and the number of keywords multiplied by importance matched as value
    ranking = {}
    ## Setting the initial value of ranking to 0
    for itr in docs.keys():        
      ranking[itr] = 0

    try:
      ## Iterating through all the keywords
      for itr in search_key :
        if order_matters == True:
          ## If order matters, then the keywords should be in the same order as entered
          helper_ranking.make_ranking(docs, itr, search_key.index(itr), ranking)
        else :
          ## If order does not matter, then the keywords can be in any order
          helper_ranking.make_ranking(docs, itr, 1, ranking)

      ## Sorting the ranking dictionary in descending order
      sorted_ranking = helper_ranking.sort_dict(ranking)

      ## Returning the top documents
      top_n_ranked_docs = (list(sorted_ranking.keys()))[:top]

      top_n_ranked_final = []
      ## Adding the documents to the final list
      for itr in top_n_ranked_docs:      
        top_n_ranked_final.append(all_docs[itr])

      ## IF no documents are found
      if len(top_n_ranked_final) == 0:
        return message.message_error(404, "No documents found", "Not Found")
        
      ## Returning the documents
      data = {
        "docs": top_n_ranked_final,
        "count": len(top_n_ranked_final)
      }
      
      if(flag_use_gpt == True):
        data["gpt_res"] = gpt_res
      
      return message.message_custom(data, 200, "Successefully searched with the keyword")
    except Exception as e:
      print(e)
      return message.message_error(500, e, "Internal Server Error")
  except Exception as e:
    print(e)
    return message.message_error(500, e, "Internal Server Error")


"""
Get Token Route
-----
post:
  description: Get token and auth for authorization to other routes
  request:
    {Required}
    - username (string) : Username of the user
    - password (string) : Password of the user    
  responses:
    {Success}
    - token (string) : Token for authorization
    - tag (string) : Tag for authorization
    {Error}
    - message (string) : Error message
"""
@app.route("/getauthtoken", methods=["POST"])
def get_auth_token():
  try:
    data = request.json

    ## Checking if the username and password are present
    if not request.json or "username" not in data or "password" not in data:
      return message.message_error(400, "Username and Password are Required fields", "Bad Request")

    username = data["username"]
    password = data["password"]
    
    ## Checking if the user exists in the mongo database
    cursor = users_collection.find({"username": username, "password": password})
    users = list(cursor)

    if len(users) == 0:
      ## If the user does not exist, return error
      return message.message_error(401, "Invalid Credentials", "Unauthorized")
    
    ## If the user exists, generate a token and tag
    key = APP_SECRET.encode('utf-8')# secret is required to be bytes
    ## Generating the token using AES encryption
    cipher = AES.new(key, AES.MODE_EAX, nonce=NONCE.encode('utf-8'))# nonce is required to be bytes

    ## Creating the object to be encrypted
    encr_object = {
      "username": username,
      "expiry": datetime.datetime.timestamp(datetime.datetime.now()) + 60*60*24*5 
    }
    ## Convert the object to string
    encr_string = json.dumps(encr_object)
    ## Encrypting the username
    ciphertext, tag = cipher.encrypt_and_digest(encr_string.encode('utf-8'))        

    ## Returning the token and tag
    data = {    
      'token':ciphertext.hex(),
      'tag':tag.hex()
    }
    return message.message_custom(data, 200, "Authorization Successful")
  except Exception as e:
    return message.message_error(500, e, "Internal Server Error")


"""
Upload document Route
-----
post:
  description: Upload a document to the database
  security:
    headers:
      {Required}
      - token (string) : token
      - tag (string) : tag
  request:
    {Required}
    - file (file) : File to be uploaded
  responses:
    {Success}
    - document (object) : Document object
    - documentID (string) : ID of the document
    - licenseID (string) : license ID of the user
    {Error}
    - message (string) : Error message
"""
@app.route('/upload', methods=['POST'])
def upload():
  try:
    ## Authorization check
    
    # a = auth.authorize(request, APP_SECRET, NONCE, users_collection)
    # if a['error'] == True:
    #   ## returning error if authorization fails
    #   return message.message_error(a['code'], a['message'], a['err']) 

    ## Checking if the file is present
    if "user_file" not in request.files:
      return message.message_error(400, "No `user_file` in request", "Bad Request")

    file = request.files["user_file"]
    ## Checking if the file name is present
    if file.filename == "":
      return message.message_error(400, "No selected file", "Bad Request")

    if file:
      ## Checking if the file is a pdf
      if file.filename.split('.')[-1] not in ['pdf']:
        return message.message_error(400, "File format not supported", "Bad Request")

      try:
        licenseID = str(request.query_string).split("=")[1].split("\'")[0]
        ## Uploading the file to AWS S3 bucket
        s3.upload_fileobj(
          file,
          bucket_name,
          file.filename,
          ExtraArgs={                    
              "ContentType": file.content_type 
          }
        ) 
        ## Getting the file url
        file_url = "https://{}.s3.amazonaws.com/{}".format(bucket_name, file.filename)
        ## Getting the licenseID of the user
        
        #licenseID = request.params['licenseID']
        #a['licenseID']
        
        document = {
          "licenseID": licenseID,
          "documents":[
              {                        
                "url": file_url,
                "fileType": "application/pdf"
              }
          ]
        }
        ## Inserting the document to the mongo database
        doc = documents_collection.insert_one(document)

        ## Returning the document object and the documentID
        data = {          
          'licenseID':licenseID,
          'document':document.get('documents')[0],
          'documentID':str(doc.inserted_id)
        }
        return message.message_custom(data, 200, "File uploaded successfully")
      except Exception as e:
        print(traceback.format_exc())        
        return message.message_error(500, str(e), "Internal Server Error")

    else:
      return message.message_error(400, "No file found", "Bad Request")
  except Exception as e:
    return message.message_error(500, e, "Internal Server Error")

## Fetch all the documents of a user by licenseID
@app.route("/alldocuments", methods=["POST"])
def all_documents():
  try:    
    if not request.json or "licenseID" not in request.json:
      return message.message_error(400, "licenseID is a Required field", "Bad Request")
    
    # only remove _id
    cursor = documents_collection.find({"licenseID": request.json["licenseID"]} , {"_id": 0})
    items = list(cursor)
    
    if len(items) == 0:
      return message.message_error(404, "No documents found", "Not Found")
    
    data = {}
    data['docs'] = items
    
    return message.message_custom(data, 200, "Docs fetched for licenseID: " + request.json["licenseID"])
      
  except Exception as e:
    print(e)
    return message.message_error(500, e, "Internal Server Error")
    
if __name__ == '__main__':
  app.run('0.0.0.0',port=5000, debug=True)