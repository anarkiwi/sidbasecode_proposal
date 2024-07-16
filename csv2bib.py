#!/usr/bin/env python

import hashlib
import pandas as pd

df = pd.read_csv("references.csv", header=None, names=["description", "url"])
for r in df.itertuples():
    h = hashlib.sha256()
    h.update(r.description.encode("utf8"))
    d = h.hexdigest()
    print("@misc{%s, title = {%s}, howpublished = {\\url{%s}},}" % (d, r.description, r.url))
