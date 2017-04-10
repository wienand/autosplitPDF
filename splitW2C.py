# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals, print_function

import argparse
import logging
import os
import pprint
import re
import string
from collections import defaultdict

import PyPDF2

logging.basicConfig(level=logging.INFO, format='%(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s')
log = logging.getLogger(__name__)


def parseCommandLine():
    parser = argparse.ArgumentParser(description='split pdf document containing W2C forms')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true', help='be very verbose')
    group.add_argument('-q', '--quiet', action='store_true', help='no logging except errors')
    parser.add_argument('-d', '--delete-source', action='store_true', help='delete source document after processing')
    parser.add_argument('-p', '--printID', action='store_true', help='prints all text values with OP ID from the pdf instead of separating the pages')
    parser.add_argument('-o', '--output-filenames-template', help='template for output filenames, e.g. "W2C form of {OP21}.pdf', default='W2C form of {OP21}.pdf')
    parser.add_argument('filename', help='path of the source document (PDF)')
    return parser.parse_args()


def splitW2C(filename, template):
    log.debug('Opening %s as source PDF', filename)
    extractOperations = [(x[1], int(x[1][2:])) for x in string.Formatter().parse(template) if x[1]]
    with open(filename, 'rb') as sourcePDF:
        reader = PyPDF2.PdfFileReader(sourcePDF)
        for index in range(0, reader.getNumPages()):
            page = reader.getPage(index)
            operations = PyPDF2.pdf.ContentStream(page.getContents(), page.pdf).operations
            formattingDictionary = {}
            for formatterID, extractOperation in extractOperations:
                operation = operations[extractOperation]
                if not operation[1] == b'Tj':
                    log.warn('NO STRING TYPE')
                text = ''.join(operation[0])
                formattingDictionary[formatterID] = re.sub('\s+', ' ', text).strip().title()
            output = PyPDF2.PdfFileWriter()
            output.addPage(page)
            outputFilename = template.format(**formattingDictionary)
            with open(outputFilename, "wb") as outputStream:
                log.debug('Exporting page %s to %s', index + 1, outputFilename)
                output.write(outputStream)


def printOperations(filename):
    log.debug('Opening %s as source PDF', filename)
    with open(filename, 'rb') as sourcePDF:
        reader = PyPDF2.PdfFileReader(sourcePDF)
        summary = defaultdict(list)
        for index in range(0, reader.getNumPages()):
            page = reader.getPage(index)
            operations = PyPDF2.pdf.ContentStream(page.getContents(), page.pdf).operations
            for count, operation in enumerate(operations):
                if operation[1] == b'Tj':
                    summary[count].append(''.join(operation[0]))
    pprint.pprint(dict(summary))

if __name__ == '__main__':
    args = parseCommandLine()
    if args.verbose:
        log.setLevel(logging.DEBUG)
    if args.quiet:
        log.setLevel(logging.ERROR)
    if args.printID:
        printOperations(args.filename)
    else:
        splitW2C(args.filename, args.output_filenames_template)
    if args.delete_source:
        os.remove(args.filename)
