import selenium
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import collections
import sys

def filter_by_rules(rules,words,correct_indexes,present_indexes):
    valid_words = []
    bad_letters = []
    good_letters = []
    for letter,rule in rules.items():
        if rule == 'absent':
            bad_letters.append(letter.upper())
        elif rule == 'present' or rule == 'correct':
            good_letters.append(letter.upper())
    for word in words:
        is_valid = True
        for bad in bad_letters:
            if bad in word:
                is_valid = False
                break 
        for good in good_letters:
            if good not in word:
                is_valid = False
                break
        for letter,indexes in correct_indexes.items():
            for index in indexes:
                if word[index] != letter:
                    is_valid = False
        for letter, indexes in present_indexes.items():
            for index in indexes:
                if word[index] == letter:
                    is_valid = False
        if is_valid:
            valid_words.append(word)
    
    return valid_words
def get_rules():
    rules = {}
    buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'Key-module_key__kchQI')]")    
    for button in buttons:
        data_state = button.get_attribute('data-state')
        letter = button.get_attribute('data-key')
        if data_state != None:
            rules[letter] = data_state
    return rules
def get_correct_and_present_indexes():
    tile_count = 0
    correct_indexes = collections.defaultdict(list)
    present_indexes = collections.defaultdict(list)
    for tile in driver.find_elements(By.XPATH, "//div[contains(@class, 'Tile-module_tile__UWEHN')]"):
        data_state = tile.get_attribute('data-state')
        letter = tile.text.upper()
        if data_state == 'correct':
            correct_indexes[letter].append(tile_count % 5)
        if data_state == 'present':
            present_indexes[letter].append(tile_count % 5)
        tile_count += 1
    return (correct_indexes, present_indexes)

def get_next_word():
    # scrape tiles
    if not rules:
        # return starting word
        return 'SLATE\n'
    else:
        next_word = words[random.randint(0,len(words)-1)]
        return next_word

if __name__ == '__main__':
    browser = input('which browser do you use? (firefox,chrome,edge) ')
    if browser.lower() == 'firefox':
        driver = webdriver.Firefox()
    elif browser.lower() == 'chrome':
        driver = webdriver.Chrome()
    elif browser == 'edge':
        driver = webdriver.Edge()
    else:
        print(f'{browser} not supported by this app')
        sys.exit(1)

    # load all 5-letter words from dictionary file
    with open('five_upper') as f:
        words = f.readlines()
    # open url
    driver.get("https://www.nytimes.com/games/wordle/index.html")
    sleep(2)
    # get keys to press 
    keys = driver.find_elements(By.XPATH, '//button[@class="Key-module_key__kchQI"]')
    c = driver.find_element(By.TAG_NAME, 'path')
    sleep(1)
    c.click()
    # get enter key, press after each word
    enter_key = driver.find_element(By.XPATH, "//button[text()='enter']")
    while True:
        (correct_indexes, present_indexes) = get_correct_and_present_indexes()
        rules = get_rules()
        words = filter_by_rules(rules,words,correct_indexes, present_indexes)
        for next_letter in get_next_word():
            for key in keys:
                if key.text == next_letter:
                    key.click()
                if next_letter == '\n':
                    enter_key.click()
                    sleep(1.7)
                    break
        stats = driver.find_elements(By.CLASS_NAME, "Stats-module_statisticsHeading__CExdL")
