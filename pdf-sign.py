#!/usr/bin/python3
# pylint: disable=maybe-no-member

from endesive import pdf, hsm
import os
import sys
import datetime
import PyKCS11 as PK11
import asn1crypto
import argparse
import getpass
import re



class KnownException(Exception):
    pass

class Signer(hsm.HSM):
    def __init__(self, args):
        try:
            super().__init__(args.card_reader)
        except PK11.PyKCS11Error:
            raise KnownException(f"cannot load card reader driver: {args.card_reader}")

        # find the label of the first pkcs11 slot
        slots = self.pkcs11.getSlotList(tokenPresent=True)
        if len(slots) == 0:
            raise KnownException("cannot read card")

        info = self.pkcs11.getTokenInfo(slots[0])
        label = info.label.split('\0')[0].strip()

        try:
            self.login(label, args.pin)
        except PK11.PyKCS11Error as e:
            if e.value == PK11.CKR_PIN_INCORRECT:
                raise KnownException("incorrect pin")
            else:
                raise

        # select certificate
        self.keyid = None
        self.cert = None
        self.common_name = None

        pk11objects = self.session.findObjects([(PK11.CKA_CLASS, PK11.CKO_CERTIFICATE)])
        all_attributes = [
            PK11.CKA_SUBJECT,
            PK11.CKA_VALUE,
            PK11.CKA_ID,
        ]

        for pk11object in pk11objects:
            try:
                attributes = self.session.getAttributeValue(pk11object, all_attributes)
            except PK11.PyKCS11Error as e:
                continue

            attrDict = dict(list(zip(all_attributes, attributes)))
            subject = asn1crypto.x509.Name.load(bytes(attrDict[PK11.CKA_SUBJECT])).native

            # Select the personal certificate, the one with the "surname" field
            if 'surname' in subject:
                self.keyid = bytes(attrDict[PK11.CKA_ID])
                self.cert = bytes(attrDict[PK11.CKA_VALUE])
                self.common_name = subject['common_name']
                break

    def certificate(self):
        return self.keyid, self.cert

    def sign(self, keyid, data, mech):
        privKey = self.session.findObjects([(PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY), (PK11.CKA_ID, keyid)])[0]
        mech = getattr(PK11, 'CKM_%s_RSA_PKCS' % mech.upper())
        sig = self.session.sign(privKey, data, PK11.Mechanism(mech, None))
        return bytes(sig)




def main():
    def parse_pos(val):
        pos = val.split(',')
        if len(pos) != 2:
            raise argparse.ArgumentTypeError(f'{val} is not of the form X,Y')
        return int(pos[0]), int(pos[1])

    parser = argparse.ArgumentParser()
    parser.add_argument('pdf', metavar='PDF', type=str,
                        help='path to pdf file')
    parser.add_argument('--pin',
                        type=str,
                        help='the card pin.')
    parser.add_argument('--stamp-page', metavar='N',
                        default=0, type=int,
                        help='the page to add a visible signature stamp. 0 (default) to disable the stamp.')
    parser.add_argument('--stamp-pos', metavar='X,Y',
                        type=parse_pos,
                        default=(200,20),
                        help='the X,Y coordinates (relative to the bottom-left corner) of the visible signature stamp.')
    parser.add_argument('--out-file', metavar='FILE',
                        type=str,
                        help='the path of the signed pdf file. The default is to add the -signed suffix to the input PDF')
    parser.add_argument('--tsa', metavar='URL',
                        default="http://qts.harica.gr/",
                        type=str,
                        help='URL of the timestamp server. Default: http://qts.harica.gr/')
    parser.add_argument('--card-reader', metavar='FILE',
                        default="libgclib.so",
                        type=str,
                        help='driver (.so/.dll file) of the card reader. Default: libgclib.so')


    args = parser.parse_args()

    if not os.path.isfile(args.pdf):
        raise KnownException(f"{args.pdf}: no such file")

    if args.pin is None:
        args.pin = getpass.getpass(prompt='Enter your PIN: ') 

    if args.out_file is None:
        args.out_file = re.sub(".(pdf)", "-signed.\\1", args.pdf, flags=re.I)


    date = datetime.datetime.utcnow().strftime('D:%Y%m%d%H%M%S+00\'00\'')
    local_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    hsm = Signer(args)
    info = {
        'sigflags': 3,
        'contact': '',
        'location': '',
        'signingdate': date.encode(),
        'reason': '',
    }

    if args.stamp_page != 0:
        info['sigpage'] = args.stamp_page - 1   # 0-based
        info['signature'] = f'Digitally signed by {hsm.common_name}\nDate: {local_date}'
        info['signaturebox'] = (args.stamp_pos[0], args.stamp_pos[1], args.stamp_pos[0] + 270, args.stamp_pos[1] + 60)
        info['sigbutton'] = True

    pdf_data = open(args.pdf, 'rb').read()
    pdf_sig = pdf.cms.sign(pdf_data, info,
        None, None,
        [],
        'sha256',
        hsm,
        args.tsa,
    )
    hsm.logout()

    with open(args.out_file, 'wb') as fp:
        fp.write(pdf_data)
        fp.write(pdf_sig)

    print(f"signed pdf written to {args.out_file}")


try:
    main()
except KnownException as e:
    print(e, file=sys.stderr)
    sys.exit(-1)
