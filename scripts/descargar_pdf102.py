#!/usr/bin/env python3
import csv,io,os,re,time,json,zipfile,urllib.request,urllib.parse,hashlib
from pathlib import Path
import fitz
ROOT=Path("outputs/pdf102");ROOT.mkdir(parents=True,exist_ok=True)
# This workflow needs the input CSV from the earlier successful run artifact.
# It is downloaded with GitHub Actions API by workflow, not from the user's machine.
source=Path("data/enlaces_texto_completo.csv")
if not source.exists():raise SystemExit("Missing data/enlaces_texto_completo.csv")
rows=list(csv.DictReader(source.open(encoding="utf-8-sig",newline="")))
rows=[r for r in rows if r.get("pdf_url")]
results=[]
for n,r in enumerate(rows,1):
 rid=r["id"];url=r["pdf_url"];status="";err="";pages=0;chars=0;sha=""
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (academic full text verification)","Accept":"application/pdf,*/*"})
  with urllib.request.urlopen(req,timeout=24) as f:
   payload=f.read(18000001)
   content_type=f.headers.get("Content-Type","")
  if len(payload)>18000000:raise ValueError("PDF >18 MB")
  if not payload.startswith(b"%PDF"):raise ValueError("Not a PDF (content-type="+content_type+")")
  doc=fitz.open(stream=payload,filetype="pdf");pages=len(doc)
  text="\n\n".join(f"--- PAGE {i+1} ---\n"+page.get_text("text") for i,page in enumerate(doc))
  chars=len(text);sha=hashlib.sha256(payload).hexdigest()
  if chars<400:raise ValueError("PDF contains no extractable text (scan/image?)")
  (ROOT/(rid+".txt")).write_text(text,encoding="utf8")
  status="full_text_extracted"
 except Exception as e:
  status="failed";err=str(e)[:300]
 results.append(dict(id=rid,title=r.get("title",""),doi=r.get("doi",""),pdf_url=url,status=status,pages=pages,characters=chars,sha256=sha,error=err))
 if n%10==0:print("Processed",n,"/",len(rows),flush=True)
 time.sleep(.15)
with (ROOT/"manifest.csv").open("w",encoding="utf8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
print("SUMMARY",len(results),"extracted",sum(x["status"]=="full_text_extracted" for x in results))
