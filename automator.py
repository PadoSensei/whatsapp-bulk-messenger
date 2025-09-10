from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from urllib.parse import quote
import os
import random
import csv
from datetime import datetime

# === CONFIGURATION ===
TEST_MODE = True          # ✅ Set True to simulate, False for real WhatsApp
BATCH_LIMIT = 3           # Max messages per run
MIN_DELAY = 10            # Min seconds between messages
MAX_DELAY = 20            # Max seconds between messages
LOG_FILE = "log_report.csv"

# Chrome options
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--profile-directory=Default")
options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")

os.system("")
os.environ["WDM_LOG_LEVEL"] = "0"

# Colors for printing
class style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    RESET = '\033[0m'

print(style.BLUE)
print("**********************************************************")
print("**********************************************************")
print("*****                                               ******")
print("*****  THANK YOU FOR USING WHATSAPP BULK MESSENGER  ******")
print("*****      This tool was built by PadoSensei        ******")
print("*****         https://github.com/PadoSensei         ******")
print("*****                                               ******")
print("**********************************************************")
print("**********************************************************")
print(style.RESET)

# Read message
with open("message.txt", "r", encoding="utf8") as f:
    message = f.read()

print(style.YELLOW + '\nThis is your message-')
print(style.GREEN + message)
print("\n" + style.RESET)
message_encoded = quote(message)

# Read numbers from file
numbers = []
with open("numbers.txt", "r") as f:
    for line in f.read().splitlines():
        if line.strip() != "":
            numbers.append(line.strip())

total_number = len(numbers)
print(style.RED + f'We found {total_number} numbers in the file' + style.RESET)

# Setup CSV logging
if not os.path.isfile(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "phone_number", "status", "error"])

def log_result(phone, status, error=""):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), phone, status, error])

# Load already processed numbers
processed = set()
with open(LOG_FILE, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader, None)  # skip header
    for row in reader:
        if len(row) >= 3:
            processed.add(row[1])

print(style.CYAN + f"Skipping {len(processed)} numbers already processed." + style.RESET)

# Filter unprocessed numbers
unprocessed = [n for n in numbers if n not in processed]
print(style.YELLOW + f"{len(unprocessed)} numbers left to process." + style.RESET)

# Initialize driver (safe default)
driver = None

# Launch browser if not in test mode
if not TEST_MODE:
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    print('Once your browser opens up sign in to WhatsApp Web')
    driver.get('https://web.whatsapp.com')
    input(style.MAGENTA + "AFTER logging into WhatsApp Web is complete and your chats are visible, press ENTER..." + style.RESET)

# Message sending loop
for idx, number in enumerate(unprocessed[:BATCH_LIMIT]):  # ✅ Batch limit applied
    number = number.strip()
    if number == "":
        continue

    print(style.YELLOW + f'{idx+1}/{BATCH_LIMIT} => Sending message to {number}.' + style.RESET)

    if TEST_MODE:
        # Simulate sending
        print(style.CYAN + f"[TEST MODE] Would send message to {number}: {message}" + style.RESET)
        log_result(number, "SIMULATED")
        delay = random.randint(MIN_DELAY, MAX_DELAY)
        print(style.CYAN + f"[TEST MODE] Waiting {delay} seconds..." + style.RESET)
        sleep(delay)
        continue

    # Real WhatsApp Web automation
    try:
        url = f'https://web.whatsapp.com/send?phone={number}&text={message_encoded}'
        sent = False
        for i in range(3):
            if not sent:
                driver.get(url)
                try:
                    # Wait for input box
                    input_box = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
                    )
                except Exception as e:
                    print(style.RED + f"\nFailed to send message to: {number}, retry ({i+1}/3)" + style.RESET)
                    if i == 2:  # Final retry failed
                        log_result(number, "FAILURE", str(e))
                else:
                    sleep(1)
                    input_box.send_keys(Keys.ENTER)  # ✅ Send message using ENTER
                    sent = True
                    print(style.GREEN + f'Message sent to: {number}' + style.RESET)
                    log_result(number, "SUCCESS")

                    # Random safe delay between messages
                    delay = random.randint(MIN_DELAY, MAX_DELAY)
                    print(style.CYAN + f"Waiting {delay} seconds before next message..." + style.RESET)
                    sleep(delay)
    except Exception as e:
        print(style.RED + f'Failed to send message to {number}: {str(e)}' + style.RESET)
        log_result(number, "FAILURE", str(e))

# Safely close driver
if driver is not None:
    try:
        driver.close()
    except:
        pass

# === SUMMARY REPORT ===
processed_after = set()
with open(LOG_FILE, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader, None)
    for row in reader:
        if len(row) >= 3:
            processed_after.add(row[1])

successes = 0
failures = 0
simulated = 0
with open(LOG_FILE, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader, None)
    for row in reader:
        if len(row) >= 3:
            if row[2] == "SUCCESS":
                successes += 1
            elif row[2] == "FAILURE":
                failures += 1
            elif row[2] == "SIMULATED":
                simulated += 1

remaining = total_number - len(processed_after)

print(style.BLUE + "\n========== SUMMARY ==========" + style.RESET)
print(style.GREEN + f" Total numbers in file: {total_number}" + style.RESET)
print(style.GREEN + f" Successfully messaged : {successes}" + style.RESET)
print(style.RED   + f" Failed to message     : {failures}" + style.RESET)
print(style.CYAN  + f" Simulated messages    : {simulated}" + style.RESET)
print(style.YELLOW+ f" Remaining to process  : {remaining}" + style.RESET)
print(style.BLUE + "=============================\n" + style.RESET)

if remaining == 0:
    print(style.GREEN + "🎉 All numbers in numbers.txt have been processed!" + style.RESET)
else:
    print(style.CYAN + f"👉 Run the script again to continue with the remaining {remaining} numbers." + style.RESET)
