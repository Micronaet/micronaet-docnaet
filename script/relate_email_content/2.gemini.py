# pip install -q -U google-generativeai

import pdb
import os
import google.generativeai as genai

import pathlib
import textwrap
# from IPython.display import display
# from IPython.display import Markdown
# def to_markdown(text):
#  text = text.replace('•', '  *')
#  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Used to securely store your API key
# from google.colab import userdata
# genai.configure(api_key='...')
# GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')

# bash: export GOOGLE_API_KEY="..."

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# %%time
text = "Testo da riassumere"
words = 50
request = \
    'Riassumi in italiano con meno di {words} parole il testo: {text}'.format(
        text=text,
        words=words
    )

pdb.set_trace()
response = model.generate_content(request)
try:
    response_text = response.text
    print(response_text)
except Exception as e:
    print(e)
    # print(f'{type(e).__name__}: {e}')

# response.prompt_feedback
