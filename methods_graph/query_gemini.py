import os
import time
import google.generativeai as genai
from decouple import config


API_KEY = config('GEMINI_API_KEY')
genai.configure(api_key=API_KEY)

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def wait_for_files_active(files):
  """Waits for the given files to be active.

  Some files uploaded to the Gemini API need to be processed before they can be
  used as prompt inputs. The status can be seen by querying the file's "state"
  field.

  This implementation uses a simple blocking polling loop. Production code
  should probably employ a more sophisticated approach.
  """
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

def recursive_call_to_gemini_10_attempts(chat_session, message):
    if not hasattr(recursive_call_to_gemini_10_attempts, "counter"):
        recursive_call_to_gemini_10_attempts.counter = 0
    if recursive_call_to_gemini_10_attempts.counter == 10:
        return None
    try:
        response = chat_session.send_message(message)
        return response
    except Exception as e:
        print(f"Error: {e}")
        recursive_call_to_gemini_10_attempts.counter += 1
        # add a delay to avoid rate limiting
        time.sleep(1)
        return recursive_call_to_gemini_10_attempts(chat_session, message)

for pdf in os.listdir("data/PDFs"):
    files = [
    upload_to_gemini(
        f"data/PDFs/{pdf}",
        mime_type="application/pdf"),
    ]

    # Some files have a processing delay. Wait for them to be ready.
    wait_for_files_active(files)

    chat_session = model.start_chat()

    message = "I have attached a PDF file. Could you please summarize the content of the methods section?"
    response = recursive_call_to_gemini_10_attempts(chat_session, message)

    print(response.text)