# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals, print_function

import argparse
import os.path
import shutil
import subprocess
import tempfile
import logging

import PyPDF2
import qrtools

log = logging.getLogger(__name__)


def parseCommandLine():
    parser = argparse.ArgumentParser(description='split pdf document based on separator pages with QR codes')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true', help='be very verbose')
    group.add_argument('-q', '--quiet', action='store_true', help='no logging except errors')
    parser.add_argument('-d', '--delete-source', action='store_true', help='delete source document after processing')
    parser.add_argument('-g', '--ghostscript', action='store_true', help='executable to start ghostscript',
                        default='c:\\Program Files\\gs\\gs9.19\\bin\\gswin64c.exe')
    parser.add_argument('filename', help='path of the source document (PDF)')
    return parser.parse_args()


def extractPages(inputPDF, start, end, filename='pages from %s to %s.pdf'):
    log.debug('Extracting pages %s to %s to file %s', start, end, filename)
    output = PyPDF2.PdfFileWriter()
    for j in range(start, end):
        output.addPage(inputPDF.getPage(j))
    with open(filename % (start, end), "wb") as outputStream:
        output.write(outputStream)


def autoSplitPDF(filename, ghostScriptExecutable):
    qr = qrtools.QR()
    temporaryDirectory = tempfile.mkdtemp(prefix='autoSplitPDF - ')
    pngFiles = os.path.join(temporaryDirectory, 'pages-%03d.png')
    inputFile = os.path.abspath(filename)
    outputDirectory = os.path.dirname(filename)
    log.debug('Call ghostscript to split PDF into pages and export as PNG')
    subprocess.check_call([ghostScriptExecutable, '-dBATCH', '-dNOPAUSE', '-sDEVICE=pnggray', '-r300', '-dUseCropBox', '-sOutputFile=%s' % pngFiles, inputFile])
    log.debug('Opening %s as source PDF', inputFile)
    with open(inputFile, 'rb') as sourcePDF:
        reader = PyPDF2.PdfFileReader(sourcePDF)
        beginOfCurrentPageSet = 0
        files = []
        filenameOfCurrentPageSet = os.path.join(outputDirectory, 'Unknown (from %s to %s).pdf')
        for i in range(reader.numPages):
            log.debug('Trying to decode page %s (file %s)', i + 1, pngFiles % (i + 1))
            if qr.decode(pngFiles % (i + 1)) and qr.data.startswith('SEPARATOR SHEET'):
                log.info("Separator sheet with data: %s", qr.data)
                if i != beginOfCurrentPageSet:
                    files += [extractPages(reader, beginOfCurrentPageSet, i, filenameOfCurrentPageSet)]
                filenameOfCurrentPageSet = os.path.join(outputDirectory, qr.data.split('-', 1)[-1].strip() + ' (from %s to %s).pdf')
                beginOfCurrentPageSet = i + 1
        if beginOfCurrentPageSet < reader.numPages:
            extractPages(reader, beginOfCurrentPageSet, reader.numPages, filenameOfCurrentPageSet)
        shutil.rmtree(temporaryDirectory)


if __name__ == '__main__':
    args = parseCommandLine()
    if args.verbose:
        log.setLevel(logging.DEBUG)
    if args.quiet:
        log.setLevel(logging.ERROR)
    autoSplitPDF(args.filename, args.ghostscript)
    if args.delete_source:
        os.remove(args.filename)
