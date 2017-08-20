# Facebook Conversation Parser

This python script is a simple conversation parser allowing you to dump a full Facebook conversation in txt or csv formats.


## Requirements

* Python >= 2.7
* Mechanize
* Beautiful Soup
* pyopenssl
* lxml

## Usage
After filling the conf.cfg file with Facebook email and password,
use this command :

```
python fbparser.py --convid <mid.XXXXXXX...until the end of the url> --name <FileName> --format <txt or csv or console>

```
