#!/usr/bin/env python3
"""Recover DOI-resolved open full text URLs and full-text content; preserve provenance."""
import csv,json,os,re,time,urllib.request,urllib.parse,urllib.error
from pathlib import Path
ROOT=Path("outputs");ROOT.mkdir(exist_ok=True)
inp=Path("data/cola_355_doi.csv")
if not inp.exists():inp=Path("data/cola_160_openalex_crossref.csv")
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"GDVReview/1.0 (academic literature audit)","Accept":"application/json"})
 try:
  with urllib.request.urlopen(req,timeout=22) as f:return json.load(f),None
 except Exception as e:return None,str(e)[:250]
def field(row,*keys):
 for k in keys:
  if row.get(k):return str(row[k]).strip()
 return ""
def normdoi(d):
 return re.sub(r"^https?://(?:dx\.)?doi\.org/","",d.strip(),flags=re.I).lower()
with inp.open(encoding="utf-8-sig",newline="") as f:records=list(csv.DictReader(f))
results=[]
for i,r in enumerate(records):
 rid=field(r,"record_id","ID","id")
 title=field(r,"title","title_base","Título")
 doi=normdoi(field(r,"doi","doi_base","DOI"))
 if not doi:
  results.append(dict(id=rid,title=title,doi="",status="sin_doi",openalex_url="",oa_url="",pdf_url="",license="",error=""));continue
 url="https://api.openalex.org/works/https://doi.org/"+urllib.parse.quote(doi,safe="/")
 obj,err=get(url)
 if obj is None:
  results.append(dict(id=rid,title=title,doi=doi,status="api_error",openalex_url="",oa_url="",pdf_url="",license="",error=err));continue
 locations=[obj.get("best_oa_location") or {},obj.get("primary_location") or {}]+(obj.get("locations") or [])
 oa_url=pdf_url=license=""
 for loc in locations:
  if not oa_url and loc.get("landing_page_url"):oa_url=loc["landing_page_url"]
  if not pdf_url and loc.get("pdf_url"):pdf_url=loc["pdf_url"]
  if not license and loc.get("license"):license=loc["license"]
 results.append(dict(id=rid,title=title or obj.get("title",""),doi=doi,status="oa_url" if (oa_url or pdf_url) else "sin_enlace_oa",openalex_url=obj.get("id",""),oa_url=oa_url,pdf_url=pdf_url,license=license,error=""))
 if (i+1)%25==0:print("processed",i+1,"/",len(records),flush=True)
 time.sleep(.2)
with (ROOT/"enlaces_texto_completo.csv").open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["id","title","doi","status","openalex_url","oa_url","pdf_url","license","error"]);w.writeheader();w.writerows(results)
print("SUMMARY",len(results),{s:sum(x["status"]==s for x in results) for s in set(x["status"] for x in results)})
