
# BonusCompare — AI-Powered Casino Bonus Scraper

A Python-based web scraping project that extracts casino welcome bonus information from a South African comparison website, processes the data using Google's Gemini AI, and displays the results in a responsive HTML, CSS and JavaScript interface.

## Features

- Extracts casino bonus information using Python and BeautifulSoup.
- Checks robots.txt before scraping.
- Processes extracted information with Google's Gemini API.
- Validates AI-generated data against the scraped source.
- Exports structured results to `casinos.json`.
- Displays casino offers in responsive cards.
- Includes a side-by-side comparison table.
- Uses safe DOM text rendering and validated source links.
- Handles API errors and retries failed requests.

## Technologies Used

- Python
- Requests
- BeautifulSoup4
- Google Gemini API
- HTML5
- CSS3
- JavaScript
- Git and GitHub Pages

## Project Structure

```text
casino-bonus-scraper/
├── scraper.py
├── casinos.json
├── index.html
├── style.css
├── script.js
├── requirements.txt
├── README.md
├── .gitignore
└── test_ai.py
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/saadlachporia/casino-bonus-scraper.git
cd casino-bonus-scraper
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_API_URL=your_gemini_generate_content_endpoint
```

The Gemini API key is kept private using `.gitignore`.

### 5. Run the scraper

```bash
python3 scraper.py
```

The scraper will:

1. Check the source website's robots.txt rules.
2. Fetch and parse the bonus comparison table.
3. Extract information for three casinos.
4. Send the extracted information to Gemini for structuring.
5. Validate the returned information.
6. Save the results to `casinos.json`.

## Running the Website Locally

Start a local web server:

```bash
python3 -m http.server 8000
```

Open:

http://localhost:8000

The frontend reads `casinos.json` and generates the comparison cards and table dynamically.

## Live Website

https://saadlachporia.github.io/casino-bonus-scraper/

The GitHub Pages website serves the last committed JSON snapshot. The Python scraper does not run on GitHub Pages.

## Data Source

https://betproof.co.za/casino-bonuses-south-africa/sign-up-bonus-south-africa/

The prototype extracts three casino offers from the source comparison table.

Offer values and conditions may change. The displayed information should be checked against the original source before use.

## AI Integration

Google Gemini is used to convert extracted casino bonus text into structured JSON.

The scraper validates the AI response before writing the final output to reduce the risk of incorrect or unsupported values.

## Error Handling

The scraper includes:

- robots.txt checking
- HTTP request error handling
- Gemini API retries
- JSON response validation
- Source-data consistency checks

## Scaling to 200 Casinos

For a larger production implementation, I would:

- Use a VPS to host the scraper and backend.
- Store casino information and scrape history in PostgreSQL.
- Schedule daily scraping jobs using cron or a task queue.
- Respect robots.txt, site terms and request rate limits.
- Implement retry handling, structured logs and failure alerts.
- Create automated database backups.
- Configure a domain, DNS and HTTPS using Let's Encrypt.
- Monitor changes in offers before publishing updates.

A small initial deployment could be budgeted at approximately €10–€25 monthly, subject to actual hosting and AI usage.

## Responsible Use

This project was developed as a technical assessment demonstrating web scraping, AI-assisted data processing and responsive frontend development.

It is not a gambling operator. Information is presented for comparison purposes only.

18+. Gamble responsibly.
```
