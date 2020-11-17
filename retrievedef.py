from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# opts = Options()
# opts.add_argument('log-level=3')
# opts.add_argument('--no-sandbox')
# opts.add_argument('--headless')
# browser = webdriver.Chrome(options=opts)

def getDefinition(word, browser):
    browser.get('https://en.wiktionary.org/wiki/{}'.format(word))
    try:
        orderedlist = browser.find_element_by_tag_name('ol').text
        if "quotations ▼" in orderedlist:
            orderedlist = orderedlist.replace('quotations ▼', '')
    except Exception as e:
        orderedlist = "Error: Could not find definition"
    return orderedlist