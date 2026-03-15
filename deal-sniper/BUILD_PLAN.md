# DEAL SNIPER - BUILD SPECIFICATION

This document defines the architecture and build instructions for the Deal Sniper system.

The AI coding agent should read this file and generate the entire project.

--------------------------------------------------

PROJECT GOAL

Create a Python system that detects high value ecommerce deals and sends alerts to Telegram.

Primary ecommerce platforms:

Amazon
Flipkart
Myntra
Ajio

Primary signal source:

Telegram deal channels.

The system must:

• monitor Telegram channels in real time
• extract ecommerce links
• parse deal information
• verify product prices
• score deals
• send alerts only for valuable deals

--------------------------------------------------


--------------------------------------------------

TECHNOLOGY STACK

Language:

Python 3.10+

Libraries:

telethon
requests
beautifulsoup4
python-dotenv
sqlite3

Purpose:

Telethon
Used for real time Telegram channel monitoring.

Requests
Used to fetch ecommerce product pages.

BeautifulSoup
Used to parse HTML and extract price information.

python-dotenv
Used to securely load credentials from environment variables.

SQLite
Used to store product price history.

--------------------------------------------------

DEPENDENCY MANAGEMENT

The agent must generate a requirements.txt file containing:

telethon
requests
beautifulsoup4
python-dotenv

The project must install dependencies using:

pip install -r requirements.txt

--------------------------------------------------

FINAL PRODUCT VISION

The final system should function as a personal deal intelligence engine.

Capabilities:

• real time Telegram monitoring
• fast deal detection
• price verification from ecommerce sites
• duplicate alert prevention
• price history tracking
• Telegram notifications

Future upgrades may include:

• coupon stacking detection
• price anomaly detection
• automated deal discovery

These are NOT required for the first version.

--------------------------------------------------

MVP SCOPE

The first version must implement:

1. Telegram channel monitoring
2. Deal parsing
3. Ecommerce price verification
4. Deal scoring
5. Telegram alerting

Focus on stability and modular design.

--------------------------------------------------

SYSTEM ARCHITECTURE

The system uses a two stage deal detection pipeline.

Stage 1: Fast processing

Telegram message
↓
Deal parser
↓
Quick heuristic scoring
↓
Verification queue

Stage 2: Verification worker

Verification queue
↓
Ecommerce watcher
↓
Price verification
↓
Final scoring
↓
Send alert

This architecture prevents slow page scraping from blocking message processing.

--------------------------------------------------

PROJECT STRUCTURE

deal-sniper/

main.py
config.py
database.py

listeners/
    telegram_listener.py

parsers/
    link_extractor.py
    deal_parser.py

watchers/
    amazon_watcher.py
    flipkart_watcher.py
    myntra_watcher.py
    ajio_watcher.py

engine/
    deal_scorer.py
    job_queue.py

notifier/
    telegram_bot.py

storage/
    deals.db


Each folder must contain an __init__.py file so it can be treated as a Python package.

Required in:

listeners/
parsers/
watchers/
engine/
notifier/

--------------------------------------------------

REQUIRED DIRECTORIES

The system must automatically ensure these directories exist:

storage/
logs/

If missing, create them during application startup.


--------------------------------------------------

IMPORT CONVENTION

All modules must use absolute imports relative to the project root.

Example:

from parsers.link_extractor import extract_links
from engine.deal_scorer import score_deal
from watchers.amazon_watcher import fetch_product_data

Avoid relative imports like:

from ..parsers import link_extractor



--------------------------------------------------

CONFIGURATION

Configuration values must be loaded from environment variables.

Use python-dotenv to load variables from a .env file.

Example .env file:

API_ID=123456
API_HASH=your_hash_here
BOT_TOKEN=telegram_bot_token
ALERT_CHAT_ID=telegram_chat_id

config.py must expose:

API_ID
API_HASH
BOT_TOKEN
ALERT_CHAT_ID

CHANNELS = [
    -1001412868909,
    -1001596448068,
    -1001493857075,
    -1001346861267
]

CHANNELS may contain either:

• Telegram usernames
• Telegram channel IDs (-100xxxxxxxxxx)


DEAL_SCORE_THRESHOLD = 60

DRY_RUN = True

--------------------------------------------------
ENVIRONMENT FILE

The project must include a .env file in the project root.

