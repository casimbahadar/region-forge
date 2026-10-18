import asyncio, pathlib
from playwright.async_api import async_playwright
HTML=pathlib.Path('/mnt/user-data/outputs/index.html').as_uri()
R=[]
def chk(l,ok,d=""):
    ok=bool(ok);R.append(ok);print(("PASS  " if ok else "FAIL  ")+l+(f"  [{d}]" if d else ""))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",args=["--no-sandbox"])
        pg=await (await b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True,color_scheme='dark')).new_page()
        errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
        await pg.goto(HTML); await pg.wait_for_function("typeof RF!=='undefined'")
        await pg.evaluate("()=>{localStorage.clear();indexedDB.deleteDatabase('region-forge')}")
        await pg.reload(); await pg.wait_for_function("typeof RF!=='undefined'"); await pg.wait_for_timeout(800)
        st=await pg.evaluate("()=>({builtin:!!OW.builtin,chars:OW.chars,fw:OW.fw,fh:OW.fh,status:(document.getElementById('owstatus')||{}).textContent||''})")
        chk("a fresh start uses the built-in characters", st['builtin'] and st['chars']==19 and st['fh']==48, str(st)[:120])
        await pg.evaluate("()=>{document.getElementById('seed').value='city2'}")
        await pg.click("#go"); await pg.wait_for_selector("#starter:not(.hide)",timeout=30000)
        await pg.click("#startopts .card"); await pg.wait_for_selector("#out:not(.hide)")
        await pg.wait_for_timeout(1200)
        await pg.evaluate("async()=>{const W=ms=>new Promise(r=>setTimeout(r,ms));if(BT.on){endBattle(false);await W(1100)}}")
        looks=await pg.evaluate("""()=>{const N=RF.REGION().nodes;
          const r=N.find(n=>n.kind==='route'&&!n.sea);r._gen=null;RF.enterNode(r);
          const tr=F.gen.trainers.map(t=>({cls:t.cls,look:owCharFor(t.x,t.y),ok:(CLASS_LOOK[t.cls]||LOOK_GENERIC).includes(owCharFor(t.x,t.y))||t.evil}));
          return {tr,player:owFrame('d',0).sx<128}}""")
        chk("the player is the explorer", looks['player'])
        chk("each route trainer wears a look made for their class", all(t['ok'] and t['look'] not in (0,3,4) for t in looks['tr']), str([(t['cls'],t['look']) for t in looks['tr']]))
        await pg.evaluate("async()=>{const W=ms=>new Promise(r=>setTimeout(r,ms));if(BT.on){endBattle(false);await W(1100)}}")
        keys=await pg.evaluate("""()=>({youngster:trainerBattleKey({cls:'Youngster',name:'Joey'}),bird:trainerBattleKey({cls:'Bird Keeper',name:'Al'}),
          rival:trainerBattleKey({rival:true,name:'R',cls:'Rival'}),grunt:trainerBattleKey({evil:true,name:'A Team operative',cls:'Grunt'}),
          boss:trainerBattleKey({evil:true,boss:true,name:'X',cls:'Leader'}),admin:trainerBattleKey({evil:true,name:'Team Admin Vera',cls:'Grunt'}),
          karate:trainerBattleKey({cls:'Black Belt',name:'Ken'}),grass:trainerBattleKey(null,{leader:'Ivy',type:'Grass'}),
          water:trainerBattleKey(null,{leader:'Brook',type:'Water'}),league:trainerBattleKey({league:true,name:'Elite Kay'})})""")
        chk("a trainer's battle sprite matches their look, or else their class", (keys['youngster'] in (18,'spiky-3')) and (keys['bird'] in (17,'bushhat-4')), str(keys))
        chk("the Rival is Mia, grunts are grunts, admins and the leader use the admin design", keys['rival']==6 and keys['grunt'] in(2,4) and keys['boss']==1 and keys['admin']==1, str(keys))
        chk("a Grass-type gym leader is Rosario; other leaders and the League get leader sprites", keys['grass']==8 and keys['water'] in (5,13,10,11,16,17,15) and keys['league'] in (5,13,10,11,16,17,15))
        chk("a Black Belt is the karate fighter in his fighting stance", keys['karate']=='karate-5', str(keys['karate']))
        poses=await pg.evaluate("""()=>({hiker:poseKey(CH.bushhat,'Hiker'),backpacker:poseKey(CH.bushhat,'Backpacker'),
          lassF:poseKey(CH.feather,'Lass'),lassS:poseKey(CH.sunhat,'Lass'),ruin:poseKey(CH.scientist,'Ruin Maniac'),
          other:poseKey(CH.spiky,'Sailor'),plain:poseKey(CH.kid,'Youngster')})""")
        chk("each class gets its own pose; other classes get the character's default", poses['hiker']=='bushhat-3' and poses['backpacker']=='bushhat-5'
            and poses['lassF']=='feather-3' and poses['lassS']=='sunhat-8' and poses['ruin']=='scientist-5' and poses['other']=='spiky-6' and poses['plain'] is None, str(poses))
        # a real trainer battle: the opening shows both trainers, then they step aside
        ob=await pg.evaluate("""async()=>{const W=ms=>new Promise(r=>setTimeout(r,ms));
          const r=RF.REGION().nodes.find(n=>n.kind==='route'&&!n.sea);r._gen=null;RF.enterNode(r);await W(200);if(BT.on){endBattle(false);await W(1100)}
          const t=F.gen.trainers[0];startTrainer(t);await W(700);
          const im=[...document.querySelectorAll('#bfield .trsp')].map(e=>({cls:e.className,src:e.src.length>100,vis:getComputedStyle(e).opacity}));
          return {cls:t.cls,im}}""")
        await pg.wait_for_timeout(100)
        await pg.evaluate("()=>document.getElementById('bfield').scrollIntoView({block:'center'})")
        await pg.locator('#bfield').screenshot(path='/mnt/user-data/outputs/battle-opening.png')
        chk("a trainer battle opens with the trainer and you on screen", any('foe' in i['cls'] for i in ob['im']) and any('me' in i['cls'] for i in ob['im']), str(ob)[:140])
        await pg.wait_for_timeout(2000)
        gone=await pg.evaluate("()=>document.querySelectorAll('#bfield .trsp').length")
        chk("then they step aside for the battle", gone==0, str(gone))
        await pg.evaluate("async()=>{const W=ms=>new Promise(r=>setTimeout(r,ms));if(BT.on){endBattle(false);await W(1100)}}")
        # the rival, and a gym battle
        rv=await pg.evaluate("""async()=>{const W=ms=>new Promise(r=>setTimeout(r,ms));
          openBattle(RF.G().party[0],true,null,{name:'Rival',rival:true,queue:[],cls:'Rival',x:-1,y:-1});await W(700);
          const s=[...document.querySelectorAll('#bfield .trsp.foe')].map(e=>e.src===SPRITE_LIB.battle[6]);
          endBattle(false);await W(1100);return s}""")
        chk("the Rival's battle shows Mia", rv and rv[0], str(rv))
        # your own sheet takes over; the button brings the built-in characters back
        await pg.evaluate("()=>document.getElementById('tabChar').click()")
        await pg.set_input_files('#owfile','/mnt/user-data/outputs/explorer-ow-matched.png'); await pg.wait_for_timeout(700)
        own=await pg.evaluate("()=>({builtin:!!OW.builtin,name:OW.name})")
        chk("loading your own sheet replaces the built-in characters", not own['builtin'], str(own))
        await pg.evaluate("()=>document.getElementById('resetow').click()"); await pg.wait_for_timeout(700)
        back=await pg.evaluate("()=>({builtin:!!OW.builtin,chars:OW.chars,btn:document.getElementById('resetow').textContent})")
        chk("'Built-in characters' brings them back", back['builtin'] and back['chars']==19, str(back))
        # a city full of people, for the picture
        await pg.evaluate("""async()=>{const W=ms=>new Promise(r=>setTimeout(r,ms));
          const n=RF.REGION().nodes.find(x=>x.kind==='town'&&genTown(mulberry32(sfrom(SEED+'#'+x.id)),x).tier==='city');
          n._gen=null;RF.enterNode(n);await W(300);if(BT.on){endBattle(false);await W(1100)}
          const m=F.gen.map;let best=null,bc=-1;
          for(let y=4;y<m.h-4;y++)for(let x=4;x<m.w-4;x++){if(m.solid(x,y)||m.get(x,y)!==TER.PATH)continue;
            const c=(F.gen.folk||[]).filter(f=>Math.abs(f.x-x)<=5&&Math.abs(f.y-y)<=4).length;if(c>bc){bc=c;best=[x,y]}}
          F.tx=best[0];F.ty=best[1];F.px=F.tx;F.py=F.ty;F.face='d';draw();
          document.querySelectorAll('.toast').forEach(t=>t.remove());document.getElementById('field').scrollIntoView({block:'center'})}""")
        await pg.wait_for_timeout(300)
        await pg.locator('#field').screenshot(path='/mnt/user-data/outputs/city-with-characters.png')
        chk("no page errors", not errs, "; ".join(errs[:2]))
        await b.close()
    print("\n"+"="*46);print(f"{sum(R)}/{len(R)} passed")
asyncio.run(main())
