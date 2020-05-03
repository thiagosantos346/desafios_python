from http import HTTPStatus
from http.client import HTTPException
import requests
import http
import hashlib
import json

def get_http_connection(host):
  try:
    connection = http.client.HTTPSConnection(host)
    return connection
  except HTTPException as e:
    raise(e)

def fetch(connection, url, body=None, headers={}, encode_chunked=False ):
  try:
    
    connection.request('GET', url=url, body=body, headers=headers, encode_chunked=encode_chunked)
    response = connection.getresponse()

    if response.status == 200 :
      return response
  except HTTPException as e:
    print(e)
    return -1
  print(response.status)
  return -1

def fetchJSON(host, url):
  connection = get_http_connection(host)
  response = fetch(connection, url)

  if response.status == 200 :
    response_data = response.readlines()
    response_data_json = json.loads(response_data[0])
    return response_data_json

  return -1

def stdioFile(path, name, values, operation):
  full_path = str(path+name)

  with open(full_path, operation) as fileObject:
    if operation == 'r' :
      result = fileObject.read(values)
    if operation in ('w', 'a')  :
      result = fileObject.write(values)

    if not fileObject.closed :
      fileObject.close()
  
  return result

def decrypt( word, shift, dic ):
  
  new_word = str('')

  for letter in word:
    position = dic.find(letter)
    if position == -1:
       new_word += letter
    else :
      new_position = position + shift
      if new_position > len(dic) :
        new_position = len(dic) - (new_position % len(dic))
      new_word  += dic[new_position]

  return new_word

def upload(path, filename, full_url):

  try:
    response = requests.post(url = full_url, files = {'answer': open(path+filename, 'rb') })
    print(response.status_code)
    print(response.json)
    print(response.text)
    print(response.headers)
  except Exception as e:
    print(e)

def main():

  #variables
  LOCAL_CONSTS = {
    "data_output" : "./tk/",
    "api_key" : "tk.txt",
    'host' : 'api.codenation.dev',
    'url_get' : '/v1/challenge/dev-ps/generate-data?token={SEU_TOKEN}',
    'url_post' : '/v1/challenge/dev-ps/submit-solution?token={SEU_TOKEN}',
    'dic' : 'abcdefghijklmnopqrstuvwxyz',
    'file_name' : 'answer.json'
  }
  token = stdioFile(LOCAL_CONSTS['data_output'], LOCAL_CONSTS['api_key']  , None , 'r')
  url_get = LOCAL_CONSTS['url_get'].format(SEU_TOKEN=token)
  full_url_post = 'https://'+LOCAL_CONSTS['host']+LOCAL_CONSTS['url_post'].format(SEU_TOKEN=token)

  #in
  response_data_json = fetchJSON(LOCAL_CONSTS['host'], url_get)

  #transform
  decrypited = decrypt(response_data_json['cifrado'], -12, LOCAL_CONSTS['dic'])
  decrypited_utf8 = str(decrypited).encode('utf-8')
  resume = hashlib.sha1(decrypited_utf8).hexdigest()

  #out
  response_data_json['decifrado'] = decrypited
  response_data_json['resumo_criptografico'] = resume
  str_response_data_json = str(response_data_json)
  str_response_data_json = str_response_data_json.replace("\'", '\"')
  stdioFile(LOCAL_CONSTS['data_output'], LOCAL_CONSTS['file_name']  , str_response_data_json, 'w')
  stdioFile(LOCAL_CONSTS['data_output'], LOCAL_CONSTS['file_name']  , None , 'r')
  
  #upload 
  file_path =LOCAL_CONSTS['data_output']+LOCAL_CONSTS['file_name']
  upload(LOCAL_CONSTS['data_output'],  LOCAL_CONSTS['file_name'] ,full_url_post)

if __name__=="__main__":
  main()
