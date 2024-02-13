## Imports
from io import BytesIO
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

## Loading the manually curated stopwords from json file
final_stop = json.load(open("stopwords.json", "r"))['stopwords']

## Configuring Spacy
nlp = spacy.load("en_core_web_sm")

## OCR Detection Module
def return_string_from_path(file):
  ## converts pdf to images
  images = convert_from_bytes(file, size=800)

  list1 = []
  for i, image in enumerate(images):
    ## OCR Detection using pytesseract
    list1.append(pytesseract.image_to_string(image, lang='eng'))

  ## Getting the final string
  string = " ".join(list1)

  return string.strip()

## Spell Correction Module
def spell_check(text):
  ## Spell Correction using TextBlob
  text = str(TextBlob(text).correct())
  text = text.strip()
  return text

## Manual Keyword Extraction Module
def check_manual_keywords(text):
  text = text.lower()
  manual_keywords_check= []

  ## tokenizing the text
  li = word_tokenize(text)
  manual_keywords = ["annexure", "section", "article"]

  ## Checking if the manual keywords are present in the text
  ## Basically for strings like "Article 14" or "Section 377"
  for i in range(0, len(li)):    
    if(li[i] in manual_keywords):
      element_tbi = li[i]+"-"+li[i+1]
      try:
        ## Checking if the next word is a number
        numb = float(li[i+1])
      except:
        continue

      ## Checking if the element is already present in the list
      if(element_tbi not in manual_keywords_check):
        ## Appending the element to the list 
        manual_keywords_check.append(element_tbi)      

  return manual_keywords_check

## Preprocessing Module 
def distill_string(final_string):
  ## COnverting to lower case and removing special characters
  final_string = final_string.lower()
  final_string = re.sub(r'(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?', '', final_string)
  
  ## Extracting Manual Keywords
  manual_keywords = ["annexure", "section", "article"]
  for item in manual_keywords:
    final_string.replace(item+" ", item+"-")
  final_string = re.sub(' +', ' ', final_string)

  ## Removing maually curated keywords
  for item in final_stop:
    final_string = final_string.replace(item, "")

  ## Lemmatizing the text 
  empty_list = []
  for token in nlp(final_string):
      empty_list.append(token.lemma_)
  final_string = ' '.join(map(str,empty_list))

  ## Removing non-English words
  word_list_en = []
  for word in word_tokenize(final_string):
    ## Checks if the word is present in the wordfreq library
    if(zipf_frequency(word, 'en', wordlist='best') > 3.3):## 3.3 is the threshold
      word_list_en.append(word)
  final_string = " ".join(word_list_en)
  
  ## Spell-correcting the remaining text
  final_string = re.sub(' +', ' ', final_string)
  final_string = str(TextBlob(final_string).correct())

  ## Returning the final string
  return final_string


## Keyword Extraction Module
def return_keyword(para, number):
  ## Extracting keywords using YAKE considering single word keywords
  kw_extractor = KeywordExtractor(lan="en", n=1, top=number)
  list_of_keywords = kw_extractor.extract_keywords(text=para)

  final_list = [itr[0] for itr in list_of_keywords]
  return final_list