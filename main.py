import selenium
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import collections
import sys


def filter_by_rules(
    bad_letters, words, correct_indexes, present_indexes, absent_indexes, counts
):
    """
    takes in bad_letters (letters not in answer), words (all words),
    correct_indexes ( dict associating letters to index of correct), present_indexes (dict associating letters to index of correct),
    counts (dict counting known occurances of letter in answer)
    returns a list of valid words according to the above rules
    """
    valid_words = []
    for word in words:
        is_valid = True
        for char, count in counts.items():
            if word.count(char) < count:
                is_valid = False
                break
        for bad in bad_letters:
            if bad in word:
                is_valid = False
                break
        for letter, indexes in absent_indexes.items():
            for index in indexes:
                if word[index] == letter:
                    is_valid = False
                    break
        for letter, indexes in correct_indexes.items():
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


def get_absent_letters():
    """
    scrape page to get list of words that are not in answer
    """
    absent_letters = set()
    buttons = driver.find_elements(
        By.XPATH, "//button[contains(@class, 'Key-module_key__kchQI')]"
    )
    for button in buttons:
        data_state = button.get_attribute("data-state")
        letter = button.get_attribute("data-key").upper()
        if data_state and data_state == "absent":
            absent_letters.add(letter)
    return absent_letters


def get_correct_present_and_absent_indexes():
    """
    scrape page and get correct and present indexes
    """
    tile_count = 0
    correct_indexes = collections.defaultdict(list)
    present_indexes = collections.defaultdict(list)
    absent_indexes = collections.defaultdict(list)
    last_row = []
    next_row = []
    all_tiles = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(@class, 'Tile-module_tile__UWEHN')]")
        )
    )
    for tile in all_tiles:
        data_state = tile.get_attribute("data-state")
        letter = tile.text.upper()
        next_row.append((letter, data_state))
        if data_state == "correct":
            correct_indexes[letter].append(tile_count % 5)
        if data_state == "present":
            present_indexes[letter].append(tile_count % 5)
        if data_state == "absent":
            absent_indexes[letter].append(tile_count % 5)
        if tile_count != 0 and tile_count % 5 == 0 and next_row[0][1] != "empty":
            last_row = next_row
            next_row = [(letter, data_state)]
        tile_count += 1
    counts = collections.Counter(
        [each[0] for each in last_row if each[1] == "present" or each[1] == "correct"]
    )
    return (correct_indexes, present_indexes, absent_indexes, counts)


def get_next_word():
    """
    return next guess.
    """
    # scrape tiles
    if not absent_letters and not correct_indexes and not present_indexes:
        # return starting word
        return ["SLATE\n", "CRANE\n", "SALET\n"][random.randint(0, 2)]
    else:
        next_word = words[random.randint(0, len(words) - 1)]
        return next_word


if __name__ == "__main__":
    browser = input("which browser do you use? (firefox,chrome,edge) ").strip()
    if browser.lower() == "firefox":
        driver = webdriver.Firefox()
    elif browser.lower() == "chrome":
        driver = webdriver.Chrome()
    elif browser == "edge":
        driver = webdriver.Edge()
    else:
        print(f"{browser} not supported by this app")
        sys.exit(1)
    try:
        # load all 5-letter words from dictionary file
        with open("five_upper") as f:
            words = f.readlines()
        # open url
        if len(sys.argv) == 1:
            driver.get("https://www.nytimes.com/games/wordle/index.html")
            purr_blocker_btn = driver.find_element(
                By.CLASS_NAME, "purr-blocker-card__button"
            ).click()
            play_button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (
                        (
                            By.XPATH,
                            '//button[@class="Welcome-module_button__ZG0Zh" and text()="Play"]',
                        )
                    )
                )
            )
            play_button.click()
            c = driver.find_element(By.TAG_NAME, "path")
            c.click()
        else:
            driver.get("https://wordleunlimited.org/")
            print("opened")
            try:
                overlay = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "overlay"))
                )
                print("found overlay")
            except Exception as e:
                print(e)
            driver.execute_script("arguments[0].style.visibility='hidden'", overlay)
            print("set invis")
            driver.find_element(By.TAG_NAME, "path").click()

        # click continue button, I swear they are trying to make it harder to scrape or someting
        keys = driver.find_elements(
            By.XPATH, '//button[@class="Key-module_key__kchQI"]'
        )
        # get enter key, press after each word
        enter_key = driver.find_element(By.XPATH, "//button[text()='enter']")
        # get backspace buton
        backspace_key = driver.find_element(
            By.XPATH, "//button[@aria-label='backspace']"
        )
        while True:
            (
                correct_indexes,
                present_indexes,
                absent_indexes,
                counts,
            ) = get_correct_present_and_absent_indexes()
            absent_letters = get_absent_letters()
            words = filter_by_rules(
                absent_letters,
                words,
                correct_indexes,
                present_indexes,
                absent_indexes,
                counts,
            )
            if not words:
                break

            if len(correct_indexes) == 5:
                break
            for next_letter in get_next_word():
                for key in keys:
                    if key.text == next_letter:
                        key.click()

                    if next_letter == "\n":
                        enter_key.click()
                        for _ in range(5):
                            backspace_key.click()
                        sleep(1.4)
                        break
        print("press ctrl-c to close browser")
        while True:
            pass
    except Exception:
        print("Looks like something went wrong, try re-running the script.")
        driver.close()
