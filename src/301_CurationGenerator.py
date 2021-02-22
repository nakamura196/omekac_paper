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

canvases = {}

def conduct_item(api_data):

    elements = api_data["element_texts"]

    canvas = ""
    uuid = ""
    manifest = ""

    for e in elements:
        id = e["element"]["id"]
        value = e["text"]

        if id == 55:
            canvas = value

        if id == 65:
            uuid = value

        if id == 48:
            manifest = value

    if manifest not in canvases:
        canvases[manifest] = {}
    if uuid not in canvases[manifest]:
        canvases[manifest][uuid] = {
            "@id" : canvas
        }

files = glob.glob("../docs/api/items/*.json")

map = {}

count = 0
for i in range(0, len(files)):
    file = files[i]

    if i % 100 == 0:
        print(i)
    # print(file)

    with open(file) as f:
        api_data = json.load(f)

    if api_data["item_type"] == None or api_data["item_type"]["id"] != 18:
        conduct_item(api_data)
        continue

    elements = api_data["element_texts"]

    region = ""
    canvas = ""
    description = ""

    metadata = []

    for e in elements:
        id = e["element"]["id"]
        value = e["text"]

        if id == 64:
            region = value

        if id == 62:
            canvas = value

        if id == 1:
            description = value

    for tag in api_data["tags"]:
        metadata.append({
            "label" : "tags",
            "value" : tag["name"]
        })
    
    if canvas not in map:
        map[canvas] = []

    count += 1
    
    map[canvas].append({
        "label" : "[{}]".format(count),
        "xywh" : region,
        "description" : description,
        "metadata" : metadata
    })

print(count)

selections = []

for manifest in canvases:

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

    canvas_map = {}
    cs = m["sequences"][0]["canvases"]

    for c in cs:
        metadata = c["metadata"]
        canvas_map[c["@id"]] = metadata

    members = []
    selection = {
        "@id" : "https://nakamura196.github.io/omekac_paper/iiif/" + hash + "/range",
        "@type" : "sc:Range",
        "label" : m["label"],
        "within" : {
            "@id" : manifest,
            "@type" : "https://nakamura196.github.io/omekac_paper/iiif/" + hash + "/manifest.json",
            "label" : m["label"]
        },
        "members" : members
    }
    selections.append(selection)

    for uuid in canvases[manifest]:
        if uuid in map:
            canvas = canvases[manifest][uuid]
            arr = map[uuid]

            for obj in arr:
                member_id = canvas["@id"]+"#xywh="+obj["xywh"]

                metadata2 = obj["metadata"]

                for obj2 in canvas_map[canvas["@id"]]:
                    metadata2.append(obj2)

                members.append({
                    "@id" : member_id,
                    "@type" : "sc:Canvas",
                    "label" : obj["label"],
                    "metadata" : metadata2,
                    "description" : obj["description"]
                })

    
curation = {
    "@context" : [
        "http://iiif.io/api/presentation/2/context.json",
        "http://codh.rois.ac.jp/iiif/curation/1/context.json"
    ],
    "@type" : "cr:Curation",
    "@id" : "https://nakamura196.github.io/omekac_paper/iiif/curation/top.json",
    "label" : "紙質分析アノテーション",
    "selections" : selections
}

with open("../docs/iiif/curation/top.json", 'w') as outfile:
    json.dump(curation, outfile, ensure_ascii=False,
                indent=4, sort_keys=True, separators=(',', ': '))