# Structlog issue

Issue: https://github.com/hynek/structlog/issues/613

# How to run this code
Install structlog
```
pip install structlog
```
Then run the main.py file
```
python main.py
```

---

Current output:
```
$ python main.py
logger argument is <_FixedFindCallerLogger testing_sructlog (DEBUG)>
2024-04-05T15:02:51+0000 [debug    ] A log test from logging.       [testing_sructlog]
logger argument is None
2024-04-05T15:02:51+0000 [debug    ] A log test from structlog.     [testing_sructlog]
```

Expected output (more or less):
```
$ python main.py
logger argument is <_FixedFindCallerLogger testing_sructlog (DEBUG)>
2024-04-05T15:02:51+0000 [debug    ] A log test from logging.       [testing_sructlog]
logger argument is <a valid object like logging.Logger> 
2024-04-05T15:02:51+0000 [debug    ] A log test from structlog.     [testing_sructlog]
```
