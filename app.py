from flask import Flask, render_template, request, redirect, url_for, jsonify
from random import choice, shuffle
import inflect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from retrievedef import getDefinition
from colorama import init
from os import environ

app = Flask(__name__)
browser = ""
init(autoreset=True)
inflect_engine = inflect.engine()

chrome_options = Options()
chrome_options.binary_location = environ.get('GOOGLE_CHROME_BIN')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--headless")
chrome_options.add_argument("log-level=3")

browser = webdriver.Chrome(executable_path=str(environ.get('CHROMEDRIVER_PATH')), options=chrome_options)
# browser = webdriver.Chrome(options=chrome_options)

with open("sowpods.txt", "r") as wordlist:
    english_dict = wordlist.read().splitlines()
    # print("Filtering out hyphenated words...")
    # english_dict = [e for e in english_dict if '-' not in e]
    print("Loading syllables...")
    syllable_list = set()
    for e in english_dict:
        for i in range(len(e)):
            if i < len(e):
                syllable_list.add(e[i-1:i+1])
                syllable_list.add(e[i-2:i+1])

    syllable_list = list(syllable_list)

    print("Filtering out hyphenated syllables...")
    # for s in syllable_list:
    #     if "-" in s:
    #         syllable_list.remove(s)
    syllable_list = [s for s in syllable_list if '-' not in s]
    print("Checking syllable lengths...")
    syllable_list = [s for s in syllable_list if len(s) >= 2 and len(s.strip()) >= 2]

    print("Filter complete!")

print("Collecting sub5 words...")
with open('SUB5.txt', 'r') as sub5s:
    sub5words = sub5s.read().splitlines()
    sub5words = [s.lower() for s in sub5words]

print("Sub5 words loaded!")

def generate_prompt():
    return choice(syllable_list)

@app.route("/lookup", methods=["POST"])
def lookup():
    if request.method == "POST":
        submitted = request.json['term']
        global browser
        justtheterm = submitted[4:]
        if inflect_engine.singular_noun(justtheterm):
            justtheterm_inflected = inflect_engine.singular_noun(justtheterm)
            result = getDefinition(justtheterm_inflected, browser)
        else:
            result = getDefinition(justtheterm, browser)
        return jsonify({"status": "OK", "defText": result, "idText": "body_{}".format(justtheterm)})


@app.route('/', methods=["GET", "POST"])
def index():
    some_syllable = generate_prompt()
    if request.method == "POST":
        userword = request.form['userSuppliedWord'].lower()
        syll = request.form['promptsyll']
        # print(some_syllable in userword)
        if syll not in userword:
            err_code = 'The word did not match the prompt, try again'
            return render_template('index.html', syll=syll, err=err_code, succ=None)
        else:
            if userword not in english_dict:
                err_code = 'Not a valid word!'
                possible_solutions = [e for e in english_dict if syll in e]
                possible_longs = [p for p in possible_solutions if len(p) >= 20]
                possible_longs = possible_longs[:3]
                shuffle(possible_solutions)
                possible_solutions = possible_solutions[:3]

                return render_template('index.html', syll=syll, err=err_code, succ=None, sols=possible_solutions, longs=possible_longs)
            else:
                succ = 'Good job!'
                if userword in sub5words:
                    special = "Rare word!"
                else:
                    special = None
                possible_solutions = [e for e in english_dict if syll in e]
                possible_longs = [p for p in possible_solutions if len(p) >= 20]
                possible_longs = possible_longs[:3]
                return render_template('index.html', syll=some_syllable, err=None, succ=succ, longs=possible_longs, spec=special)
            # err_code = False
            # return redirect(url_for('index', syll=some_syllable))
        # return redirect(url_for('index'))
    else:
        some_syllable = generate_prompt()
        return render_template('index.html', syll=some_syllable, err=None, succ=None)

if __name__ == "__main__":
    # Heroku convention
    port = int(environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)