#!/usr/bin/env python3

import json
import smtplib
import sys
from datetime import datetime
from email.message import EmailMessage

import requests
import io


class C19AppointmentCheck(object):
    def __init__(self, userid, starttoken, mailserver, mailport, mailuser, mailpass):
        self.userid = userid
        self.starttoken = starttoken
        self.mailserver = mailserver
        self.mailport = mailport
        self.mailuser = mailuser
        self.mailpass = mailpass
        self.tokenjar = self.get_tokenjar()

    def get_tokenjar(self):
        try:
            with io.open('tokenjar.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'refresh_token': self.starttoken}

    def save_tokenjar(self):
        with io.open('tokenjar.json', 'w+', encoding='utf-8') as f:
            f.write(json.dumps(self.tokenjar))

    def refresh_token(self):
        resp = requests.post(
            'https://ciam.impfzentren.bayern/auth/realms/C19V-Citizen/protocol/openid-connect/token',
            data={
                'client_id': 'c19v-frontend',
                'grant_type': 'refresh_token',
                'refresh_token': self.tokenjar['refresh_token']
            }
        )

        if 'refresh_token' in resp.json():
            self.tokenjar = resp.json()
        else:
            raise Exception()

    def get_appointments(self):
        resp = requests.get(
            'https://impfzentren.bayern/api/v1/citizens/{userid}/appointments/next?timeOfDay=ALL_DAY&lastDate={date}&lastTime=00%3A00'.format(
                userid=self.userid,
                date=datetime.today().strftime('%Y-%m-%d')
            ), headers={
                'Authorization': 'Bearer {refresh_token}'.format(refresh_token=self.tokenjar['access_token'])
            }
        )

        if resp.status_code == 404:
            print("{}: No new appointments found".format(datetime.now()))
        elif resp.status_code in [200, 201, 202]:
            print("{}: {}".format(
                datetime.now(),
                json.dumps(
                    resp.json(),
                    sort_keys=True, indent=4, separators=(',', ': ')
                ),
            ))
            return resp.json()
        elif resp.status_code == 500:
            # Site is probably just overloaded right now
            return
        else:
            raise Exception()

    def mail(self, recipient, subject, content):
        msg = EmailMessage()
        msg.set_content(content)

        msg['Subject'] = subject
        msg['From'] = self.mailuser
        msg['To'] = recipient

        try:
            smtp = smtplib.SMTP(self.mailserver, self.mailport)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.mailuser, self.mailpass)
            smtp.send_message(msg)
        except smtplib.SMTPException:
            print("SMTP Error")


if __name__ == '__main__':
    with io.open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    c19ac = C19AppointmentCheck(
        userid=config['userid'],
        starttoken=config['starttoken'],
        mailserver=config['mailserver'],
        mailport=config['mailport'],
        mailuser=config['mailuser'],
        mailpass=config['mailpass']
    )

    if config['sys_stop'] and (config['stop_on_success'] or config['stop_on_fail'] or config['stop_on_tokenfail']):
        sys.exit()

    try:
        c19ac.refresh_token()
    except:
        c19ac.mail(config['recipient'], '[C19AC] refresh_token() fail', 'Could not refresh Token')
        if config['stop_on_tokenfail']:
            config['sys_stop'] = True
    else:
        c19ac.save_tokenjar()

    try:
        appointments = c19ac.get_appointments()
    except:
        c19ac.mail(config['recipient'], '[C19AC] get_appointments() fail', 'Could not get appointments')
        if config['stop_on_fail']:
            config['sys_stop'] = True
    else:
        if appointments:
            c19ac.mail(config['recipient'], '[C19AC] get_appointments() success', json.dumps(
                appointments, sort_keys=True, indent=4, separators=(',', ': ')
            ))
            if config['stop_on_success']:
                config['sys_stop'] = True

    if config['sys_stop']:
        with io.open('config.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(
                config, sort_keys=True, indent=4, separators=(',', ': ')
            ))

