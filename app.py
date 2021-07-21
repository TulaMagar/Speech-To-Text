from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

# Initialise Flask
app = Flask(__name__)

# Provided credentials to authenticate to a Google Cloud API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\tmaga\\OneDrive\\Desktop\\740comp\\individual project\\Individual-project-68cf1e95bacd.json"

# Temporary storage for uploaded pictures
# to be able to display uploaded pictures they should locate in static directory
UPLOAD_FOLDER = 'resources' 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#  Extension allowed for curtain audio files
ALLOWED_EXTENSIONS = set(['raw', 'wav'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      file = request.files['file']
      if file and allowed_file(file.filename):
         filename = secure_filename(file.filename)
         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
         file.save(filepath)
         Data = search(filepath)
         return render_template('search_results.html',
                    original=filepath,
                    Data=Data)

def search(file_name):
    # Imports the Google Cloud client library
    from google.cloud import speech_v1p1beta1 as speech
    import io
    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    # Loads the audio into memory
    
    with io.open(file_name, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=44100,
        language_code="en-US",
    )

    # [START speech_python_migration_async_response
    operation = client.long_running_recognize(
        request={"config": config, "audio": audio}
    )
    operation = client.long_running_recognize(config=config, audio=audio)

    # print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    Data = []
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        Data.append(result.alternatives[0].transcript)

    return Data
    
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