This file contains sensitive credentials.

Example structure:

API_ID=123456
API_HASH=abcdef123456
BOT_TOKEN=12345:telegram_bot_token
ALERT_CHAT_ID=123456789

The .env file must not be committed to version control.

The agent should generate a .env.example file for reference.

--------------------------------------------------

DRY RUN MODE

The system must support a dry run mode.

When DRY_RUN = True:

• the system runs the full pipeline
• deals are parsed
• price verification is executed
• deal scoring is executed

BUT

• no Telegram alerts are sent

Instead the system must log detected deals to the console and log file.

Example log output:

[DRY RUN] Deal Detected
Product: Samsung SSD
Price: 899
MRP: 2999
Discount: 70%

This mode is used for debugging and testing.

When DRY_RUN = False:

• Telegram alerts must be sent normally.

--------------------------------------------------

BUILD ORDER

The AI agent must follow this order.

STEP 1

Create project folder structure.

STEP 2

Implement config loader.

STEP 3

Implement Telegram listener using Telethon.

Responsibilities:

connect to Telegram
subscribe to channels
detect new messages
pass message text to pipeline

The listener must support both channel usernames and numeric channel IDs.

When resolving channels:

if isinstance(channel, int):
    use channel ID directly
else:
    resolve username using Telethon client.get_entity()

Function:

start_listener(callback_function)



--------------------------------------------------

STEP 4

Implement link extractor.

Responsibilities:

extract URLs from text
expand shortened links

Examples:

amzn.to
fkrt.it

Implementation detail:

Use HTTP HEAD request with redirects enabled.


--------------------------------------------------

URL NORMALIZATION

All product URLs must be normalized before further processing.

Examples:

Amazon

https://amazon.in/dp/B08ABC123?tag=something

Normalize to:

https://amazon.in/dp/B08ABC123

Flipkart

remove tracking parameters.

Purpose:

• consistent database keys
• proper duplicate detection

--------------------------------------------------

STEP 5

Implement deal parser.

Extract:

product_name
price
mrp
discount
site

The parser should extract product identifiers when possible:

Amazon → extract ASIN from URL
Flipkart → extract PID from URL

This identifier will be used for database tracking and duplicate detection.


Site detection must recognize:

amazon
flipkart
myntra
ajio


DEAL PARSER OUTPUT FORMAT

The deal parser must return a dictionary.

Example structure:

{
    "product_name": str,
    "price": float,
    "mrp": float,
    "discount": float,
    "site": str,
    "product_id": str,
    "url": str
}

The scoring engine will use this structure.

--------------------------------------------------

STEP 6

Implement job queue system.

Purpose:

prevent slow website scraping from blocking message processing.

Implementation:

use Python queue or asyncio queue.

Pipeline:

listener
→ parser
→ quick score
→ queue verification job


WORKER MODEL

The verification worker must run in a separate asynchronous task or thread.

Recommended implementation:

asyncio task OR worker thread consuming queue.

Listener must never wait for watcher execution.

Listener must remain non-blocking.

--------------------------------------------------

STEP 7

Implement ecommerce watchers.

Each watcher must fetch product page and extract:

product_name
price
mrp

Watchers must also normalize currency values and convert them to float.

--------------------------------------------------

WATCHER FUNCTION INTERFACE

Each watcher module must expose a standardized function.

Function signature:

def fetch_product_data(url: str, session) -> dict

Return format:

{
    "product_id": str,
    "product_name": str,
    "price": float,
    "mrp": float,
    "site": str,
    "url": str
}

All watcher modules must follow this interface so the main pipeline can call them generically.

--------------------------------------------------

MAIN PIPELINE IMPLEMENTATION

The main application must coordinate all modules.

main.py responsibilities:

1. load configuration
2. initialize database
3. initialize HTTP session
4. start Telegram listener
5. process incoming messages

Processing pipeline:

on_message(message):

    links = extract_links(message)

    for each link:

        detect site

        parse deal text

        quick_score = score_deal(parsed_data)

        if quick_score >= DEAL_SCORE_THRESHOLD:

            enqueue verification job
        
        If quick_score < DEAL_SCORE_THRESHOLD:

            discard the deal
            log that the deal was filtered by heuristic scoring

    

