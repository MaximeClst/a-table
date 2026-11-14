from pathlib import Path
import json,re,html
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent/'dist'
def fmt(x):return f'{x:g}'.replace('.',',')
labels={'poulet':'Filet de poulet','steak':'Steak haché 20 % MG','thon':'Thon au naturel','sardines':'Sardines à l’huile','riz':'Riz blanc','pates':'Pâtes classiques','pdt':'Pommes de terre','haricots':'Haricots verts','tomate':'Tomates','concombre':'Concombre','pomme':'Pomme','poire':'Poire','banane':'Banane','cacahuete':'Beurre de cacahuète','huile':'Huile','whey':'Whey goût cookies','jus':'Jus de pomme sans sucres ajoutés','fromage_blanc':'Fromage blanc 0 %','oeuf':'Œufs entiers','biscotte_seigle':'Biscottes de seigle','galette':'Galettes de riz'}
menus=json.loads((root/'menus/calculs-menus-v11.json').read_text());days=[]
def ings(q):
 out=[]
 for k,v in q.items():
  unit='g';state=''
  if k in ['oeuf','biscotte_seigle','galette']:v=v/{'oeuf':50,'biscotte_seigle':10,'galette':7}[k];unit='';state={'oeuf':'à cuire, jaunes conservés','biscotte_seigle':'10 g / pièce estimés','galette':'7 g / pièce estimés'}[k]
  elif k=='jus':unit='ml'
  elif k in ['poulet','steak','riz','pates']:state='pesé cuit'
  elif k=='pdt':state='épluchées, cuites à l’eau'
  elif k in ['thon','sardines','haricots']:state='égoutté'
  out.append({'key':k,'name':labels[k],'amount':fmt(v)+(' '+unit if unit else ''),'state':state})
 return out
for name,day in menus.items():
 meals=[{'name':m['prise'],'ingredients':ings(m['quantites_g_sauf_jus_ml']),'q':m['quantites_g_sauf_jus_ml'],'macros':m['apports']} for m in day['prises']]
 breakfasts=[{'id':o['id'],'label':o['libelle'],'ingredients':ings(o['prise']['quantites_g_sauf_jus_ml']),'q':o['prise']['quantites_g_sauf_jus_ml'],'macros':o['prise']['apports'],'note':o['prise'].get('note','')} for o in day.get('options_petit_dejeuner',[])]
 days.append({'name':name,'type':'training' if 'Entraînement' in name else 'rest','meals':meals,'breakfasts':breakfasts,'total':day['total']})
shopkeys=[('Œufs','oeuf'),('Filets de poulet','poulet'),('Fromage blanc','fromage_blanc'),('Sardines','sardines'),('Biscottes','biscotte_seigle'),('Galettes','galette'),('Tomates','tomate'),('Concombre','concombre'),('Pommes de terre',None),('Pommes','pomme'),('Poires','poire'),('Huile','huile')]
shopping=[];current=None
for line in (root/'LISTE-COURSES-4-JOURS.md').read_text().splitlines():
 if line.startswith('## '):current={'title':line[3:],'items':[]}
 if line.startswith('<!--'):continue
 if line.startswith('| ☐'):
  row=[x.strip().replace('**','') for x in line.strip('|').split('|')]
  if not current['items']:shopping.append(current)
  name=row[0].replace('☐','').strip();key=next((k for p,k in shopkeys if name.startswith(p)),None)
  current['items'].append({'id':'item-'+str(sum(len(g['items']) for g in shopping)),'name':name,'quantity':row[1],'note':row[2],'key':key})
def inline(t):
 t=html.escape(t);t=re.sub(r'\*\*(.*?)\*\*',r'<strong>\1</strong>',t)
 t=re.sub(r'\[([^\]]+)\]\((https?[^)]+)\)',r'<a href="\2" target="_blank" rel="noopener">\1 ↗</a>',t)
 t=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',t);return t

def render(s):
 result=[];table=False
 for l in s.strip().splitlines():
  l=l.strip()
  if not l or l.startswith('<!--'):continue
  if l.startswith('|'):
   cells=[x.strip() for x in l.strip('|').split('|')]
   if all(re.fullmatch('[-: ]+',c) for c in cells):continue
   if not table:result.append('<div class="table-scroll" tabindex="0" role="region" aria-label="Tableau, défilement horizontal possible"><table>');table=True;tag='th'
   else:tag='td'
   result.append('<tr>'+''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells)+'</tr>');continue
  if table:result.append('</table></div>');table=False
  if l.startswith('#'):result.append('<h4>'+inline(l.lstrip('# '))+'</h4>')
  elif l.startswith('- '):result.append('<p class="bullet">'+inline(l[2:])+'</p>')
  else:result.append('<p>'+inline(l)+'</p>')
 if table:result.append('</table></div>')
 return ''.join(result)
batch=(root/'BATCHCOOKING-4-JOURS.md').read_text();chunks=re.split(r'(?=^#{2,3} )',batch,flags=re.M);steps=[]
for c in chunks[1:]:
 heading,_,body=c.partition('\n');heading=heading.lstrip('# ')
 if not body.strip():continue
 steps.append({'title':heading,'html':render(body)})
notes=(root/'MENUS-4-JOURS-V11.md').read_text();sections=re.split(r'(?=^## )',notes,flags=re.M)
info=[{'title':c.split('\n')[0][3:],'html':render(c.split('\n',1)[1])} for c in sections if c.startswith(('## Pesées','## Cibles','## Idées','## Sources'))]
(out/'data.json').write_text(json.dumps({'edition':'2026-11-14-v11','days':days,'shopping':shopping,'steps':steps,'info':info},ensure_ascii=False))
print('4 journées,',sum(len(d['breakfasts']) for d in days),'petits déjeuners au choix,',sum(len(d['meals']) for d in days),'repas,',sum(len(g['items']) for g in shopping),'courses,',len(steps),'étapes')
