import argparse

import bibtexparser
from bibtexparser.bibdatabase import (BibDatabase, BibDataString, BibDataStringExpression)
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter

# bibtex strings (e.g., #cvpr#) for conferences
CONFERENCE_BIBSTR = {
    'CVPR': '#cvpr#',
    'CVPR Workshops': '#cvprw#',
    'ICCV': '#iccv#',
    'ICCV Workshops': '#iccvw#',
    'ECCV': '#eccv#',
    'ECCV Workshops': '#eccvw#',
    'NeurIPS': '#nips#',
    'ICPR': '#icpr#',
    'BMVC': '#bmvc#',
    'ACM MM': '#acmmm#',
    'ICME': '#icme#',
    'ICASSP': '#icassp#',
    'ICIP': '#icip#',
    'ACCV': '#accv#',
    'ICLR': '#iclr#',
    'IJCAI': '#ijcai#',
    'PR': '#pr#',
    'AAAI': '#aaai#',
    'ICML': '#icml#',
}
# bibtex strings (e.g., #pami#) for journals
JOURNAL_BIBSTR = {
    'IEEE TPAMI': '#pami#',
    'IJCV': '#ijcv#',
    'ACM TOG': '#tog#',
    'IEEE TIP': '#tip#',
    'IEEE TVCG': '#tvcg#',
    'IEEE TCSVT': '#tcsvt#',
    'IEEE TMM': '#tmm#',
    'IEEE TCSVT': '#csvt#'
}
# shortname dict for conferences
CONFERENCE_SHORTNAMES = {
    'cvpr': 'CVPR',
    'cvprw': 'CVPR Workshops',
    'iccv': 'ICCV',
    'iccvw': 'ICCV Workshops',
    'eccv': 'ECCV',
    'eccvw': 'ECCV Workshops',
    'nips': 'NeurIPS',
    'icpr': 'ICPR',
    'bmvc': 'BMVC',
    'acmmm': 'ACM MM',
    'icme': 'ICME',
    'icassp': 'ICASSP',
    'icip': 'ICIP',
    'accv': 'ACCV',
    'iclr': 'ICLR',
    'ijcai': 'IJCAI',
    'pr': 'PR',
    'aaai': 'AAAI',
    'icml': 'ICML'
}
# shortname dict for journals
JOURNAL_SHORTNAMES = {
    'pami': 'IEEE TPAMI',
    'ijcv': 'IJCV',
    'tog': 'ACM TOG',
    'tip': 'IEEE TIP',
    'tvcg': 'IEEE TVCG',
    'tcsvt': 'IEEE TCSVT',
    'tmm': 'IEEE TMM',
    'csvt': 'IEEE TCSVT'
}
SHORTNAME_BIBSTR = r"""@String(PAMI  = {IEEE TPAMI})
@String(IJCV  = {IJCV})
@String(CVPR  = {CVPR})
@String(CVPRW = {CVPR Workshops})
@String(ICCV  = {ICCV})
@String(ICCVW = {ICCV Workshops})
@String(ECCV  = {ECCV})
@String(ECCVW = {ECCV Workshops})
@String(NIPS  = {NeurIPS})
@String(ICPR  = {ICPR})
@String(BMVC  =	{BMVC})
@String(TOG   = {ACM TOG})
@String(TIP   = {IEEE TIP})
@String(TVCG  = {IEEE TVCG})
@String(TCSVT = {IEEE TCSVT})
@String(TMM   =	{IEEE TMM})
@String(ACMMM = {ACM MM})
@String(ICME  =	{ICME})
@String(ICASSP=	{ICASSP})
@String(ICIP  = {ICIP})
@String(ACCV  = {ACCV})
@String(ICLR  = {ICLR})
@String(IJCAI = {IJCAI})
@String(PR    = {PR})
@String(AAAI  = {AAAI})
@String(CSVT  = {IEEE TCSVT})
@String(ICML  = {ICML})

"""


