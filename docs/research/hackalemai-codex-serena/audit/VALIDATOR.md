# Reproduce the local static checks

This is a preparation/audit utility, **not product code**. It does not install dependencies, execute fenced setup commands, start Codex/Serena, fetch sources or change package files. Its recipe assertions are a bounded model of the inspected source contracts, not a complete vendor schema validator.

Extract the Python fence to a temporary file outside the submission repository and run it against the unpacked revision. Python 3.11+ is needed for tomllib; dependencies are PyYAML, markdown-it-py and pathspec. The report records the versions actually used here. Pin and provision those separately when reproducing the check. Do not assume they belong in the application dependency graph.

The utility reads all Markdown, validates UTF-8/LF, links, skill metadata, fenced JSON/YAML/TOML/Python syntax, the payload manifest and selected recipe constraints. Its negative controls must be rejected for their expected classes of errors. Expected rejection by this utility is **not execution of Codex's own parser**.

Example invocation after extracting the fence: `python /tmp/validate_pack.py /absolute/path/to/unpacked-pack`. A nonzero exit is a check failure. `--without-manifest` is only a packaging-stage diagnostic, not final validation.

````python
"""Read-only Markdown package checks. Does not install or execute documented tools."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from copy import deepcopy
import argparse, ast, hashlib, importlib.metadata, json, re, sys, tomllib, unicodedata
import yaml
from markdown_it import MarkdownIt
import pathspec

class DuplicateKey(ValueError):
    pass

class StrictLoader(yaml.SafeLoader):
    pass

def strict_mapping(loader, node, deep=False):
    seen={}
    for k_node, v_node in node.value:
        k=loader.construct_object(k_node, deep=deep)
        if k in seen:
            raise DuplicateKey(f'duplicate YAML key: {k}')
        seen[k]=loader.construct_object(v_node, deep=deep)
    return seen
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, strict_mapping)

def json_pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise DuplicateKey(f'duplicate JSON key: {k}')
        out[k]=v
    return out

def nonfinite_constant(value):
    raise ValueError('non-finite token is not JSON: '+value)

def parse_json(s):
    return json.loads(s, object_pairs_hook=json_pairs, parse_constant=nonfinite_constant)

def slug(s):
    # GitHub-style anchors for this pack's headings, not a universal renderer.
    s=s.strip().lower().replace('`','')
    s=''.join(c for c in s if c in '-_ ' or not unicodedata.category(c).startswith(('P','S')))
    return s.replace(' ','-')

def parsed(path):
    return MarkdownIt('commonmark').enable('table').parse(path.read_text())

def anchors(tokens):
    result=set();used={}
    for i,t in enumerate(tokens):
        if t.type=='heading_open':
            a=slug(tokens[i+1].content);n=used.get(a,0);used[a]=n+1
            result.add(a+(f'-{n}' if n else ''))
    return result

def check_fence(token, lines):
    if token.type!='fence':return
    final=lines[token.map[1]-1].strip() if token.map and token.map[1] else ''
    if not re.fullmatch(re.escape(token.markup[0])+'{'+str(len(token.markup))+r',}\s*',final):
        raise ValueError(f'unclosed fence at line {(token.map or [0])[0]+1}')

def safe_local(root, base, dest):
    parts=urlsplit(dest)
    if parts.scheme or parts.netloc:return None
    p=(base/unquote(parts.path)).resolve() if parts.path else base
    # Caller passes current file when fragment-only.
    if not p.is_relative_to(root.resolve()):raise ValueError('link escapes package')
    if not p.exists():raise FileNotFoundError(str(p))
    return p,unquote(parts.fragment)

def check_skill(path):
    s=path.read_text()
    if not s.startswith('---\n'):raise ValueError('skill frontmatter missing')
    data=yaml.load(s.split('---\n',2)[1],Loader=StrictLoader)
    if data.get('name')!=path.parent.name:raise ValueError('skill name mismatch')
    if not re.fullmatch(r'[a-z0-9-]{1,64}',data['name']):raise ValueError('skill name invalid')
    if not isinstance(data.get('description'),str) or not data['description'].strip():raise ValueError('skill description invalid')
    return data

def check_hook(h):
    for event,groups in h.get('hooks',{}).items():
        for group in groups:
            for handler in group.get('hooks',[]):
                if handler.get('type')!='command':raise ValueError('recipe expects command hooks')
                if type(handler.get('timeout',1)) is not int:raise ValueError('hook timeout must be an integer')
                if event=='SessionEnd' and not 1<=handler.get('timeout',1)<=3:raise ValueError('SessionEnd effective budget exceeds 3')
                if ' reset' in handler.get('command','') or ' remind' in handler.get('command',''):raise ValueError('unselected hook command')

def check_project(p):
    if 'base_modes' in p:raise ValueError('stable project base_modes is ignored')
    if 'languages' in p:raise ValueError('use canonical language_servers in this recipe')
    ls=p.get('language_servers',[])
    selected={'python_ty','python','python_basedpyright','typescript','typescript_vts','bash','markdown','yaml','json','toml','html','scss','rust','go','dart','cpp','swift','java','kotlin','latex','hlsl'}
    if not set(ls)<=selected:raise ValueError('adapter not in the selected verified catalogue')
    if sum(x.startswith('python') for x in ls)>1:raise ValueError('multiple Python primary providers')
    if sum(x.startswith('typescript') for x in ls)>1:raise ValueError('multiple TypeScript primary providers')
    spec=pathspec.PathSpec.from_lines('gitwildmatch',p.get('ignored_paths',[]))
    for name in ['services/api/build/plan.py','apps/web/dist/authored.ts','packages/target/symbols.py','services/uploads/metadata.py']:
        if spec.match_file(name):raise ValueError('generic ignore hides authored-path control: '+name)

def check_global(g,client):
    if g.get('base_modes')!=['editing']:raise ValueError('unexpected autonomous profile base modes')
    if g.get('tool_timeout',240)>=client['mcp_servers']['serena']['tool_timeout_sec']:raise ValueError('server budget not below caller budget')
    if '**' in g.get('trusted_project_path_patterns',[]):raise ValueError('wildcard trust not selected')

def check_merge(project,local):
    # Mirrors verified top-level dictionary update, not a package-runtime test.
    effective=deepcopy(project);effective.update(local)
    inherited=project.get('ls_specific_settings',{})
    actual=effective.get('ls_specific_settings',{})
    if not set(inherited)<=set(actual):raise ValueError('shallow local override dropped an LS entry')
    return effective

def validate(root, require_manifest=True):
    root=root.resolve(); errors=[];stats={'markdown_files':0,'utf8_lf_files':0,'relative_links':0,'skills':0,'fences':0,'json_fences':0,'yaml_fences':0,'toml_fences':0,'python_fences':0,'manifest_entries':0}
    files=sorted(root.rglob('*.md')); tokens_by={};blocks={}
    for p in files:
        name=str(p.relative_to(root));stats['markdown_files']+=1
        try:
            b=p.read_bytes();s=b.decode('utf-8')
            if b'\x00' in b or b'\r\n' in b or not b.endswith(b'\n'):raise ValueError('noncanonical authored text')
            stats['utf8_lf_files']+=1
            toks=parsed(p);tokens_by[p]=toks;lines=s.splitlines();blocks[name]=[]
            for t in toks:
                if t.type!='fence':continue
                check_fence(t,lines);stats['fences']+=1
                lang=t.info.split()[0] if t.info.split() else ''
                data=None
                if lang=='json':data=parse_json(t.content);stats['json_fences']+=1
                elif lang in ('yaml','yml'):data=yaml.load(t.content,Loader=StrictLoader);stats['yaml_fences']+=1
                elif lang=='toml':data=tomllib.loads(t.content);stats['toml_fences']+=1
                elif lang=='python':ast.parse(t.content);stats['python_fences']+=1
                blocks[name].append((lang,data,t.content))
            if p.name=='SKILL.md':check_skill(p);stats['skills']+=1
        except Exception as ex:errors.append(f'{name}: {ex}')
    for p,toks in tokens_by.items():
        for t in toks:
            for c in t.children or []:
                if c.type not in ('link_open','image'):continue
                dest=c.attrGet('href') if c.type=='link_open' else c.attrGet('src')
                if not dest:continue
                parts=urlsplit(dest)
                if parts.scheme or parts.netloc:continue
                stats['relative_links']+=1
                try:
                    base=p if not parts.path else p.parent
                    target,fragment=safe_local(root,base,dest)
                    if fragment and target.suffix=='.md' and fragment not in anchors(tokens_by.get(target,parsed(target))):raise ValueError(f'missing anchor {fragment}')
                except Exception as ex:errors.append(f'{p.relative_to(root)} -> {dest}: {ex}')
    # Recipe-specific assertions are intentionally bounded, not complete vendor schemas.
    if 'setup/CONFIG-RECIPES.md' in blocks:
        try:
            recipe=blocks['setup/CONFIG-RECIPES.md']
            y=[d for l,d,_ in recipe if l in ('yaml','yml')]
            t=[d for l,d,_ in recipe if l=='toml']
            if len(y)!=3 or len(t)!=1:raise ValueError('reviewed recipe layout changed')
            check_global(y[0],t[0]);check_project(y[1]);check_merge(y[1],y[2])
            hs=[d for l,d,_ in blocks['setup/HOOKS-AND-EXEC-POLICY.md'] if l=='json']
            for h in hs:check_hook(h)
            stats['source_derived_recipe_assertions']='PASS (bounded; not vendor-runtime validation)'
        except Exception as ex:errors.append('recipe assertions: '+str(ex))
    if require_manifest:
        try:
            rows=re.findall(r'\| `([^`]+)` \| (\d+) \| `([a-f0-9]{64})` \|',(root/'MANIFEST.md').read_text())
            names=[n for n,_,_ in rows]
            expected={str(p.relative_to(root)) for p in files if p.name!='MANIFEST.md'}
            if len(names)!=len(set(names)) or set(names)!=expected:raise ValueError('manifest inventory mismatch')
            for name,n,h in rows:
                b=(root/name).read_bytes()
                if len(b)!=int(n) or hashlib.sha256(b).hexdigest()!=h:raise ValueError('hash/size mismatch: '+name)
            stats['manifest_entries']=len(rows)
        except Exception as ex:errors.append('manifest: '+str(ex))
    stats['root_agents_bytes']=(root/'repo-policy/AGENTS.md').stat().st_size
    stats['max_root_plus_scoped_bytes']=stats['root_agents_bytes']+max(p.stat().st_size for p in (root/'scoped-templates').glob('*-AGENTS.md'))
    return stats,errors,blocks

def negatives(blocks,root):
    rows=[]
    def reject(name,fn):
        try:fn()
        except Exception as ex:rows.append({'id':name,'status':'EXPECTED-REJECTION','reason':str(ex)})
        else:rows.append({'id':name,'status':'FAILED-TO-REJECT'})
    reject('N01 duplicate JSON key',lambda:parse_json('{"a":1,"a":2}'))
    reject('N02 duplicate YAML key',lambda:yaml.load('a: 1\na: 2\n',Loader=StrictLoader))
    reject('N03 duplicate TOML key',lambda:tomllib.loads('a=1\na=2\n'))
    reject('N04 escaping relative link',lambda:safe_local(root,root,'../outside.md'))
    reject('N05 missing local document',lambda:safe_local(root,root,'nonexistent-negative-control.md'))
    y=[d for l,d,_ in blocks['setup/CONFIG-RECIPES.md'] if l=='yaml'];t=[d for l,d,_ in blocks['setup/CONFIG-RECIPES.md'] if l=='toml'][0]
    h=deepcopy([d for l,d,_ in blocks['setup/HOOKS-AND-EXEC-POLICY.md'] if l=='json'][0]);h['hooks']['SessionEnd'][0]['hooks'][0]['timeout']=5
    reject('N06 old SessionEnd five-second budget',lambda:check_hook(h))
    p=deepcopy(y[1]);p['base_modes']=['editing'];reject('N07 ignored project base_modes',lambda:check_project(p))
    p=deepcopy(y[1]);p['language_servers'].append('typescript_native');reject('N08 invented stable adapter ID',lambda:check_project(p))
    p=deepcopy(y[1]);p['language_servers'].append('python');reject('N09 competing Python providers',lambda:check_project(p))
    p=deepcopy(y[1]);p['ignored_paths'].append('**/build/**');reject('N10 authored build file hidden',lambda:check_project(p))
    local={'ls_specific_settings':{'python_ty':{'ls_path':'/synthetic/ty'}}};reject('N11 shallow override drops TS pin',lambda:check_merge(y[1],local))
    g=deepcopy(y[0]);g['tool_timeout']=240;reject('N12 server timeout above caller',lambda:check_global(g,t))
    g=deepcopy(y[0]);g['trusted_project_path_patterns']=['**'];reject('N13 wildcard project trust',lambda:check_global(g,t))
    toks=MarkdownIt().parse('```json\n{}\n');reject('N14 unclosed fence',lambda:check_fence(toks[0],['```json','{}']))
    reject('N15 non-finite JSON token',lambda:parse_json('{"value":NaN}'))
    h=deepcopy([d for l,d,_ in blocks['setup/HOOKS-AND-EXEC-POLICY.md'] if l=='json'][0]);h['hooks']['SessionEnd'][0]['hooks'][0]['timeout']=True
    reject('N16 boolean hook timeout',lambda:check_hook(h))
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--without-manifest',action='store_true');args=ap.parse_args()
    stats,errors,blocks=validate(args.root,not args.without_manifest);neg=negatives(blocks,args.root.resolve())
    if any(x['status']!='EXPECTED-REJECTION' for x in neg):errors.append('negative-control failure')
    print(json.dumps({'scope':'local read-only static checks; no vendor runtime or host execution','python':sys.version.split()[0], 'dependencies':{n:importlib.metadata.version(n) for n in ['PyYAML','markdown-it-py','pathspec']},'stats':stats,'negative_controls':neg,'errors':errors},indent=2,ensure_ascii=False))
    raise SystemExit(bool(errors))
if __name__=='__main__':main()

````
