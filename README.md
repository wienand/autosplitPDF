# autosplitPDF
Split pdf files using separator pages, e.g. when after scanning them with a MFD

```
usage: autosplitPDF.py [-h] [-v | -q] [-d] [-g] filename

split pdf document based on separator pages with QR codes

positional arguments:
  filename             path of the source document (PDF)

optional arguments:
  -h, --help           show this help message and exit
  -v, --verbose        be very verbose
  -q, --quiet          no logging except errors
  -d, --delete-source  delete source document after processing
  -g, --ghostscript    executable to start ghostscript

Process finished with exit code 0
```
