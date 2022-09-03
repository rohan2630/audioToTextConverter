# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 11:53:47 2022

@author: Rohan Mathur
"""
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_EXTENSIONS'] = ['.mp3' ]
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['SECRET_KEY'] = "supersecretkey"

@app.route('/')
def home():
    return render_template('audio.html')

@app.route('/', methods=['POST'])
def upload():
    my_files = request.files    
    for item in my_files:
        uploaded_file = my_files.get(item)
        uploaded_file.filename = secure_filename(uploaded_file.filename)
    audFiles = [val for sublist in [[os.path.join(i[0], j) for j in i[2] if j.endswith('.mp3')] for i in os.walk('./')] for val in sublist]
    for i in audFiles:
        os.remove(i)
    uploaded_file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(uploaded_file.filename)))
    
    return redirect(url_for('output'))
    
@app.route('/output')
def output():
    apikey = 'iIqfbQH_dlc6EGpEiYZ4U2u2_i1qPYN1vSre2K0erQsi'
    url = 'https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/fb9a94df-c40f-4822-9e49-24fac4d9bf1e'

    authenticator = IAMAuthenticator(apikey)
    stt = SpeechToTextV1(authenticator = authenticator)
    stt.set_service_url(url)
    
    audFiles = [val for sublist in [[os.path.join(i[0], j) for j in i[2] if j.endswith('.mp3')] for i in os.walk('./')] for val in sublist]
    for i in audFiles:
        results = []
        with open(i, 'rb') as audF:
            res = stt.recognize(audio=audF, content_type='audio/mp3', model='en-US_NarrowbandModel', inactivity_timeout=360).get_result()
            results.append(res)
            
    text = []
    for file in results:
        for result in file['results']:
            text.append(result['alternatives'][0]['transcript'].rstrip() + '.\n')
    text = ''.join(text).replace('%HESITATION', '')
    with open('static/files/output.txt', 'w') as out:
        out.write(text)
    return render_template('output.html', text=text)

if __name__ == '__main__':
    app.run(debug=True)