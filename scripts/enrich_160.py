#!/usr/bin/env python3
"""Crossref/OpenAlex metadata enrichment. Standard library only; no automatic exclusions."""
import csv, difflib, html, json, os, re, sys, time, urllib.parse, urllib.request
from urllib.error import HTTPError, URLError
KEY=os.environ.get("OPENALEX_API_KEY","").strip()
EMAIL=os.environ.get("CONTACT_EMAIL","").strip()
UA="GenderedDigitalViolenceReview/1.0"+(f" (mailto:{EMAIL})" if EMAIL else "")
def norm(s):
    return re.sub(r"\\s+"," ",re.sub(r"[^\\w ]"," ",(s or "").casefold())).strip()
def sim(a,b):
    return round(difflib.SequenceMatcher(None,norm(a),norm(b)).ratio(),3)
def get(url):
    error=""
    for n in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"}),timeout=25) as f:
                return json.load(f),""
        except (HTTPError,URLError,TimeoutError,ValueError) as e:
            error=str(e)
            if isinstance(e,HTTPError) and e.code in (401,403):break
            time.sleep(1+n)
    return {},error
def cr(doi,title):
    root="https://api.crossref.org/works"
    if re.match(r"^10\\.\\d{4,9}/\\S+",doi,re.I):
        d,e=get(root+"/"+urllib.parse.quote(doi,safe="/"))
        if d.get("message"):return d["message"],e
    q=urllib.parse.urlencode({"query.title":title,"rows":3})
    d,e=get(root+"?"+q)
    arr=d.get("message",{}).get("items",[])
    return (max(arr,key=lambda x:sim(title,(x.get("title") or [""])[0])) if arr else {}),e
def oa(doi,title):
    if not KEY:return {},"OPENALEX_API_KEY missing"
    root="https://api.openalex.org/works"
    if re.match(r"^10\\.\\d{4,9}/\\S+",doi,re.I):
        d,e=get(root+"/https://doi.org/"+urllib.parse.quote(doi,safe="/")+"?"+urllib.parse.urlencode({"api_key":KEY}))
        if d.get("id"):return d,e
    d,e=get(root+"?"+urllib.parse.urlencode({"api_key":KEY,"search":title,"per-page":3}))
    arr=d.get("results",[])
    return (max(arr,key=lambda x:sim(title,x.get("title",""))) if arr else {}),e
def reconstruct(idx):
    if not isinstance(idx,dict):return ""
    positions={}
    for word,locs in idx.items():
        for i in locs:positions[i]=word
    return " ".join(positions[i] for i in sorted(positions))
def main():
    with open("data/cola_160_openalex_crossref.csv",encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=160:raise SystemExit(f"Expected 160 records, found {len(rows)}")
    os.makedirs("results",exist_ok=True)
    cols=["record_id","title_base","doi_base","crossref_title","crossref_doi","crossref_similarity","crossref_abstract","crossref_url","crossref_error","openalex_title","openalex_doi","openalex_similarity","openalex_abstract","openalex_url","openalex_oa_url","openalex_error","match_assessment"]
    with open("results/enriquecimiento_api_160.csv","w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
        for i,r in enumerate(rows,1):
            title=r["title"];doi=(r.get("doi") or "").strip()
            c,ce=cr(doi,title);o,oe=oa(doi,title)
            ct=(c.get("title") or [""])[0];ot=o.get("title","")
            cs=sim(title,ct) if ct else 0;oscore=sim(title,ot) if ot else 0
            status="High title similarity; eligibility NOT verified" if max(cs,oscore)>=.92 else ("Manual match check" if max(cs,oscore)>=.75 else "No reliable metadata match")
            writer.writerow(dict(record_id=r["record_id"],title_base=title,doi_base=doi,crossref_title=ct,crossref_doi=c.get("DOI",""),crossref_similarity=cs,crossref_abstract=html.unescape(re.sub("<[^>]*>"," ",c.get("abstract",""))).strip(),crossref_url=c.get("URL",""),crossref_error=ce,openalex_title=ot,openalex_doi=o.get("doi",""),openalex_similarity=oscore,openalex_abstract=reconstruct(o.get("abstract_inverted_index")),openalex_url=o.get("id",""),openalex_oa_url=(o.get("best_oa_location") or {}).get("landing_page_url","") or (o.get("best_oa_location") or {}).get("pdf_url",""),openalex_error=oe,match_assessment=status))
            f.flush()
            print(f"{i}/{len(rows)} {r['record_id']} {status}",flush=True)
            time.sleep(.15)
if __name__=="__main__":main()
