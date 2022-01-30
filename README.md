# wordle-ai
Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI

Includes a Command Line version of the [Wordle Game](https://www.powerlanguage.co.uk/wordle/)

You get 6 tries to guess a 5 letter word. Each guess you make you will get feedback on each letter. 
I.E. Whether it is in the answer word and in the right position, whether it is in the answer word and in the wrong position, or it is not in the answer word.

## Dependencies
If you wish to run this you will need to install

Tesseract-OCR for [here](https://github.com/tesseract-ocr/tesseract)

Python packages:
 - pytesseract
 - pynput
 - numpy
 - opencv-python
 - pillow
 - alive-progress

which could be done with `python -m pip install pytesseract pynput numpy opencv-python pillow alive-progress`

you might have to change `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'` at the top of wordle_ai_utils.py (line 7) to where youre tesseract.exe was installed to if it is not on your PATH