verification_worker(job):

    fetch product info using watcher

    recompute score

    if score >= DEAL_SCORE_THRESHOLD:

        send alert (or log if DRY_RUN)



--------------------------------------------------

HTTP SESSION MANAGEMENT

The system must create a single shared HTTP session during startup.

Implementation requirements:

• create one global requests.Session() instance
• initialize it in main.py during application startup
• pass the session object to all watcher modules

Purpose:

• reduce connection overhead
• reuse TCP connections
• behave more like a real browser
• reduce risk of bot detection

Example structure:

main.py

session = requests.Session()

watchers must receive this session object when making requests.

Example usage inside watcher:

def get_product_data(url, session):
    response = session.get(url)

Do NOT create new requests.Session() instances inside watcher modules.

All watchers must reuse the shared session.



--------------------------------------------------
AMAZON WATCHER REQUIREMENTS

Amazon pages often fail if headers are missing.

Always send realistic browser headers.

Example headers:

User-Agent: Mozilla/5.0
Accept-Language: en-IN,en;q=0.9
Connection: keep-alive

Use requests.Session() for connection reuse.

Price selectors to check:

span.a-price-whole
span#priceblock_ourprice
span#priceblock_dealprice

If one selector fails, try others.

--------------------------------------------------

FLIPKART WATCHER

Extract:

product name
price
mrp

Use HTML parsing.

--------------------------------------------------

MYNTRA WATCHER

Extract:

price
mrp
product name

--------------------------------------------------

AJIO WATCHER

Extract:

price
mrp
product name

--------------------------------------------------

DEAL SCORING ENGINE

File:

engine/deal_scorer.py

Rules:

discount > 70% → +40 points
discount > 50% → +25 points

price drop > 1000 INR → +20 points

keywords:

ssd
router
gpu
headphones

→ +20 points

Function:

score_deal(product_data)

Return score.

--------------------------------------------------

DATABASE

Use SQLite.

Location:

storage/deals.db

Store:

product_id
site
price
timestamp

Purpose:

track price history
prevent duplicate alerts


DATABASE SCHEMA

Create table:

alerts

Columns:

product_id TEXT
site TEXT
price REAL
timestamp INTEGER
last_alert_time INTEGER

Primary key:

(product_id, site)
--------------------------------------------------

DUPLICATE ALERT PREVENTION

The system must prevent sending the same deal alert repeatedly.

Before sending a Telegram alert the system must check whether the product was recently alerted.

Implementation requirements:

• store alerted products in the database
• store product identifier and timestamp

Recommended identifier:

Amazon → ASIN extracted from URL
Flipkart → PID extracted from URL
Myntra/Ajio → normalized product URL

Duplicate rule:

If the same product has been alerted within the last 30 minutes:

• do NOT send another alert
• log that the alert was skipped

Example logic:

if last_alert_timestamp < 30 minutes ago:
    send alert
else:
    skip alert

Database table must include:

product_id
site
last_alert_time

--------------------------------------------------

TELEGRAM NOTIFICATIONS

File:

notifier/telegram_bot.py

Function:

send_alert(product_data, score)

Message format:

⚡ Deal Detected

Product: {name}
Price: ₹{price}
MRP: ₹{mrp}
Discount: {discount}%

Link: {url}


Before sending a Telegram alert, the function must check the configuration value DRY_RUN.

If DRY_RUN = True:

• do not send Telegram message
• print formatted alert to console
• log alert

If DRY_RUN = False:

• send Telegram message using Bot API

--------------------------------------------------

ASYNC PROCESSING

The system should use asyncio where possible.

Reasons:

Telegram listener already uses async.

Async processing allows multiple deals to process simultaneously.

--------------------------------------------------

GRACEFUL SHUTDOWN

The system must handle shutdown signals.

When receiving SIGINT or SIGTERM:

• stop Telegram listener
• stop worker threads
• close HTTP session
• flush logs
• close database

Program must exit cleanly.

--------------------------------------------------

ERROR HANDLING

Handle:

invalid URLs
network errors
missing price fields
Telegram connection failures

--------------------------------------------------
Watcher failures must not crash the application pipeline.

TRAFFIC SAFETY AND ANTI-DETECTION REQUIREMENTS

The system must behave like a normal user and must NOT aggressively scrape ecommerce websites.

The goal is to minimize the risk of IP blocking or bot detection.

