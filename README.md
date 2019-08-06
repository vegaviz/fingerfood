# web-utils #

A few python tools for web and text processing.

## wget  ##

Mimics GNU Wget for web download. Keeps an index of downloaded files and a list of visited URLs.

```
from web_utils import Wget

# save files here
data_dir = 'tmp'

# do not download files with these extensions
rejected = ['pdf','png','jpg','jpeg','png']

# force to follow only these domains
accepted = [
    'en.wikipedia.org',
    'github.com'
]

# init and start crawling - always specify HTTP scheme
wget = Wget(recursive=True, recursion_level=3, reject_ext=rejected,
    include_domains=accepted, datapath=data_dir)
wget.get('https://en.wikipedia.org')
wget.get('https://github.com')

# access index of all traversed web-sites
download_index = wget.data_index
```

## html2text  ##

Extracts text from html code.

```
from web_utils import Html2Text

html2text = Html2Text(len_thr=50)

# list of text fragments extracted
plain_text = html2text(html)

```

## fingerprinting  ##

Generate text fingerprints for duplicate detection. The fingerprinting algorithm is an implementation of [Winnowing: Local Algorithms for Document Fingerprinting](http://theory.stanford.edu/~aiken/publications/papers/sigmod03.pdf), so please refer to it for the algorithm details.

```
from web_utils import Fingerprint

text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
fp = Fingerprint(noise_thr=15, detection_thr=40)

# generate fingerprint sample from text
sample = fp(text)

```

## Quick start  ##

Clone and install:

```
git clone https://github.com/acapitanelli/web-utils.git
cd web-utils
pip install .
```