def main(args):
    # read bib file and parse without interpreting the BibDataString, e.g., #cvpr#
    parser = BibTexParser(interpolate_strings=False)
    with open(args.input, encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file, parser)

    new_bib_database = BibDatabase()  # storing the new bib entries
    new_bib_database.entries = []

    conference_names = [v.lower() for v in CONFERENCE_BIBSTR.keys()]
    journal_names = [v.lower() for v in JOURNAL_BIBSTR.keys()]

    # fields to be reserved in each bib entry
    reserved_fields = [
        'ID', 'ENTRYTYPE', 'title', 'author', 'booktitle', 'year', 'journal', 'comment', 'groups', 'timestamp', 'file',
        'howpublished'
    ]
    # fields to be removed in each bib entry
    removed_fields = [
        'pages', 'number', 'volume', 'organization', 'date', 'owner', 'publisher', 'journaltitle', 'eprint',
        'eprintclass', 'eprinttype', 'institution'
    ]

    # for duplicate checking
    all_ids = []
    all_titles = []

    for entry in bib_database.entries:
        entry_type = entry['ENTRYTYPE']
        entry_id = entry['ID']
        new_entry = dict(ID=entry_id, ENTRYTYPE=entry_type)
        # change data to year
        if 'date' in entry and 'year' not in entry:
            new_entry['year'] = entry['date']
        # change journaltitle to booktitle or journal
        if 'journaltitle' in entry:
            if entry_type == 'inproceedings':
                new_entry['booktitle'] = entry['journaltitle']
            elif entry_type == 'article':
                new_entry['journal'] = entry['journaltitle']

        # remove unnecessary keys
        for key in entry.keys():
            if key not in reserved_fields:
                if key in removed_fields:
                    print(f'Remove {key} for {entry_id}')
                else:
                    status = input(f'Unknown key: {key} for {entry_id}\n'
                                   '> Enter R/r for reserving, or leave it for deleting: ')
                    if status.lower() == 'r':
                        new_entry[key] = entry[key]
            else:
                new_entry[key] = entry[key]

        # for inproceedings
        if entry_type == 'inproceedings':
            # check booktitle
            if isinstance(new_entry['booktitle'], str):  # pass the BibDataString type (e.g., #cvpr#')
                booktitle_text = new_entry['booktitle'].lower()
                new_booktitle = None
                if 'international conference on computer vision' in booktitle_text or 'iccv' in booktitle_text:
                    if 'workshop' in booktitle_text:
                        new_booktitle = 'iccvw'
                    else:
                        new_booktitle = 'iccv'
                elif 'computer vision and pattern recognition' in booktitle_text or 'cvpr' in booktitle_text:
                    if 'workshop' in booktitle_text:
                        new_booktitle = 'cvprw'
                    else:
                        new_booktitle = 'cvpr'
                elif 'international conference on machine learning' in booktitle_text or 'icml' in booktitle_text:
                    if 'workshop' in booktitle_text:
                        new_booktitle = 'icmlw'
                    else:
                        new_booktitle = 'icml'
                else:
                    new_booktitle = input(f'Unknown conference name: {new_entry["booktitle"]}\n'
                                          f'> Please enter the abbreviation(Leave it for not changing): ')
                if new_booktitle is not None and new_booktitle != '':
                    new_entry['booktitle'] = BibDataStringExpression([BibDataString(new_bib_database, new_booktitle)])
        elif entry_type == 'article':
            # remove the 'arXiv preprint' string
            if 'journal' in new_entry and isinstance(new_entry['journal'],
                                                     str) and new_entry['journal'].startswith('arXiv preprint'):
                new_entry['journal'] = new_entry['journal'].replace('arXiv preprint ', '')
            # check journal
            if 'journal' in new_entry and isinstance(new_entry['journal'],
                                                     str) and not new_entry['journal'].startswith('arXiv:'):
                journal_text = new_entry['journal'].lower()
                new_journal = None
                if 'pattern analysis and machine intelligence' in journal_text or 'pami' in journal_text:
                    new_journal = 'iccvw'
                else:
                    new_journal = input(f'Unknown journal name: {new_entry["journal"]}\n'
                                        f'> Please enter the abbreviation(Leave it for not changing): ')
                if new_journal is not None and new_journal != '':
                    new_entry['journal'] = BibDataStringExpression([BibDataString(new_bib_database, new_journal)])

        # check duplication
        if new_entry['ID'].lower() in all_ids or new_entry['title'].lower() in all_titles:
            print(f'Entry has already exists, please check: (ID: {new_entry["ID"].lower() in all_ids}, '
                  f'title: {new_entry["title"].lower() in all_titles})')
            print(new_entry)
            input('Press any to continue (will not add it to the new bib file):')
            continue
        # append to the database
        new_bib_database.entries.append(new_entry)
        all_ids.append(new_entry['ID'].lower())
        all_titles.append(new_entry['title'].lower())

    writer = BibTexWriter()
    writer.indent = '    '  # indent entries with 4 spaces instead of one
    # write to the new bib file
    with open(args.output, 'w', encoding='utf-8') as bibtex_file:
        bibtex_file.write(writer.write(new_bib_database))

    # add shortname bib string to the bib file
    with open(args.output, 'r+', encoding='utf-8') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(SHORTNAME_BIBSTR.rstrip('\r\n') + '\n\n' + content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', type=str, help='Input path to *.bib file', default='bib.bib')
    parser.add_argument('--output', type=str, help='Output path to *.bib file', default='bib_clean.bib')
    args = parser.parse_args()
    main(args)
