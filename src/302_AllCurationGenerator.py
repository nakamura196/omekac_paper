import sys
import urllib
import json
import argparse
import requests
import os
import shutil
import yaml
import glob
import hashlib

files = glob.glob("../docs/api/collections/*.json")

selections = []

for i in range(0, len(files)):
    file = files[i]

    if i % 100 == 0:
        print(i)
    # print(file)

    with open(file) as f:
        api_data = json.load(f)

    elements = api_data["element_texts"]

    manifest = ""

    for e in elements:
        id = e["element"]["id"]
        value = e["text"]

        if id == 57:
            manifest = value
    
    
    if manifest == "":
        continue

    print(manifest)

    hash = hashlib.md5(manifest.encode('utf-8')).hexdigest()
    file = "../docs/iiif/"+hash+"/manifest.json"

    if not os.path.exists(file):
        m = requests.get(manifest).json()

        dir = os.path.dirname(file)
        os.makedirs(dir, exist_ok=True)

        with open(file, 'w') as outfile:
            json.dump(m, outfile, ensure_ascii=False,
                        indent=4, sort_keys=True, separators=(',', ': '))

    with open(file) as f:
        m = json.load(f)

    if "sequences" not in m:
        continue
    cs = m["sequences"][0]["canvases"]

    members = []
    for c in cs:
        members.append({
            "@id" : c["@id"],
            "@type": "sc:Canvas",
            "description": "",
            "label": "",
            "metadata" : c["metadata"]
        })

    selections.append({
        "@id": manifest,
        "@type": "sc:Range",
        "label": m["label"],
        "members" : members,
        "within" : {
            "@id": manifest,
            "@type": "sc:Manifest",
            "label": m["label"]
        }
    })


    
curation = {
    "@context" : [
        "http://iiif.io/api/presentation/2/context.json",
        "http://codh.rois.ac.jp/iiif/curation/1/context.json"
    ],
    "@type" : "cr:Curation",
    "@id" : "https://nakamura196.github.io/omekac_paper/iiif/curation/all.json",
    "label" : "紙質分析DB",
    "selections" : selections
}

with open("../docs/iiif/curation/all.json", 'w') as outfile:
    json.dump(curation, outfile, ensure_ascii=False,
                indent=4, sort_keys=True, separators=(',', ': '))