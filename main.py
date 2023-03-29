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
    print(f"good letter//div[contains(@class, 'foo')]s: {good_letters}")
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


def get_next_word():
    # load all 5-letter words from dictionary file
    with open('five_upper') as f:
        words = f.readlines()
    # find the lowest row that gives rules
    rules = {}
    buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'Key-module_key__kchQI')]")    
    for button in buttons:
        data_state = button.get_attribute('data-state')
        letter = button.get_attribute('data-key')
        if data_state != None:
            rules[letter] = data_state
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
    if not rules:
        # return starting word
        return 'SLATE\n'
    else:
        print(rules)
        valid_words = filter_by_rules(rules,words,correct_indexes,present_indexes)
    # pick random (or other strategy) word from remaining valid words
    next_word = valid_words[random.randint(0,len(valid_words)-1)]
    print(f'next word is: {next_word}')
    return next_word
    # repeat until game is over

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
    driver.get("https://www.nytimes.com/games/wordle/index.html")
    #driver.get('https://wordleunlimited.org/')
    sleep(2)
    keys = driver.find_elements(By.XPATH, '//button[@class="Key-module_key__kchQI"]')
    # <dialog class="Modal-module_modalOverlay__cdZDa Modal-module_paddingTop__xhWdR">
    # close initial pop-up, need to click anywhere on the screen
    c = driver.find_element(By.TAG_NAME, 'path')
    sleep(1)
    c.click()
    enter_key = driver.find_element(By.XPATH, "//button[text()='enter']")
    start_words = ["audio", "pious", "radio", "slate"]
    while True:
        for next_letter in get_next_word():
            for key in keys:
                if key.text == next_letter:
                    key.click()
                if next_letter == '\n':
                    enter_key.click()
                    sleep(3)
                    break
                
    driver.close()
