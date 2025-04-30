# auto-mcd-survey

**Scripted bot for completing McDonald’s “Food for Thoughts” surveys**

---

## 📦 Installation

**Step 1: Clone the repository**  
```bash
git clone https://github.com/FloppyMemo/auto-mcd-survey.git
cd auto-mcd-survey
```

**Step 2: Install dependencies**  
```bash
pip install -r requirements.txt
```

---

## ⚙️ Requirements

- Python 3.7 or higher  
- Google Chrome browser  
- pip packages:
  - selenium
  - webdriver-manager

---

## 🚀 Usage

### 1. Interactive Mode  
```bash
python McDonalds.py
# You will be prompted to enter:
# - 12-character receipt code
# - Purchase amount (e.g., 5.50)
```

### 2. Direct Mode  
```bash
python McDonalds.py <RECEIPT_CODE> --amount <VALUE>
# <RECEIPT_CODE>: 12 alphanumeric chars (e.g., 9N7C-R9ZF-J6MW)
# --amount <VALUE>: amount spent (e.g., 5.50)
```

### 3. Batch Mode  
```bash
python McDonalds.py --batch-file receipts.csv --workers 4 --headless
# receipts.csv format:
# 9N7C-R9ZF-J6MW,5.50
# ABCD-EFGH-IJKL,7.25
```

---

## ⚙️ Command-Line Options

| Option                     | Description                                                      | Default       |
| -------------------------- | ---------------------------------------------------------------- | ------------- |
| `receipt_code`             | 12-character receipt code (positional)                           | —             |
| `--amount <VALUE>`         | Amount spent (e.g., `5.50`)                                      | `00.00`       |
| `--batch-file <PATH>`      | CSV with `receipt_code,amount` lines                             | —             |
| `--workers <N>`            | Number of parallel threads in batch mode                         | `1`           |
| `--headless`               | Run Chrome in headless mode                                      | off           |
| `--no-headless`            | Run Chrome with UI                                               | on            |
| `--attempts <N>`           | Page load retry attempts                                         | `5`           |
| `--delay-min <SECONDS>`    | Minimum delay between retries                                    | `3.0`         |
| `--delay-max <SECONDS>`    | Maximum delay between retries                                    | `8.0`         |
| `--element-timeout <SEC>`  | Timeout for element waits                                        | `15`          |
| `--output <PATH>`          | CSV output file path                                             | `results.csv` |
| `--log-file <PATH>`        | Log file path                                                    | `scraper.log` |

---

## 💡 Examples

**Single run (visible UI)**  
```bash
python McDonalds.py 9N7C-R9ZF-J6MW --amount 7.25
```

**Batch run (4 threads, headless)**  
```bash
python McDonalds.py --batch-file my_receipts.csv --workers 4 --headless
```

---

## 📂 Project Structure

```
auto-mcd-survey/
├── McDonalds.py        # Main script
├── requirements.txt    # Python dependencies (selenium, webdriver-manager)
├── receipts.csv        # Example batch input file
├── results.csv         # Default CSV output (after run)
├── scraper.log         # Default log file
└── README.md           # This file
```

---

## 📝 Description

This tool automates the completion of McDonald’s “Food for Thoughts” surveys by:
1. Loading the survey welcome page.  
2. Entering the normalized coupon code and the purchase amount.  
3. Progressing through survey questions with randomized selections.  
4. Extracting and saving the final offer code.

Supports configurable retries, delays, headless/UI modes, parallel batch processing, and logging.

---

## 📄 License

MIT License  
See [LICENSE](LICENSE) for details.