The following rules must be implemented.

--------------------------------------------------

REQUEST RATE LIMITING

Each ecommerce watcher must implement request throttling.

Rules:

maximum 1 request per product verification
minimum 2–5 seconds between requests to the same domain
randomized delay between requests

Example delay:

random delay between 2 and 5 seconds

This helps mimic human browsing patterns.

--------------------------------------------------

SESSION REUSE

All HTTP requests should use a shared requests.Session().

Benefits:

• connection reuse
• fewer TCP handshakes
• more realistic browsing behavior

Example:

create one global session object
reuse it for all watcher requests

--------------------------------------------------

REALISTIC HEADERS

All ecommerce requests must include browser-like headers.

Required headers:

User-Agent (modern browser string)
Accept-Language: en-IN,en;q=0.9
Connection: keep-alive

These headers reduce the chance of bot detection.

--------------------------------------------------

LIMITED SCRAPING SCOPE

The system must NOT scan entire ecommerce catalogs.

Instead it should only fetch product pages when:

1. a Telegram deal contains a product link
2. a product enters the verification queue

This ensures the system only checks a small number of pages.

--------------------------------------------------

REDIRECT HANDLING

Shortened links must be expanded before scraping.

Use HTTP HEAD requests with redirects enabled.

Example shortened domains:

amzn.to
fkrt.it

--------------------------------------------------

FAILURE HANDLING

If a website request fails:

• log the error
• skip the deal
• do not retry aggressively

Avoid repeated retries that could trigger blocking.


RETRY POLICY

Watcher requests may retry up to 2 times with exponential backoff.

Example:

retry delay:

1 second
2 seconds

After maximum retries:

log failure
skip deal

Retries must respect request rate limiting rules.

--------------------------------------------------

REQUEST TIMEOUTS

All HTTP requests must include timeouts.

Example:

timeout = 10 seconds

If a request exceeds the timeout it should be aborted.

--------------------------------------------------

OPTIONAL USER AGENT ROTATION

The system may optionally rotate between a small set of realistic browser user agents.

Example pool:

Chrome Windows
Chrome Linux
Chrome Android

Do NOT generate random or unrealistic user agents.

--------------------------------------------------

NO PARALLEL BURSTS

Even when using asyncio or workers, the system must not send many requests simultaneously to the same domain.

Maximum concurrency per domain:

2 requests

--------------------------------------------------

LOGGING AND MONITORING

Log all ecommerce requests.

Log fields:

timestamp
domain
URL requested
response status

If repeated failures occur from a domain, the system should slow down request frequency.


LOGGING IMPLEMENTATION

Use Python logging module.

Logging levels required:

INFO
WARNING
ERROR

Log format:

timestamp | module | level | message

Example:

2026-03-15 19:21:03 | watcher.amazon | INFO | Price extracted successfully

Logs must be written to:

logs/deal_sniper.log
--------------------------------------------------

PERFORMANCE TARGET

The system must:

process messages within 2 seconds
handle 100+ deals per hour
avoid duplicate alerts

--------------------------------------------------

TESTING CHECKPOINTS

Checkpoint 1

Telegram listener prints incoming messages.

Checkpoint 2

Link extractor detects URLs.

Checkpoint 3

Watchers return price data.

Checkpoint 4

Deal scoring returns numeric score.

Checkpoint 5

Telegram bot sends alerts.

Checkpoint 6

Full pipeline works.


BASIC TEST COVERAGE

The agent should create simple tests for:

• link extraction
• deal parsing
• deal scoring

Tests should be placed in:

tests/

--------------------------------------------------

APPLICATION ENTRYPOINT

main.py must act as the single entrypoint for the application.

Responsibilities of main.py:

• load configuration
• initialize logging before any other subsystem
• initialize SQLite database
• create shared HTTP session
• initialize job queue
• start verification worker
• start Telegram listener

The program must start the entire pipeline when executing:

python main.py

--------------------------------------------------

RUNNING THE SYSTEM

The application must run using:

python main.py

--------------------------------------------------

INSTRUCTIONS FOR AI AGENT

The agent must:

1. generate project structure
2. implement modules sequentially
3. ensure imports work
4. add error handling
5. verify each checkpoint before proceeding

If a module fails, debug and fix before continuing.

--------------------------------------------------