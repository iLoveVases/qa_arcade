# QA Arcade

Automated test project using **Playwright** and **Pytest**.
This repository serves both as a learning environment and a personal portfolio
##  Project Structure
```
qa_arcade/
│
├── tests/             # stable tests
│   └── herokuapp/     # test cases for demo pages
│
├── fail_examples/     # intentionally failing tests for demo
│
├── conftest.py        # pytest hooks
├── requirements.txt
└── README.md
```

## Current Features
-  **Playwright + Pytest** integration for automation  
-  **HTML reporting** with automatic screenshot capture on failure  
-  **Parameterized tests** (data-driven testing)  
-  **Custom hook** in `conftest.py` to attach screenshots and logs  
-  **Intentional failures** included for demo purposes  
-  **Clean test structure**: `tests/` for stable tests, `fail_examples/` for failure demos  


## How to Run Tests

### 1. Set Up Virtual Environment

Open a terminal and navigate to the project directory (`cd path_to\qa_arcade`), and create a virtual environment:

**Windows (PowerShell)**

    python -m venv .venv
    .venv\Scripts\Activate.ps1

**macOS / Linux**

    python3 -m venv .venv
    source .venv/bin/activate
### 2. Install Dependencies

Install the required dependencies:

    pip install -r requirements.txt

### 3. Install Playwright Browsers

Install the necessary Playwright browsers:

    python -m playwright install

### 4. Run Tests

Run all stable tests (an HTML report will be generated automatically):

    pytest

Run a single test file (an HTML report will be generated automatically):

    pytest tests/herokuapp/test_basic_auth.py

### 5. Run Intentional Failures

To demonstrate how failed cases are handled, you can run the intentionally failing tests located in `fail_examples/`:

    pytest fail_examples



## Reporting
HTML report is generated automatically at:
  ```
  test_results/report.html
  ```
Failed tests include **screenshots** in the report (configured in `conftest.py`).

### About the `test_results/` folder
- The folder is created **only when tests are executed**.  
- It is **ignored by Git** (not versioned) because it contains generated artifacts (reports, screenshots).  
- To view a report, simply run the tests and open the generated HTML file in a browser.  