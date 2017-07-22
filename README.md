# fingerfood #

A python module for **fingerprinting** and **detecting duplicates** in text documents.

Text fingerprinting is the process of extracting from text a collection of representive hashes which identify the original data. By using fingerprints, it is possible to quickly search for duplicate strings between documents.

With fingerfood you can:

* **generate** fingerprints from any text string
* **store** fingerprinted data into a sqlite database
* **compare** with strings or with stored data

The fingerprinting algorithm is an implementation of [Winnowing: Local Algorithms for Document Fingerprinting](http://theory.stanford.edu/~aiken/publications/papers/sigmod03.pdf), so please refer to it for algorithm details.

## Quick Start  ##

To start using fingerfood, let first import the module.

```
import fingerfood as fd
```

### Generating a fingerprint ###

Then we can generate our first fingerprint:
```
text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'

fp = fd.Fingerprint(text,text_name='lorem',kgram_len=10,detection_thr=30)
```

The following two parameters are very important as they define the behaviour of fingerprinting comparison:

1. If there is a substring match at least as long as the *detection threshold* `detection_thr`, then the match is detected, and
2. no match shorter than the *noise threshold* `kgram_len` is detected.

If not specified, default values are used: `kgram_len=15` and `detection_thr=40`.

Optionally, we can specify a name for data using `text_name` parameter, otherwise an excerpt from text is used instead.

### Storing a fingerprint ###

To save fingerprint into DB, just use the method provided by *Fingerprint* class:

```
fp.to_sql('my.db',if_exists='append')
```

If not found, a new DB is created in the given filepath. However, when saving a new fingerprint to a DB we can specify how to manage the case in which DB tables already exist:

* `if_exists=fail`: if tables exist, do nothing.
* `if_exists=replace`: if tables exist, drop it, recreate it and insert data.
* `if_exists=append`: if tables exist, insert data. Create if does not exist. This is the default value.

### Finding matches ###

Now, let perform a simple comparison between two text strings:

```
# input texts
text_01 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis finibus metus quam, eget pulvinar ligula viverra vitae. Mauris vitae faucibus orci. Duis egestas vitae diam ac sodales.'
text_02 = 'Aenean consectetur turpis et gravida pharetra. Mauris vitae faucibus orci. Curabitur lobortis arcu id iaculis scelerisque. Morbi magna nunc, blandit quis congue eu, ullamcorper ac odio.'

# generate fingerprints
fp_01 = fd.Fingerprint(text_01)
fp_02 = fd.Fingerprint(text_02)

# search for matches
matches = fp_01.compare_with(fp_02)
if matches:
    print('found some matches!')
```

We can also compare a fingerprint object with a text string, which will be automatically fingerprinted to the scope:

```
matches = fp_01.compare_with(text_02)
if matches:
    print('found some matches!')
```

Let perform a one-to-all matching with texts stored in a DB:

```
fp_01.to_sql('my.db',if_exists='append')
fp_02.to_sql('my.db',if_exists='append')

text_03 = 'Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Aenean vel convallis arcu. Sed non feugiat mi. Fusce vulputate dui vel metus tincidunt blandit. Sed finibus faucibus mi, quis dictum nulla tempus non. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut ultricies sagittis laoreet. Curabitur in nibh ante.'

fp_03 = fd.Fingerprint(text_03,text_name='03')

matches = fp_03.search_in_db('my.db')
if matches:
    print('found some matches!')
```

### Match insight ###

Methods `compare_with()` and `search_in_db()` return `None` if no matches are found, or the list of matches otherwise.

Each match found is returned as a *dict* with three keys:

* `substr`: the match maximum-length substring (>=`detection_thr`)
* `found_in`: in which text the match is found
* `pos`: position of match inside text of the fingerprint performing the search  

So, with the previous matching we would have:

```
matches = fp_03.search_in_db('my.db')
if matches:
    print('found some matches!')
    for m in matches:
        print(m)
```
> \>>> found some matches!  
> \>>> {'substr': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. ', 'pos': 258, 'found_in': '01'}  
> \>>> {'substr': '. Lorem ipsum dolor sit amet, consectetur adipiscing elit. ', 'pos': 258, 'found_in': '02'}  

Note that in this case position is the same because refers to the same string in `fp_03` text.

## Installation  ##

To install fingerfood, simply run pip command in your terminal of choice:

```
pip install fingerfood
```
