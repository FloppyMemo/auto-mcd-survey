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
python McDonalds.py <RECEIPT_CODE> --amount 5.50
# <RECEIPT_CODE>: 12 alphanumeric chars (e.g., 9N7C-R9ZF-J6MW)
# --amount: amount spent (e.g., 5.50)
```

### 3. Batch Mode  
```bash
python McDonalds.py --batch-file receipts.csv --workers 4 --headless
# receipts.csv should have lines in the format:
# 9N7C-R9ZF-J6MW,5.50
# ABCD-EFGH-IJKL,7.25
```

---

## ⚙️ Command-Line Options

| Option                     | Description                                                      | Default       |
| -------------------------- | ---------------------------------------------------------------- | ------------- |
| `--headless`               | Run Chrome in headless mode                                      | off           |
| `--no-headless`            | Disable headless (show UI)                                       | on            |
| `--attempts <N>`           | Page reload retry attempts                                       | 5             |
| `--delay-min <s>`          | Minimum delay between retries (seconds)                          | 3.0           |
| `--delay-max <s>`          | Maximum delay between retries (seconds)                          | 8.0           |
| `--element-timeout <s>`    | Timeout for element waits (seconds)                              | 15            |
| `--batch-file <PATH>`      | CSV with `receipt_code,amount` lines for batch mode              | none          |
| `--workers <N>`            | Parallel threads in batch mode                                   | 1             |
| `--output <PATH>`          | Path to the output CSV file                                      | `results.csv` |
| `--log-file <PATH>`        | Path to the log file                                             | `scraper.log` |

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
├── McDonalds.py       # Main script
├── requirements.txt   # Python dependencies (selenium, webdriver-manager)
├── receipts.csv       # Example batch input file
├── results.csv        # Default output (after run)
├── scraper.log        # Default log file
└── README.md          # This file
```

---

## 📝 License

MIT License. See [LICENSE](LICENSE) for details.
