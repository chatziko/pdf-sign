## pdf-sign.py

A simple command line tool for signing pdf documents using a card reader.
Mainly intended for use in Linux, using the Gemalto readers provided to Greek
universities (but any PKCS #11 compatible reader should work).



### Installation

1. Install the [endesive](https://github.com/m32/endesive) library
    ```
    sudo python3 -mpip install endesive
    ```

2. Install the card reader drivers. The Gemalto drivers for __Ubuntu 20.04__ can
   be installed using the provided script:
   ```
   ./scripts/install-gemalto-ubuntu-20.04.sh
   ```
   Instructions for other linux distributions are available [here](https://it.auth.gr/el/node/4986).


### Usage

Connect the card reader and run `pdf-sign.py` passing a pdf file as parameter:
```
pdf-sign.py document.pdf
```

#### Notes
  - By default the script is using the [HARICA](https://harica.gr/) timestamp server, as a
    consequence it needs to be run from a __Greek university network (or VPN)__.
    To select a different timestamp server use the `--tsa` option.
  - By default the signature is __invisible__, not shown in any page of the pdf.
    Use `--stamp-page=N` to add a visible signature stamp to page `N`.

#### Detailed options
```
positional arguments:
  PDF                 path to pdf file

optional arguments:
  -h, --help          show this help message and exit
  --pin PIN           the card pin. Default: ask for pin
  --stamp-page N      the page to add a visible signature stamp. Default: 0 (no stamp)
  --stamp-pos X,Y     the X,Y coordinates (relative to the bottom-left corner) of the signature stamp. Default: 200,20
  --stamp-size W,H    the width and height of the signature stamp. Default: 270,60
  --stamp-text TEXT   the text of the signature stamp. Default: signer's name and date
  --out-file FILE     the path of the signed pdf file. Default: input file with -signed suffix
  --tsa URL           URL of the timestamp server (empty: no timestamp). Default: http://qts.harica.gr/
  --card-reader FILE  driver (.so/.dll file) of the card reader. Default: libgclib.so
```


### Validate

The signed pdfs can be validated using Acrobat Reader, or the following online tool:

https://ec.europa.eu/cefdigital/DSS/webapp-demo/validation


### Nautilus integration

An easy way to integrate with Nautilus:
- put `pdf-sign.py` anywhere in `PATH`
- copy `scripts/pdf-sign.sh` under `.local/share/nautilus/scripts`
- Right click a pdf file and select `Scripts / pdf-sign.sh`
