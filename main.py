import selenium
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import collections
import sys

def filter_by_rules(rules,words,correct_indexes,present_indexes,counts):
    valid_words = []
    bad_letters = []
    for letter,rule in rules.items():
        if rule == 'absent':
            bad_letters.append(letter.upper())
    for word in words:
        is_valid = True
        for char,count in counts.items():
            if word.count(char) < count:
                is_valid = False
                break
        for bad in bad_letters:
            if bad in word:
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
    last_row = []
    next_row = []
    for tile in driver.find_elements(By.XPATH, "//div[contains(@class, 'Tile-module_tile__UWEHN')]"):
        data_state = tile.get_attribute('data-state')
        letter = tile.text.upper()
        next_row.append((letter,data_state))
        if data_state == 'correct':
            correct_indexes[letter].append(tile_count % 5)
        if data_state == 'present':
            present_indexes[letter].append(tile_count % 5)
        if tile_count != 0 and tile_count % 5 == 0 and next_row[0][1] != 'empty':
            last_row = next_row
            next_row = [(letter,data_state)]
        tile_count += 1
    counts = collections.Counter([each[0] for each in last_row if each[1] == 'present' or each[1] == 'correct'] )
    print(counts)
    return (correct_indexes, present_indexes, counts)

def get_next_word():
    # scrape tiles
    if not rules:
        # return starting word
        return ['SLATE\n', 'AUDIO\n', 'PIOUS\n'][random.randint(0,2)]
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
    # get backspace buton
    backspace_key = driver.find_element(By.XPATH, "//button[@aria-label='backspace']")
    while True:
        (correct_indexes, present_indexes,counts) = get_correct_and_present_indexes()
        rules = get_rules()
        words = filter_by_rules(rules,words,correct_indexes, present_indexes,counts)
        for next_letter in get_next_word():
            for key in keys:
                if key.text == next_letter:
                    key.click()
                if next_letter == '\n':
                    enter_key.click()
                    for _ in range(5):
                        backspace_key.click()
                    sleep(1.4)
                    break
        stats = driver.find_elements(By.CLASS_NAME, "Stats-module_statisticsHeading__CExdL")
