from flask import Flask, make_response
import json
import re
import time
import pprint
import requests
import difflib

def get_diffs(request):

    id1 = str(request.args.get('id1'))
    id2 = str(request.args.get('id2'))
    r0 = requests.get('https://ga-create-api.s3.amazonaws.com/' + id1)
    r1 = requests.get('https://ga-create-api.s3.amazonaws.com/' + id2)
    fmt = request.args.get('fmt')

#    print(f'request is {request}')
#    print(f'vars: {id1}{id2}{fmt}')
#    print(f'response urls: {r0.url}\n{r1.url}')
#    print(f'response codes: {r0.status_code}{type(r0.status_code)}{r1.status_code}{type(r1.status_code)}')

    if r0.status_code == 200 & r1.status_code == 200:

        # optional api with ?fmt=text param for curl use
        if fmt == 'text':

            diff = difflib.unified_diff(
                pprint.pformat(json.loads(r0.content)).splitlines(),
                pprint.pformat(json.loads(r1.content)).splitlines(),
                id1,
                id2
            )
            resp = make_response('\n'.join(diff))
            return resp

        else:

            # this doesn't actually remove material, it just prevents it from being parsed
            # the cleanjunk() function is the thing that actually removes activityID lines from output
            diff = difflib.HtmlDiff(linejunk=(lambda line: False if re.match(r'^.*\b(activityId)\b.*$', line) is None else True))
            resp = make_response(diff.make_file(
                [cleanjunk(line) for line in pprint.pformat(json.loads(r0.content)).splitlines()],
                [cleanjunk(line) for line in pprint.pformat(json.loads(r1.content)).splitlines()],
                fromdesc=id1,
                todesc=id2,
                context=True,
                numlines=3
            ))
            return resp

    else:
        resp = make_response(str('Call to lesson endpoint failed.<br><br>Endpoint #1 status: ' + str(r0.status_code) + '<br>Endpoint #2 status: ' + str(r0.status_code)))
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
        return resp

def cleanjunk(line):
    if re.match(r'^.*\b(activityId)\b.*$', line) is None:
        return line
    else:
        return "#"
