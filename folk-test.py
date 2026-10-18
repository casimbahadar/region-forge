import asyncio, pathlib
from playwright.async_api import async_playwright
HTML=pathlib.Path('/mnt/user-data/outputs/index.html').as_uri()
R=[]
def chk(l,ok,d=""):
    ok=bool(ok);R.append(ok);print(("PASS  " if ok else "FAIL  ")+l+(f"  [{d}]" if d else ""))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",args=["--no-sandbox"])
        pg=await (await b.new_context(viewport={"width":430,"height":900})).new_page()
        errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
        await pg.goto(HTML); await pg.wait_for_function("typeof RF!=='undefined'")
        await pg.evaluate("()=>{localStorage.clear();indexedDB.deleteDatabase('region-forge')}")
        await pg.reload(); await pg.wait_for_function("typeof RF!=='undefined'")
        await pg.evaluate("()=>{document.getElementById('seed').value='city2'}")
        await pg.click("#go"); await pg.wait_for_selector("#starter:not(.hide)",timeout=30000)
        await pg.click("#startopts .card"); await pg.wait_for_selector("#out:not(.hide)")
        await pg.wait_for_timeout(1200)
        c=await pg.evaluate("""async()=>{const W=ms=>new Promise(r=>setTimeout(r,ms));if(BT.on){endBattle(false);await W(1100)}
          const n=RF.REGION().nodes.find(x=>x.kind==='town'&&isCity(x)&&['coast','lake'].includes(habitatOf(x)))||RF.REGION().nodes.find(x=>x.kind==='town'&&isCity(x));
          n._gen=null;RF.enterNode(n);await W(400);if(BT.on){endBattle(false);await W(1100)}
          return {name:n.name,hab:habitatOf(n),folk:F.gen.folk.length,tier:F.gen.tier}}""")
        print(f"      in {c['name']} ({c['tier']}, {c['hab']}) with {c['folk']} people")
        # watch them for a while
        wd=await pg.evaluate("""async()=>{const W=ms=>new Promise(r=>setTimeout(r,ms));const g=F.gen,m=g.map;
          const start=g.folk.map(f=>[f.x,f.y]);let bad=[],moves=0;
          for(let t=0;t<30;t++){folkTick();
            for(const f of g.folk){const t2=m.get(f.x,f.y);
              if(t2===TER.WATER&&!(m.get(f.x,f.y)===TER.PATH))bad.push('water');
              if((g.doors||[]).some(d=>d.x===f.x&&d.y===f.y))bad.push('door');
              if(f.x===F.tx&&f.y===F.ty)bad.push('player');
              if(Math.abs(f.x-f.home[0])>f.r||Math.abs(f.y-f.home[1])>f.r)bad.push('strayed');
              if(m.obj(f.x,f.y)!==OBJ.NPC)bad.push('lost')}}
          g.folk.forEach((f,i)=>{if(f.x!==start[i][0]||f.y!==start[i][1])moves++});
          return {moves,bad:[...new Set(bad)]}}""")
        chk("people wander around", wd['moves']>0, f"{wd['moves']} of {c['folk']} moved")
        chk("never into water, doors or you, and never far from home", not wd['bad'], str(wd['bad']))
        # talk with A, and by bumping into them
        tk=await pg.evaluate("""async()=>{const W=ms=>new Promise(r=>setTimeout(r,ms));const g=F.gen,m=g.map;
          const f=g.folk.find(q=>[[0,1],[0,-1],[1,0],[-1,0]].some(([a,c])=>!m.solid(q.x+a,q.y+c)&&m.obj(q.x+a,q.y+c)===OBJ.NONE));
          const[a,c]=[[0,1],[0,-1],[1,0],[-1,0]].find(([a,c])=>!m.solid(f.x+a,f.y+c)&&m.obj(f.x+a,f.y+c)===OBJ.NONE);
          F.tx=f.x+a;F.ty=f.y+c;F.px=F.tx;F.py=F.ty;
          document.querySelectorAll('.toast').forEach(t=>t.remove());interact();await W(60);
          const said=[...document.querySelectorAll('.toast')].map(t=>t.textContent).join(' | ');
          const faced=f.face;document.querySelectorAll('.toast').forEach(t=>t.remove());
          step(-a,-c);await W(60);const bump=[...document.querySelectorAll('.toast')].map(t=>t.textContent).join(' | ');
          return {said,bump,battle:BT.on,line:f.line,name:f.name,faced,want:a>0?'r':a<0?'l':c>0?'d':'u'}}""")
        chk("pressing A beside someone, they say something", tk['said'] and tk['name'] in tk['said'] and tk['line'] in tk['said'], tk['said'][:90])
        chk("and they turn to face you", tk['faced']==tk['want'], f"{tk['faced']} vs {tk['want']}")
        chk("bumping into them talks too, and never starts a battle", tk['bump'] and not tk['battle'], tk['bump'][:60])
        # the waterside: the pier is reachable
        pr=await pg.evaluate("""()=>{const g=F.gen,m=g.map;let pier=0;
          for(let i=0;i<m.t.length;i++){const x=i%m.w,y=(i/m.w)|0;if(m.t[i]===TER.PATH&&[[1,0],[-1,0],[0,1],[0,-1]].filter(([a,c])=>m.get(x+a,y+c)===TER.WATER).length>=2)pier++}
          const reach=new Set([g.entry.join(',')]),q=[g.entry];
          while(q.length){const[x,y]=q.shift();for(const[a,c]of[[1,0],[-1,0],[0,1],[0,-1]]){const nx=x+a,ny=y+c,k=nx+','+ny;
            if(nx<0||ny<0||nx>=m.w||ny>=m.h||reach.has(k)||m.solid(nx,ny))continue;reach.add(k);q.push([nx,ny])}}
          let onPier=0;for(let i=0;i<m.t.length;i++){const x=i%m.w,y=(i/m.w)|0;if(m.t[i]===TER.PATH&&reach.has(x+','+y)&&[[1,0],[-1,0],[0,1],[0,-1]].filter(([a,c])=>m.get(x+a,y+c)===TER.WATER).length>=2)onPier++}
          return {pier,onPier,sand:m.t.filter(v=>v===TER.SAND).length}}""")
        if c['hab'] in ('coast','lake'): chk("the pier out over the water can be walked onto", pr['pier']>0 and pr['onPier']>0, str(pr))
        # the guide asks a city for its signature building
        wz=await pg.evaluate("()=>wzRolesFor(F.node,F.gen)")
        chk("the tile guide asks a city for its signature building", 'signature' in wz, str(wz))
        # copying the city keeps people as people
        cp=await pg.evaluate("""()=>{const r=meCopyPlace();const L=r.L;
          const persons=L.things.filter(t=>t.kind==='person'),trainers=L.things.filter(t=>t.kind==='trainer');
          const g=buildCustom(L,F.node);return {persons:persons.length,trainers:trainers.length,folk:g.folk.length,want:F.gen.folk.length,
            signs:L.things.filter(t=>t.kind==='sign').map(t=>t.text).slice(0,2)}}""")
        chk("copying the city keeps its people as people, not trainers", cp['persons']==cp['want'] and cp['trainers']==0 and cp['folk']==cp['want'], str(cp))
        chk("and its signs keep their own words", any('Welcome' in t or 'Gym' in t for t in cp['signs']), str(cp['signs']))
        chk("no page errors", not errs, "; ".join(errs[:2]))
        await b.close()
    print("\n"+"="*46);print(f"{sum(R)}/{len(R)} passed")
asyncio.run(main())
