<h1 align='center'>BruteforceHTTP</h1>
<p align='center'><i>An automated brute forcing tool</i></p>

## About this project
This project focusing on Brute Forcing HTTP protocol AUTOMATICALLY.

## Installation

Requirements
# python2.x
pip install -r requirements.txt


## Options
```
Usage: main.py [options] <url>
```
Options:

 ```
 -u <word_list> : Add word list for username field
 -p <word_list> : Add word list for password field
 -U <username>: user1:user2:user3
 ```

## Usage

Use default userlist and passlit:
```
python main.py <Target URL>
```

Use default passlist for user `admin` (for multiple usernames, use `user1:user2:user3`):
```
python main.py -U admin <Target URL>
```

Use custom userlist and custom passlist:
```
python main.py -u <path to userlist> -p <path to passlist> <Target URL>
```


## How this tool work
This tool will detect form field automatically, collect information and submit data therefor it can handle csrf token.


