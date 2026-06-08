/**
 * ETERNAL WARRIORS — city.js v6.0
 * Reescritura limpia. Sin parches. Canvas siempre inicializado antes de render.
 */
'use strict';

import { openBuildingMenu } from '/static/js/screens/building_menu.js';

const TW = 60, TH = 30;
const BH = { 1:8, 2:12, 3:16, 4:20, 5:26 };

// Art functions declaradas primero, DEFS después
function _artCC(nw,ne,se,sw,bh){
  block(nw,ne,se,sw,bh,'#243560','#131d3a','#0d1528','#3a5090');
  batt(nw.x,nw.y-bh,ne.x,ne.y-bh,6,5,5,lt('#243560',18));
  batt(nw.x,nw.y-bh,sw.x,sw.y-bh,6,5,5,lt('#243560',12));
  ogive((sw.x+se.x)/2-8,(sw.y+se.y)/2-bh*.55,5,8,'#1a3060');
  ogive((sw.x+se.x)/2+8,(sw.y+se.y)/2-bh*.55,5,8,'#1a3060');
  ogive((se.x+ne.x)/2,(se.y+ne.y)/2-bh*.55,5,8,'#0e1840');
  const cx=(nw.x+ne.x+se.x+sw.x)/4, cy=(nw.y+ne.y+se.y+sw.y)/4-bh-2;
  spire(cx,cy,20,6,'#1a2a58');
  ctx.beginPath();ctx.arc(cx,cy-20,3,0,Math.PI*2);ctx.fillStyle='#7aa8f0';ctx.fill();
  ctx.beginPath();ctx.arc(cx,cy-20,5,0,Math.PI*2);ctx.strokeStyle='rgba(90,150,240,0.3)';ctx.lineWidth=2;ctx.stroke();
  ctx.fillStyle='#b02828';ctx.fillRect(cx+6,cy-20,1.5,9);
  ctx.beginPath();ctx.moveTo(cx+7.5,cy-20);ctx.lineTo(cx+14,cy-16);ctx.lineTo(cx+7.5,cy-12);ctx.closePath();ctx.fillStyle='#d03030';ctx.fill();
}
function _artSanct(nw,ne,se,sw,bh){
  block(nw,ne,se,sw,bh,'#2e1050','#180830','#100620','#6030a0');
  const cx=(nw.x+ne.x+se.x+sw.x)/4, cy=(nw.y+ne.y+se.y+sw.y)/4-bh;
  ctx.beginPath();ctx.arc(cx,cy,8,0,Math.PI*2);ctx.fillStyle='#401070';ctx.fill();ctx.strokeStyle='#8040c0';ctx.lineWidth=1.2;ctx.stroke();
  for(let r=1;r<=2;r++){ctx.beginPath();ctx.arc(cx,cy,8+r*6,0,Math.PI*2);ctx.strokeStyle=`rgba(120,50,200,${0.13-r*0.04})`;ctx.lineWidth=2;ctx.stroke();}
  spire(nw.x+(ne.x-nw.x)*.25,nw.y+(ne.y-nw.y)*.25-bh,14,3,'#250a40');
  spire(nw.x+(sw.x-nw.x)*.25,nw.y+(sw.y-nw.y)*.25-bh,14,3,'#250a40');
  batt(nw.x,nw.y-bh,ne.x,ne.y-bh,4,4,4,lt('#2e1050',14));
  batt(nw.x,nw.y-bh,sw.x,sw.y-bh,4,4,4,lt('#2e1050',10));
}
function _artTemple(nw,ne,se,sw,bh){
  block(nw,ne,se,sw,bh,'#102850','#081630','#060e22','#284880');
  const cx=(nw.x+ne.x+se.x+sw.x)/4, cy=(nw.y+ne.y+se.y+sw.y)/4-bh;
  spire(cx,cy,16,3,'#183060');
  ctx.beginPath();ctx.arc(cx,cy-16,2,0,Math.PI*2);ctx.fillStyle='#50a0ff';ctx.fill();
  batt(nw.x,nw.y-bh,ne.x,ne.y-bh,3,4,3,'#183060');
  batt(nw.x,nw.y-bh,sw.x,sw.y-bh,3,4,3,'#102448');
}
function _artBarracks(nw,ne,se,sw,bh){
  block(nw,ne,se,sw,bh,'#401006','#240802','#1a0602','#802010');
  batt(nw.x,nw.y-bh,ne.x,ne.y-bh,5,5,4,'#501408');
  batt(nw.x,nw.y-bh,sw.x,sw.y-bh,3,5,4,'#401008');
  batt(ne.x,ne.y-bh,se.x,se.y-bh,3,5,4,'#381006');
  const lmx=(sw.x+se.x)/2, ly=Math.min(sw.y,se.y)-bh;
  for(let i=-1;i<=1;i++){
    ctx.beginPath();ctx.moveTo(lmx+i*8,ly);ctx.lineTo(lmx+i*8,ly-12);ctx.strokeStyle='#a06030';ctx.lineWidth=1;ctx.stroke();
    ctx.beginPath();ctx.moveTo(lmx+i*8,ly-12);ctx.lineTo(lmx+i*8-2,ly-7);ctx.lineTo(lmx+i*8+2,ly-7);ctx.closePath();ctx.fillStyle='#c08040';ctx.fill();
  }
}
function _artUniv(nw,ne,se,sw,bh){
  block(nw,ne,se,sw,bh,'#103010','#081808','#060e06','#206020');
  const cx=(nw.x+ne.x+se.x+sw.x)/4, cy=(nw.y+ne.y+se.y+sw.y)/4-bh;
  spire(cx,cy,14,3,'#184018');
  ctx.strokeStyle='#40a040';ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(cx-4,cy-14);ctx.lineTo(cx+4,cy-14);ctx.stroke();
  ctx.beginPath();ctx.moveTo(cx,cy-18);ctx.lineTo(cx,cy-10);ctx.stroke();
  batt(nw.x,nw.y-bh,ne.x,ne.y-bh,4,4,4,'#184018');
  batt(nw.x,nw.y-bh,sw.x,sw.y-bh,3,4,4,'#143014');
}
function _artForge(nw,ne,se,sw,bh){
  block(nw,ne,se,sw,bh,'#301808','#180c04','#100802','#604010');
  const cx=(nw.x+ne.x+se.x+sw.x)/4, cy=(nw.y+ne.y+se.y+sw.y)/4-bh-3;
  ctx.fillStyle='#201008';ctx.fillRect(cx-2.5,cy,5,8);
  ctx.strokeStyle='#403010';ctx.lineWidth=0.5;ctx.strokeRect(cx-2.5,cy,5,8);
  for(let i=0;i<3;i++){ctx.beginPath();ctx.arc(cx+(i%2?1.5:-1.5),cy-i*3,1,0,Math.PI*2);ctx.fillStyle=`rgba(255,${80+i*40},0,${0.5-i*0.1})`;ctx.fill();}
}
function _artWareh(nw,ne,se,sw,bh){
  block(nw,ne,se,sw,bh,'#282418','#14120c','#0e0e08','#484030');
  const mx=(nw.x+sw.x)/2, my=(nw.y+sw.y)/2-bh-5;
  const mx2=(ne.x+se.x)/2, my2=(ne.y+se.y)/2-bh-5;
  shape([{x:nw.x,y:nw.y-bh},{x:mx,y:my},{x:sw.x,y:sw.y-bh}]);ctx.fillStyle=lt('#282418',10);ctx.fill();ctx.strokeStyle='#484030';ctx.lineWidth=0.5;ctx.stroke();
  shape([{x:ne.x,y:ne.y-bh},{x:mx2,y:my2},{x:se.x,y:se.y-bh}]);ctx.fillStyle=lt('#282418',6);ctx.fill();ctx.stroke();
  ctx.beginPath();ctx.moveTo(mx,my);ctx.lineTo(mx2,my2);ctx.strokeStyle='#484030';ctx.lineWidth=0.8;ctx.stroke();
}
function _artHouse(nw,ne,se,sw,bh){
  block(nw,ne,se,sw,bh,'#2e2020','#181010','#100c0c','#604040');
  const cx=(nw.x+ne.x)/2, cy=(nw.y+ne.y)/2-bh-4;
  const cx2=(sw.x+se.x)/2, cy2=(sw.y+se.y)/2-bh-4;
  shape([{x:nw.x,y:nw.y-bh},{x:cx,y:cy},{x:sw.x,y:sw.y-bh}]);ctx.fillStyle='#4a2828';ctx.fill();ctx.strokeStyle='#704848';ctx.lineWidth=0.5;ctx.stroke();
  shape([{x:ne.x,y:ne.y-bh},{x:cx2,y:cy2},{x:se.x,y:se.y-bh}]);ctx.fillStyle='#3a1e1e';ctx.fill();ctx.stroke();
  ogive((sw.x+se.x)/2,(sw.y+se.y)/2-bh*.55,4,6,'#2a1808');
}
function _artTravel(nw,ne,se,sw,bh){
  block(nw,ne,se,sw,bh,'#102030','#080e18','#060a12','#204060');
  const cx=(nw.x+ne.x+se.x+sw.x)/4, cy=(nw.y+ne.y+se.y+sw.y)/4-bh;
  ctx.beginPath();ctx.arc(cx,cy,6,0,Math.PI*2);ctx.strokeStyle='#3080a0';ctx.lineWidth=1.5;ctx.stroke();
  ctx.beginPath();ctx.arc(cx,cy,3,0,Math.PI*2);ctx.fillStyle='#0c1828';ctx.fill();
}
function _artHide(nw,ne,se,sw,bh){
  block(nw,ne,se,sw,bh,'#141220','#0a0810','#07060c','#2e2c48');
  const cx=(nw.x+ne.x+se.x+sw.x)/4, cy=(nw.y+ne.y+se.y+sw.y)/4-bh-1;
  ctx.beginPath();ctx.arc(cx,cy,2,0,Math.PI*2);ctx.fillStyle='rgba(70,70,140,0.45)';ctx.fill();
}
function _artTower(nw,ne,se,sw,bh){
  block(nw,ne,se,sw,bh,'#282020','#141010','#0e0c0c','#504040');
  const cx=(nw.x+ne.x+se.x+sw.x)/4, cy=(nw.y+ne.y+se.y+sw.y)/4-bh;
  spire(cx,cy,22,3,'#181010');
  ctx.beginPath();ctx.arc(cx,cy-22,2.5,0,Math.PI*2);ctx.fillStyle='#d0b050';ctx.fill();
  ctx.beginPath();ctx.arc(cx,cy-22,5,0,Math.PI*2);ctx.strokeStyle='rgba(200,170,60,0.2)';ctx.lineWidth=2.5;ctx.stroke();
  batt(nw.x,nw.y-bh,ne.x,ne.y-bh,3,5,4,'#302828');
  batt(nw.x,nw.y-bh,sw.x,sw.y-bh,3,5,4,'#282020');
}

const DEFS = [
  // Centro
  {key:'CENTRO_DE_CIUDAD',    label:'C.Ciudad',    col:4,row:4,w:2,h:2,rank:5,art:_artCC      },
  // Noroeste: Santuario
  {key:'SANTUARIO_ARCANO',    label:'Santuario',   col:2,row:2,w:2,h:2,rank:4,art:_artSanct   },
  // Oeste: 3 Templos juntos verticalmente
  {key:'TEMPLO_1',            label:'Templo 1',    col:2,row:5,w:1,h:1,rank:3,art:_artTemple  },
  {key:'TEMPLO_2',            label:'Templo 2',    col:2,row:6,w:1,h:1,rank:3,art:_artTemple  },
  {key:'TEMPLO_3',            label:'Templo 3',    col:2,row:7,w:1,h:1,rank:3,art:_artTemple  },
  // Este: 2 Cuarteles juntos
  {key:'CUARTEL_1',           label:'Cuartel 1',   col:6,row:3,w:2,h:1,rank:3,art:_artBarracks},
  {key:'CUARTEL_2',           label:'Cuartel 2',   col:6,row:4,w:2,h:1,rank:2,art:_artBarracks},
  // Interior
  {key:'UNIVERSIDAD',         label:'Universidad', col:4,row:7,w:2,h:1,rank:3,art:_artUniv    },
  {key:'CASA',                label:'Casa',        col:3,row:7,w:1,h:1,rank:2,art:_artHouse   },
  {key:'HERRERIA',            label:'Herrería',    col:7,row:6,w:1,h:1,rank:2,art:_artForge   },
  {key:'ALMACEN',             label:'Almacén',     col:6,row:2,w:2,h:1,rank:2,art:_artWareh   },
  {key:'CENTRO_DE_VIAJES',    label:'C.Viajes',    col:7,row:7,w:1,h:1,rank:2,art:_artTravel  },
  {key:'ESCONDITE',           label:'Escondite',   col:7,row:5,w:1,h:1,rank:1,art:_artHide    },
  // Muralla — seleccionable, se dibuja como perímetro
  {key:'MURALLA',             label:'Muralla',     col:1,row:1,w:8,h:8,rank:2,art:null         },
  // Torre de Vigilancia — seleccionable, se dibuja en las 4 esquinas
  {key:'TORRE_DE_VIGILANCIA', label:'Torre Vig.',  col:1,row:1,w:1,h:1,rank:4,art:null         },
];

// Estado
let canvas, ctx, cW, cH, oX, oY;
let cityData=null, tasas=null, jugador='', ciudad='';
let hits=[], hoverK=null, selK=null, stars=[];
let ticker=null, sync=null;

// Geometría
function iso(c,r){return{x:oX+(c-r)*TW/2, y:oY+(c+r)*TH/2};}
function quad(c,r,w,h){return{nw:iso(c,r),ne:iso(c+w,r),se:iso(c+w,r+h),sw:iso(c,r+h)};}
function shape(pts){ctx.beginPath();pts.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();}
function lt(hex,n){return `rgb(${[1,3,5].map(i=>Math.min(255,parseInt(hex.slice(i,i+2),16)+n)).join(',')})`;}

function block(nw,ne,se,sw,bh,top,left,right,edge){
  shape([{x:sw.x,y:sw.y-bh},{x:se.x,y:se.y-bh},{x:se.x,y:se.y},{x:sw.x,y:sw.y}]);
  ctx.fillStyle=left;ctx.fill();ctx.strokeStyle='rgba(0,0,0,0.6)';ctx.lineWidth=0.5;ctx.stroke();
  shape([{x:se.x,y:se.y-bh},{x:ne.x,y:ne.y-bh},{x:ne.x,y:ne.y},{x:se.x,y:se.y}]);
  ctx.fillStyle=right;ctx.fill();ctx.stroke();
  shape([{x:nw.x,y:nw.y-bh},{x:ne.x,y:ne.y-bh},{x:se.x,y:se.y-bh},{x:sw.x,y:sw.y-bh}]);
  ctx.fillStyle=top;ctx.fill();ctx.strokeStyle=edge;ctx.lineWidth=0.8;ctx.stroke();
}
function spire(x,y,h,w,col){
  ctx.beginPath();ctx.moveTo(x,y-h);ctx.lineTo(x-w,y);ctx.lineTo(x+w,y);ctx.closePath();
  ctx.fillStyle=col;ctx.fill();ctx.strokeStyle=lt(col,40);ctx.lineWidth=0.5;ctx.stroke();
}
function batt(x1,y1,x2,y2,n,h,w,col){
  for(let i=0;i<n;i++){
    const t=(i+0.5)/n,mx=x1+t*(x2-x1),my=y1+t*(y2-y1);
    ctx.fillStyle=col;ctx.fillRect(mx-w/2,my-h,w,h);
    ctx.strokeStyle=lt(col,20);ctx.lineWidth=0.3;ctx.strokeRect(mx-w/2,my-h,w,h);
  }
}
function ogive(cx,cy,w,h,col){
  ctx.beginPath();ctx.rect(cx-w/2,cy,w,h*.5);ctx.arc(cx,cy,w/2,Math.PI,0);
  ctx.fillStyle=col;ctx.fill();ctx.strokeStyle=lt(col,60);ctx.lineWidth=0.4;ctx.stroke();
}

function _resize(){
  if(!canvas||!canvas.parentElement)return;
  cW=canvas.width=canvas.parentElement.clientWidth;
  cH=canvas.height=canvas.parentElement.clientHeight;
  oX=cW/2; oY=cH/2-5*TH+10;
}

function _stars(){
  stars=[];let s=137;
  const rng=()=>{s=(s*16807)%2147483647;return(s-1)/2147483646;};
  for(let i=0;i<150;i++)stars.push({rx:rng(),ry:rng()*.55,r:rng()*1+.2,a:rng()*.5+.2});
}

function _bg(){
  const g=ctx.createLinearGradient(0,0,0,cH*.7);
  g.addColorStop(0,'#010306');g.addColorStop(1,'#080c18');
  ctx.fillStyle=g;ctx.fillRect(0,0,cW,cH);
  stars.forEach(s=>{ctx.beginPath();ctx.arc(s.rx*cW,s.ry*cH,s.r,0,Math.PI*2);ctx.fillStyle=`rgba(255,255,240,${s.a})`;ctx.fill();});
  ctx.beginPath();ctx.arc(cW*.87,cH*.1,24,0,Math.PI*2);ctx.fillStyle='#e4dbb8';ctx.fill();
  ctx.beginPath();ctx.arc(cW*.87-7,cH*.1,24,0,Math.PI*2);ctx.fillStyle='#010306';ctx.fill();
}

function _ground(){
  for(let c=2;c<=8;c++)for(let r=2;r<=8;r++){
    const{nw,ne,se,sw}=quad(c,r,1,1);
    shape([nw,ne,se,sw]);
    ctx.fillStyle=(c+r)%2?'#0c0f1c':'#0f1222';ctx.fill();
    ctx.strokeStyle='rgba(255,255,255,0.018)';ctx.lineWidth=0.3;ctx.stroke();
  }
}

function _wseg(c,r){
  const{nw,ne,se,sw}=quad(c,r,1,1),H=18;
  shape([{x:sw.x,y:sw.y-H},{x:se.x,y:se.y-H},{x:se.x,y:se.y},{x:sw.x,y:sw.y}]);ctx.fillStyle='#181c2c';ctx.fill();ctx.strokeStyle='rgba(0,0,0,0.5)';ctx.lineWidth=0.4;ctx.stroke();
  shape([{x:se.x,y:se.y-H},{x:ne.x,y:ne.y-H},{x:ne.x,y:ne.y},{x:se.x,y:se.y}]);ctx.fillStyle='#121626';ctx.fill();ctx.stroke();
  shape([{x:nw.x,y:nw.y-H},{x:ne.x,y:ne.y-H},{x:se.x,y:se.y-H},{x:sw.x,y:sw.y-H}]);ctx.fillStyle='#22263a';ctx.fill();ctx.strokeStyle='#32364e';ctx.lineWidth=0.6;ctx.stroke();
  batt(nw.x,nw.y-H,ne.x,ne.y-H,3,4,4,'#2a2e42');
  batt(nw.x,nw.y-H,sw.x,sw.y-H,3,4,4,'#22263a');
}
function _wtower(c,r){
  const{nw,ne,se,sw}=quad(c,r,1,1),H=28;
  shape([{x:sw.x,y:sw.y-H},{x:se.x,y:se.y-H},{x:se.x,y:se.y},{x:sw.x,y:sw.y}]);ctx.fillStyle='#1a1e30';ctx.fill();ctx.strokeStyle='rgba(0,0,0,0.5)';ctx.lineWidth=0.4;ctx.stroke();
  shape([{x:se.x,y:se.y-H},{x:ne.x,y:ne.y-H},{x:ne.x,y:ne.y},{x:se.x,y:se.y}]);ctx.fillStyle='#141828';ctx.fill();ctx.stroke();
  shape([{x:nw.x,y:nw.y-H},{x:ne.x,y:ne.y-H},{x:se.x,y:se.y-H},{x:sw.x,y:sw.y-H}]);ctx.fillStyle='#282d44';ctx.fill();ctx.strokeStyle='#3e4460';ctx.lineWidth=0.8;ctx.stroke();
  batt(nw.x,nw.y-H,ne.x,ne.y-H,2,6,5,'#333856');
  batt(nw.x,nw.y-H,sw.x,sw.y-H,2,6,5,'#2c3050');
}
function _wall(){
  for(let c=2;c<=8;c++){_wseg(c,1);_wseg(c,9);}
  for(let r=2;r<=8;r++){_wseg(1,r);_wseg(9,r);}
  // Torres de esquina se dibujan desde DEFS (TORRE_DE_VIGILANCIA)
}

function _render(){
  if(!ctx||!cW||!cH)return;
  _bg();_ground();_wall();
  hits=[];
  if(!cityData)return;
  DEFS
    .map(d=>({d,nv:cityData[d.key]||0}))
    .sort((a,b)=>(a.d.col+a.d.row)-(b.d.col+b.d.row))
    .forEach(({d,nv})=>{
      const{nw,ne,se,sw}=quad(d.col,d.row,d.w,d.h);
      const isRuin=nv<=0;
      const bh=isRuin?3:BH[d.rank]+Math.min(Math.floor(nv/10),8);
      const isH=d.key===hoverK,isSel=d.key===selK;

      // Muralla — hit area en el perímetro, no se dibuja aquí (ya la dibuja _wall)
      if(d.key==='MURALLA'){
        if(isH||isSel){
          // Resaltar arista superior de todos los segmentos de muralla
          ctx.save();
          ctx.shadowColor=isSel?'#e8c96d':'#6ba3e0';
          ctx.shadowBlur=isSel?16:10;
          ctx.strokeStyle=isSel?'#e8c96d':'#6ba3e0';
          ctx.lineWidth=isSel?2:1.5;
          // Dibujar arista superior de cada segmento
          const segs=[
            ...Array.from({length:8},(_,i)=>({wc:i+1,wr:1})),
            ...Array.from({length:8},(_,i)=>({wc:i+1,wr:9})),
            ...Array.from({length:7},(_,i)=>({wc:1,wr:i+2})),
            ...Array.from({length:7},(_,i)=>({wc:9,wr:i+2})),
          ];
          segs.forEach(({wc,wr})=>{
            const wq=quad(wc,wr,1,1); const wh=18;
            ctx.beginPath();
            ctx.moveTo(wq.nw.x,wq.nw.y-wh);
            ctx.lineTo(wq.ne.x,wq.ne.y-wh);
            ctx.lineTo(wq.se.x,wq.se.y-wh);
            ctx.lineTo(wq.sw.x,wq.sw.y-wh);
            ctx.closePath();
            ctx.stroke();
          });
          ctx.restore();
        }
        // Hit area: líneas de muralla norte, sur, este, oeste
        // Push individual hit areas for each wall segment so hover works on all sides
        const wallSegs=[
          ...Array.from({length:8},(_,i)=>({c:i+1,r:1})),   // norte
          ...Array.from({length:8},(_,i)=>({c:i+1,r:9})),   // sur
          ...Array.from({length:7},(_,i)=>({c:1,r:i+2})),   // oeste
          ...Array.from({length:7},(_,i)=>({c:9,r:i+2})),   // este
        ];
        wallSegs.forEach(({c:wc,r:wr})=>{
          const wq=quad(wc,wr,1,1);
          const wh=18;
          hits.push({key:d.key,label:d.label,nivel:nv,pts:[
            {x:wq.nw.x,y:wq.nw.y-wh},{x:wq.ne.x,y:wq.ne.y-wh},
            {x:wq.se.x,y:wq.se.y-wh},{x:wq.sw.x,y:wq.sw.y-wh},
            {x:wq.se.x,y:wq.se.y},   {x:wq.sw.x,y:wq.sw.y}
          ]});
        });
        return;
      }

      // Torre de Vigilancia — 4 esquinas, hover y selección en todas
      if(d.key==='TORRE_DE_VIGILANCIA'){
        const corners=[[1,1],[9,1],[1,9],[9,9]];
        corners.forEach(([tc,tr])=>{
          const cc=quad(tc,tr,1,1);
          const tbh=28+Math.min(Math.floor(nv/5),10);
          if(isH||isSel){ctx.save();ctx.shadowColor=isSel?'#e8c96d':'#6ba3e0';ctx.shadowBlur=14;}
          _artTower(cc.nw,cc.ne,cc.se,cc.sw,tbh);
          if(isH||isSel)ctx.restore();
        });
        // Hit area en las 4 esquinas
        [[1,1],[9,1],[1,9],[9,9]].forEach(([tc,tr])=>{
          const hc=quad(tc,tr,1,1);
          const tbh2=28+Math.min(Math.floor(nv/5),10);
          hits.push({key:d.key,label:d.label,nivel:nv,pts:[
            {x:hc.nw.x,y:hc.nw.y-tbh2},{x:hc.ne.x,y:hc.ne.y-tbh2},
            {x:hc.se.x,y:hc.se.y-tbh2},{x:hc.sw.x,y:hc.sw.y-tbh2},
            {x:hc.se.x,y:hc.se.y},     {x:hc.sw.x,y:hc.sw.y}
          ]});
        });
        return;
      }

      if(isRuin){
        // En ruinas — bloque bajo, gris desaturado, semitransparente
        ctx.save();ctx.globalAlpha=0.35;
        block(nw,ne,se,sw,bh,'#1a1a1e','#101012','#0c0c0e','#252528');
        ctx.restore();
      } else {
        if(isH||isSel){ctx.save();ctx.shadowColor=isSel?'#e8c96d':'#6ba3e0';ctx.shadowBlur=12;}
        d.art(nw,ne,se,sw,bh);
        if(isH||isSel)ctx.restore();
        if(isSel){shape([{x:nw.x,y:nw.y-bh},{x:ne.x,y:ne.y-bh},{x:se.x,y:se.y-bh},{x:sw.x,y:sw.y-bh}]);ctx.strokeStyle='#e8c96d';ctx.lineWidth=1.5;ctx.stroke();}
      }
      // Barra de progreso si hay obra activa — se dibuja en segundo pase
      hits.push({key:d.key,label:d.label+(isRuin?' (en ruinas)':''),nivel:nv,pts:[
        {x:nw.x,y:nw.y-bh},{x:ne.x,y:ne.y-bh},{x:se.x,y:se.y-bh},{x:sw.x,y:sw.y-bh},{x:se.x,y:se.y},{x:sw.x,y:sw.y}
      ]});
    });

  // Segundo pase: barras de progreso encima de todo
  if(cityData.OBRAS && cityData.OBRAS.length){
    const now=Date.now()/1000;
    DEFS.forEach(d=>{
      if(d.key==='MURALLA'||d.key==='TORRE_DE_VIGILANCIA')return;
      const obra=cityData.OBRAS.find(o=>o.edificio===d.key&&o.inicio&&o.duracion_seg);
      if(!obra)return;
      const{nw,ne,se,sw}=quad(d.col,d.row,d.w,d.h);
      const nv=cityData[d.key]||0;
      const bh=nv<=0?3:BH[d.rank]+Math.min(Math.floor(nv/10),8);
      const pct=Math.min(1,(now-obra.inicio)/obra.duracion_seg);
      const barW=Math.abs(se.x-sw.x);
      const barX=Math.min(sw.x,se.x);
      const barY=Math.max(sw.y,se.y)+3;
      ctx.fillStyle='rgba(0,0,0,0.6)';
      ctx.fillRect(barX,barY,barW,5);
      ctx.fillStyle='#e8c96d';
      ctx.fillRect(barX,barY,barW*pct,5);
      ctx.font='8px monospace';ctx.textAlign='center';
      ctx.fillStyle='rgba(0,0,0,0.8)';
      ctx.fillText(`→${obra.nivel_dest}`,barX+barW/2+1,barY+15);
      ctx.fillStyle='#e8c96d';
      ctx.fillText(`→${obra.nivel_dest}`,barX+barW/2,barY+14);
    });
  }
}

function _pip(px,py,pts){
  let inside=false;
  for(let i=0,j=pts.length-1;i<pts.length;j=i++){
    const xi=pts[i].x,yi=pts[i].y,xj=pts[j].x,yj=pts[j].y;
    if(((yi>py)!==(yj>py))&&(px<(xj-xi)*(py-yi)/(yj-yi)+xi))inside=!inside;
  }
  return inside;
}
function _getHit(mx,my){for(let i=hits.length-1;i>=0;i--)if(_pip(mx,my,hits[i].pts))return hits[i];return null;}
function _xy(e){const r=canvas.getBoundingClientRect();return[e.clientX-r.left,e.clientY-r.top];}
function _onMove(e){
  const[mx,my]=_xy(e);
  const h=_getHit(mx,my),k=h?h.key:null;
  if(k!==hoverK){hoverK=k;canvas.style.cursor=k?'pointer':'default';_render();}
  const tt=document.getElementById('city-tooltip');
  if(tt){
    if(h){
      tt.textContent=`${h.label}  Nv.${h.nivel}`;
      tt.style.display='block';
      const wrap=document.getElementById('city-canvas-wrap');
      const wr=wrap.getBoundingClientRect();
      tt.style.left=(e.clientX-wr.left+14)+'px';
      tt.style.top=(e.clientY-wr.top-28)+'px';
    } else {
      tt.style.display='none';
    }
  }
}
function _onLeave(){
  hoverK=null;canvas.style.cursor='default';_render();
  const tt=document.getElementById('city-tooltip');
  if(tt)tt.style.display='none';
}
function _onClick(e){
  const h=_getHit(..._xy(e));
  if(h){selK=h.key===selK?null:h.key;_render();if(selK)openBuildingMenu(h.key,jugador,ciudad,cityData);}
  else{selK=null;_render();}
}

function _fmtSeg(seg) {
  if (!seg || seg <= 0) return '—';
  seg = Math.round(seg);
  const d = Math.floor(seg/86400), h = Math.floor((seg%86400)/3600);
  const m = Math.floor((seg%3600)/60), s = seg%60;
  if (d > 0) return d+'d '+h+'h '+m+'m';
  if (h > 0) return h+'h '+m+'m '+s+'s';
  if (m > 0) return m+'m '+s+'s';
  return s+'s';
}
function _fmt(n){
  if(n==null||n===undefined)return'—';
  n=Number(n); if(isNaN(n))return'—';
  if(!isFinite(n))return'∞';
  const a=Math.abs(n);
  if(a>=1e99)return(n/1e99).toFixed(1)+'Ct';
  if(a>=1e90)return(n/1e90).toFixed(1)+'Nn';
  if(a>=1e60)return(n/1e60).toFixed(1)+'Sx';
  if(a>=1e33)return(n/1e33).toFixed(1)+'Dc';
  if(a>=1e30)return(n/1e30).toFixed(1)+'No';
  if(a>=1e27)return(n/1e27).toFixed(1)+'Oc';
  if(a>=1e24)return(n/1e24).toFixed(1)+'Sp';
  if(a>=1e21)return(n/1e21).toFixed(1)+'Sx';
  if(a>=1e18)return(n/1e18).toFixed(1)+'Qn';
  if(a>=1e15)return(n/1e15).toFixed(1)+'Pd';
  if(a>=1e12)return(n/1e12).toFixed(1)+'T';
  if(a>=1e9) return(n/1e9).toFixed(1)+'B';
  if(a>=1e6) return(n/1e6).toFixed(1)+'M';
  if(a>=1e3) return(n/1e3).toFixed(1)+'K';
  return Math.floor(n).toLocaleString('es');
}

function _updateLeftWithOffset(offset){
  _updateLeft(offset||{});
}

function _updateLeft(offset){
  offset = offset||{};
  const el=document.getElementById('city-left');
  if(!el||!cityData)return;
  // Mostrar cityData + offset local (estimación visual, no modifica el estado real)
  const c={...cityData};
  Object.keys(offset).forEach(k=>{ c[k]=(c[k]||0)+offset[k]; });
  const t=tasas||{};

  const isInfMat = (c.ALMACEN||0) >= 50;
  const isInfMana = (c.SANTUARIO_ARCANO||0) >= 50;
  const RES=[
    ['🪵','Madera',  'MADERA', 'madera', isInfMat],
    ['🪨','Piedra',  'PIEDRA', 'piedra', isInfMat],
    ['⚙️','Hierro',  'HIERRO', 'hierro', isInfMat],
    ['🔥','Carbón',  'CARBON', 'carbon', isInfMat],
    ['🪙','Oro',     'ORO',    'oro',    isInfMat],
    ['✨','Maná',    'MANA',   'mana',   isInfMana],
  ];
  const resRows=RES.map(([ico,lbl,k,tk,isInf])=>`
    <div class="stat-row">
      <span class="stat-label">${ico} ${lbl}</span>
      <span class="stat-val">${isInf?'∞':_fmt(c[k])}</span>
      ${isInf?'<span class="stat-rate" style="color:#6ba3e0">∞</span>':(t[tk]?`<span class="stat-rate">+${_fmt(t[tk])}/s</span>`:'<span class="stat-rate"></span>')}
    </div>`).join('');

  const prodRows=`
    <div class="stat-row"><span class="stat-label">👥 Aldeanos</span><span class="stat-val">${_fmt(c.ALDEANO)}</span>${t.aldeanos_hora?`<span class="stat-rate">+${_fmt(t.aldeanos_hora)}/h</span>`:'<span class="stat-rate"></span>'}</div>
    <div class="stat-row"><span class="stat-label">✨ Maná</span><span class="stat-val">${isInfMana?'∞':_fmt(c.MANA)}</span>${isInfMana?'<span class="stat-rate" style="color:#6ba3e0">∞</span>':(t.mana?`<span class="stat-rate">+${_fmt(t.mana)}/s</span>`:'<span class="stat-rate"></span>')}</div>
    <div class="stat-row"><span class="stat-label">🪙 Oro</span><span class="stat-val">${isInfMat?'∞':_fmt(c.ORO)}</span>${isInfMat?'<span class="stat-rate" style="color:#6ba3e0">∞</span>':(t.oro?`<span class="stat-rate">+${_fmt(t.oro)}/s</span>`:'<span class="stat-rate"></span>')}</div>`;

  const logRows=[
    ['Almacén Nv.',   c.ALMACEN],
    ['Santuario Nv.', c.SANTUARIO_ARCANO],
    ['C.Ciudad Nv.',  c.CENTRO_DE_CIUDAD],
    ['Universidad Nv.',c.UNIVERSIDAD],
  ].map(([lbl,v])=>`<div class="stat-row"><span class="stat-label">${lbl}</span><span class="stat-val">${v||0}</span></div>`).join('');

  // ── Panel de Obras en curso ──────────────────────────────────────────────
  const _nowSecObras = Date.now() / 1000;
  const obrasData = (cityData.OBRAS || []).filter(o => {
    if (o.inicio && o.duracion_seg) return (_nowSecObras - o.inicio) < o.duracion_seg;
    if (o.TIEMPO != null) return o.TIEMPO > 0;
    return true;
  });
  const NOMBRES_EDIF = {
    CENTRO_DE_CIUDAD:'Centro de Ciudad', CASA:'Casa', MURALLA:'Muralla',
    TORRE_DE_VIGILANCIA:'Torre de Vigilancia', CENTRO_DE_VIAJES:'Centro de Viajes',
    ESCONDITE:'Escondite', ALMACEN:'Almacén', SANTUARIO_ARCANO:'Santuario Arcano',
    UNIVERSIDAD:'Universidad', HERRERIA:'Herrería',
    TEMPLO_1:'Templo 1', TEMPLO_2:'Templo 2', TEMPLO_3:'Templo 3',
    CUARTEL_1:'Cuartel 1', CUARTEL_2:'Cuartel 2',
  };
  const _nowSec = Date.now() / 1000;

  const obrasRows = obrasData.map(o => {
    // Soportar ambos formatos
    const key      = o.edificio || o.KEY || '?';
    const nombre   = NOMBRES_EDIF[key] || key.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
    const nivelDst = o.nivel_dest ?? '?';
    let pct = 0, restSeg = 0;

    if (o.inicio && o.duracion_seg) {
      // Formato nuevo
      const transcurrido = Math.max(0, _nowSec - o.inicio);
      pct    = Math.min(1, transcurrido / o.duracion_seg);
      restSeg = Math.max(0, o.duracion_seg - transcurrido);
    } else if (o.TIEMPO != null && o.TOTAL != null) {
      // Formato viejo
      pct    = Math.min(1, 1 - o.TIEMPO / o.TOTAL);
      restSeg = o.TIEMPO;
    }

    const pctPct = (pct * 100).toFixed(0);
    const fmtRest = _fmtSeg(restSeg);

    const _inicio = o.inicio || 0;
    const _dur = o.duracion_seg || 1;
    return `<div style="margin-bottom:8px;">
      <div style="display:flex;justify-content:space-between;font-size:10px;margin-bottom:2px;">
        <span style="color:#c9a84c;font-family:'Cinzel',serif;">${nombre}${nivelDst!=='?'?' → Nv.'+nivelDst:''}</span>
        <span data-obra-info style="color:#666;">${pctPct}% · ${fmtRest}</span>
      </div>
      <div style="background:#111;border-radius:2px;height:5px;">
        <div data-obra-inicio="${_inicio}" data-obra-dur="${_dur}"
          style="background:linear-gradient(90deg,#c9a84c,#e8d080);width:${pctPct}%;height:100%;border-radius:2px;"></div>
      </div>
    </div>`;
  }).join('');

  const obrasPanel = obrasData.length ? `
    <div class="panel" style="margin-top:6px">
      <div class="panel-title">▼ Construcciones (${obrasData.length})</div>
      ${obrasRows}
    </div>` : '';

  // Panel de progreso del jugador
  const xpVal = window._playerXP;
  const bat   = window._playerBatallas||{};
  const xpPanel = xpVal!==null&&xpVal!==undefined ? `
    <div class="panel" style="margin-top:6px">
      <div class="panel-title">▼ Progreso</div>
      <div class="stat-row"><span class="stat-label">⭐ Experiencia</span><span class="stat-val">${_fmt(xpVal)}</span></div>
      <div class="stat-row"><span class="stat-label">⚔ Batallas ganadas</span><span class="stat-val">${_fmt(bat.ganadas||0)}</span></div>
      <div class="stat-row"><span class="stat-label">💀 Batallas perdidas</span><span class="stat-val">${_fmt(bat.perdidas||0)}</span></div>
      <div class="stat-row"><span class="stat-label">🌩 Dioses abatidos</span><span class="stat-val">${_fmt(bat.dioses||0)}</span></div>
      <div class="stat-row"><span class="stat-label">🦎 Cuevas derrotadas</span><span class="stat-val">${_fmt(bat.cuevas||0)}</span></div>
      <div style="margin-top:8px;">
        <button onclick="window._abrirLeveling()" style="
          width:100%;padding:6px;background:rgba(201,168,76,0.12);
          border:1px solid #c9a84c88;color:#c9a84c;border-radius:4px;
          cursor:pointer;font-family:'Cinzel',serif;font-size:11px;">
          ⬆ Subir nivel de tropas
        </button>
      </div>
    </div>` : '';

  el.innerHTML=`
    <div class="panel">
      <div class="panel-title">▼ Recursos</div>${resRows}
    </div>
    <div class="panel" style="margin-top:6px">
      <div class="panel-title">▼ Producción / Hora</div>${prodRows}
    </div>
    <div class="panel" style="margin-top:6px">
      <div class="panel-title">▼ Logística</div>${logRows}
    </div>
    ${obrasPanel}
    ${xpPanel}`;
}

function _updateRight(){
  const el=document.getElementById('city-right');
  if(!el||!cityData)return;
  const cd=cityData;
  const ARMY=[['Aldeano','ALDEANO'],['Explorador','EXPLORADOR'],['Sacerdote','SACERDOTE'],
    ['Guerrero','GUERRERO'],['Comando','COMANDO'],['Mercenario','MERCENARIO'],
    ['Marine','MARINE'],['Cyborg','CYBORG'],['Mago','MAGO'],['Metahumano','METAHUMANO']];
  const INV=[['Demonio','DEMONIO'],['Ánima','ANIMA'],['Espectro','ESPECTRO'],
    ['Gólem','GOLEM'],['Centauro','CENTAURO'],['Kraken','KRAKEN'],
    ['Alonardo','ALONARDO'],['Madreselva','MADRESELVA'],['Coloso','COLOSO'],
    ['Fénix','FENIX'],['Dragón de Oro','DRAGON_DE_ORO'],['Cab. de Luz','CABALLERO_DE_LUZ'],
    ['AlalaiA','ALALAIA'],['Éon Supremo','EON_SUPREMO']];
  const ar=ARMY.map(([l,k])=>`<div class="stat-row"><span class="stat-label">${l}</span><span class="stat-val">${_fmt(cd[k]||0)}</span></div>`).join('');
  const ir=INV.map(([l,k])=>`<div class="stat-row"><span class="stat-label">${l}</span><span class="stat-val">${_fmt(cd[k]||0)}</span></div>`).join('');
  const CUEVAS_CITY=[['Behemot','BEHEMOT'],['Chupacabras','CHUPACABRAS'],['Dragón','DRAGON'],['Leviatán','LEVIATAN'],['Patotas','PATOTAS'],['Simurgh','SIMURGH']];
  const cr=CUEVAS_CITY.filter(([,k])=>(cd[k]||0)>0).map(([l,k])=>`<div class="stat-row"><span class="stat-label" style="color:#e07050">${l}</span><span class="stat-val">${_fmt(cd[k]||0)}</span></div>`).join('');
  const bh=window._bonusHerreria;
  const herrHTML=bh?`
    <div class="panel" style="margin-top:6px">
      <div class="panel-title">⚒ Herrería</div>
      <div class="stat-row"><span class="stat-label">⚔ PA Bonus</span><span class="stat-val">+${_fmt(bh.pa_bonus)}</span></div>
      <div class="stat-row"><span class="stat-label">🛡 CA Bonus</span><span class="stat-val">+${_fmt(bh.ca_bonus)}</span></div>
      <div class="stat-row"><span class="stat-label">❤ HP Bonus</span><span class="stat-val">+${_fmt(bh.hp_bonus)}</span></div>
      ${bh.detalle.filter(d=>d.nivel>0).map(d=>`
        <div class="stat-row"><span class="stat-label" style="font-size:9px">${d.ciudad}</span>
        <span class="stat-val" style="font-size:9px">Nv.${d.nivel} PA+${d.pa}</span></div>`).join('')}
    </div>`:'';
  el.innerHTML=`
    <div class="panel"><div class="panel-title">▼ Ejército</div>${ar}</div>
    <div class="panel" style="margin-top:6px"><div class="panel-title">▼ Invocaciones</div>${ir}</div>
    ${cr?`<div class="panel" style="margin-top:6px"><div class="panel-title" style="color:#e07050">▼ Criaturas de Cueva</div>${cr}</div>`:''}
    ${herrHTML}`;
}

function _updateBar(){
  if(!cityData)return;
  const c=cityData;
  const ARMY_KEYS=['ALDEANO','EXPLORADOR','SACERDOTE','GUERRERO','COMANDO','MERCENARIO','MARINE','CYBORG','MAGO','METAHUMANO'];
  const INV_KEYS=['DEMONIO','ANIMA','ESPECTRO','GOLEM','CENTAURO','KRAKEN','ALONARDO','MADRESELVA','COLOSO','FENIX','DRAGON_DE_ORO','CABALLERO_DE_LUZ','ALALAIA','EON_SUPREMO'];
  const totalArmy=ARMY_KEYS.reduce((s,k)=>s+(c[k]||0),0);
  const totalInv=INV_KEYS.reduce((s,k)=>s+(c[k]||0),0);
  const totalEdif=Object.keys(c).filter(k=>['CENTRO_DE_CIUDAD','CASA','MURALLA','TORRE_DE_VIGILANCIA','CENTRO_DE_VIAJES','ESCONDITE','ALMACEN','SANTUARIO_ARCANO','UNIVERSIDAD','HERRERIA','TEMPLO_1','CUARTEL_1','TEMPLO_2','CUARTEL_2','TEMPLO_3'].includes(k)&&c[k]>0).length;
  const sb=id=>document.getElementById('sb-'+id);
  if(sb('pob'))  sb('pob').textContent  = _fmt(c.ALDEANO||0);
  if(sb('ej'))   sb('ej').textContent   = _fmt(totalArmy);
  if(sb('inv'))  sb('inv').textContent  = _fmt(totalInv);
  if(sb('edif')) sb('edif').textContent = totalEdif;
  if(sb('mur'))  sb('mur').textContent  = 'Nv.'+( c.MURALLA||0);
}

function _startTick(){
  if(ticker)clearInterval(ticker);
  let _off={};
  const _token = jugador+'|'+ciudad;
  window._resetLocalOffset=()=>{_off={};};
  ticker=setInterval(()=>{
    // Parar si la ciudad cambió
    if(jugador+'|'+ciudad !== _token){ clearInterval(ticker); ticker=null; return; }
    if(!cityData||!tasas)return;
    ['MADERA','PIEDRA','HIERRO','CARBON','ORO','MANA'].forEach(k=>{
      const tk=k.toLowerCase();if(tasas[tk])_off[k]=(_off[k]||0)+tasas[tk];
    });
    if(tasas.aldeanos_hora)_off['ALDEANO']=(_off['ALDEANO']||0)+tasas.aldeanos_hora/3600;
    _updateLeft(_off);_updateBar();
    // Actualizar barras de obras cada segundo
    const _nowTick = Date.now()/1000;
    document.querySelectorAll('[data-obra-inicio]').forEach(bar => {
      const inicio = parseFloat(bar.dataset.obraInicio);
      const dur = parseFloat(bar.dataset.obraDur);
      const pct = Math.min(1, (_nowTick - inicio) / dur);
      bar.style.width = (pct*100).toFixed(1) + '%';
      const info = bar.parentElement?.parentElement?.querySelector('[data-obra-info]');
      if (info) {
        const rest = Math.max(0, dur - (_nowTick - inicio));
        info.textContent = (pct*100).toFixed(0) + '% · ' + _fmtSeg(rest);
      }
    });
  },1000);
}

// ── Modal de Leveling ────────────────────────────────────────────────────────
let _levelingModal = null;

window._abrirLeveling = async function() {
  if (_levelingModal) { _levelingModal.remove(); _levelingModal = null; }

  const resp = await fetch(`/api/leveling/${jugador}`);
  const data = await resp.json();
  if (!data.ok) return;

  const LABELS = {
    ALDEANO:'Aldeano', EXPLORADOR:'Explorador', SACERDOTE:'Sacerdote',
    GUERRERO:'Guerrero', COMANDO:'Comando', MERCENARIO:'Mercenario',
    MARINE:'Marine', CYBORG:'Cyborg', MAGO:'Mago', METAHUMANO:'Metahumano',
    DEMONIO:'Demonio', ANIMA:'Ánima', ESPECTRO:'Espectro', GOLEM:'Gólem',
    CENTAURO:'Centauro', KRAKEN:'Kraken', ALONARDO:'Alonardo',
    MADRESELVA:'Madreselva', COLOSO:'Coloso', FENIX:'Fénix',
    DRAGON_DE_ORO:'Dragón de Oro', CABALLERO_DE_LUZ:'Cab. de Luz',
    ALALAIA:'AlalaiA', EON_SUPREMO:'Éon Supremo',
  };

  const filas = data.tropas.map(t => {
    const lbl   = LABELS[t.tipo] || t.tipo;
    const costo = t.xp_costo != null ? _fmt(t.xp_costo) : '—';
    const btn   = t.puede_subir
      ? `<button onclick="window._subirNivel('${t.tipo}')"
           style="padding:2px 10px;background:rgba(201,168,76,0.15);
             border:1px solid #c9a84c99;color:#c9a84c;border-radius:3px;
             cursor:pointer;font-size:10px;font-family:'Cinzel',serif;">
           ⬆ Subir
         </button>`
      : `<span style="color:#444;font-size:10px;">${t.nivel >= t.nivel_max ? 'MAX' : 'Sin XP'}</span>`;
    return `<div style="display:grid;grid-template-columns:120px 50px 1fr auto;
        gap:6px;align-items:center;padding:4px 0;
        border-bottom:1px solid rgba(255,255,255,0.04);">
      <span style="font-size:11px;color:#b0a080;font-family:'Cinzel',serif;">${lbl}</span>
      <span style="font-size:11px;color:#e8e0d0;text-align:center;">Nv.${t.nivel}</span>
      <span style="font-size:10px;color:#666;">Costo: ${costo}</span>
      ${btn}
    </div>`;
  }).join('');

  const modal = document.createElement('div');
  modal.id = 'leveling-modal';
  modal.style.cssText = `position:fixed;top:0;left:0;width:100%;height:100%;
    background:rgba(0,0,0,0.75);z-index:1000;display:flex;
    align-items:center;justify-content:center;`;
  modal.innerHTML = `
    <div style="background:#0a0c14;border:1px solid #c9a84c44;border-radius:8px;
      padding:20px;width:500px;max-height:80vh;overflow-y:auto;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
        <span style="font-family:'Cinzel',serif;color:#c9a84c;font-size:14px;">⬆ Subir nivel de tropas</span>
        <button onclick="window._cerrarLeveling()"
          style="background:none;border:none;color:#666;cursor:pointer;font-size:18px;">✕</button>
      </div>
      <div style="color:#888;font-size:11px;font-family:'Cinzel',serif;margin-bottom:12px;">
        ⭐ XP disponible: <b style="color:#c9a84c;">${_fmt(data.xp_pool)}</b>
      </div>
      <div id="leveling-filas">${filas}</div>
    </div>`;
  document.body.appendChild(modal);
  _levelingModal = modal;
  modal.addEventListener('click', e => { if (e.target === modal) window._cerrarLeveling(); });
};

window._cerrarLeveling = function() {
  if (_levelingModal) { _levelingModal.remove(); _levelingModal = null; }
};

window._subirNivel = async function(tipo) {
  const resp = await fetch(`/api/leveling/${jugador}/subir`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({tipo}),
  });
  const data = await resp.json();
  if (!data.ok) {
    alert(data.msg);
    return;
  }
  // Actualizar XP local y reabrir modal
  if (window._playerXP !== null) window._playerXP = data.xp_restante;
  window._abrirLeveling();  // recargar modal con datos frescos
};

export function cleanup(){
  if(ticker){clearInterval(ticker);ticker=null;}
  if(sync){clearInterval(sync);sync=null;}
  if(canvas){
    canvas.removeEventListener('mousemove',_onMove);
    canvas.removeEventListener('click',_onClick);
    canvas.removeEventListener('mouseleave',_onLeave);
  }
  cityData=null; tasas=null; canvas=null; ctx=null;
}

export async function render(container, jug, ciu){
  jugador=jug; ciudad=ciu;
  // Limpiar estado anterior inmediatamente
  if(ticker){clearInterval(ticker);ticker=null;}
  if(sync){clearInterval(sync);sync=null;}
  if(window._resetLocalOffset) window._resetLocalOffset();
  // Limpiar canvas anterior si existe
  const oldCanvas = document.getElementById('city-canvas');
  if(oldCanvas){
    oldCanvas.removeEventListener('mousemove',_onMove);
    oldCanvas.removeEventListener('click',_onClick);
    oldCanvas.removeEventListener('mouseleave',_onLeave);
  }
  cityData=null; tasas=null;
  hoverK=null; selK=null; hits=[];
  canvas=null; ctx=null;

  container.innerHTML=`
    <div class="city-screen">
      <div class="city-left" id="city-left"></div>
      <div class="city-center">
        <div class="city-canvas-wrap" id="city-canvas-wrap">
          <canvas id="city-canvas" style="position:absolute;top:0;left:0;width:100%;height:100%;display:block;"></canvas>
          <div class="city-name-badge">${ciu.toUpperCase()}</div>
          <div id="city-tooltip" style="
            display:none;position:absolute;pointer-events:none;
            background:rgba(8,8,18,0.92);border:1px solid var(--color-gold);
            color:var(--color-gold);font-family:var(--font-ui);font-size:11px;
            letter-spacing:1px;padding:4px 10px;border-radius:3px;
            white-space:nowrap;z-index:10;
          "></div>
        </div>
        <div class="city-stats-bar">
          <div class="stat-bar-item"><span class="stat-bar-icon">👥</span><span class="stat-bar-label">POBLACIÓN</span><span class="stat-bar-val" id="sb-pob">—</span></div>
          <div class="stat-bar-item"><span class="stat-bar-icon">⚔️</span><span class="stat-bar-label">EJÉRCITOS</span><span class="stat-bar-val" id="sb-ej">—</span></div>
          <div class="stat-bar-item"><span class="stat-bar-icon">✨</span><span class="stat-bar-label">INVOC.</span><span class="stat-bar-val" id="sb-inv">—</span></div>
          <div class="stat-bar-item"><span class="stat-bar-icon">🏛️</span><span class="stat-bar-label">EDIFICIOS</span><span class="stat-bar-val" id="sb-edif">—</span></div>
          <div class="stat-bar-item"><span class="stat-bar-icon">🛡️</span><span class="stat-bar-label">MURALLA</span><span class="stat-bar-val" id="sb-mur">—</span></div>
        </div>
      </div>
      <div class="city-right" id="city-right"></div>
    </div>`;

  let data, tasasRaw;
  try{
    const [r1,r2]=await Promise.all([
      fetch(`/api/city/${jug}/${ciu}`),
      fetch(`/api/city/${jug}/${ciu}/tasas`)
    ]);
    if(!r1.ok)throw new Error(`HTTP ${r1.status}`);
    data=await r1.json();
    tasasRaw=r2.ok?await r2.json():null;
  }catch(e){
    container.innerHTML=`<div class="screen-loading"><span>Error: ${e.message}</span></div>`;return;
  }
  cityData=data.city||data;
  window._bonusHerreria=data.bonus_herreria||null;
  window._playerXP=data.experiencia??null;
  window._playerBatallas={ganadas:data.batallas_ganadas??0,perdidas:data.batallas_perdidas??0,dioses:data.dioses_abatidos??0,cuevas:data.cuevas_derrotadas??0};
  if(tasasRaw&&tasasRaw.tasas){
    const raw=tasasRaw.tasas;
    tasas={
      madera: (raw.MADERA||0)/3600,
      piedra: (raw.PIEDRA||0)/3600,
      hierro: (raw.HIERRO||0)/3600,
      carbon: (raw.CARBON||0)/3600,
      oro:    (raw.ORO||0)/3600,
      mana:   (raw.MANA||0)/3600,
      aldeanos_hora: raw.ALDEANOS_POR_HORA||0,
    };
  }
  window._cityData=cityData;

  canvas=document.getElementById('city-canvas');
  ctx=canvas.getContext('2d');
  _stars();

  // Esperar a que el layout esté listo antes de leer dimensiones
  requestAnimationFrame(()=>{
    requestAnimationFrame(()=>{
      _resize();
      _render();
      _updateLeft();
      _updateRight();
      _updateBar();
      _startTick();
      window.addEventListener('resize',()=>{_resize();_render();});
      canvas.addEventListener('mousemove',_onMove);
      canvas.addEventListener('click',_onClick);
      canvas.addEventListener('mouseleave',_onLeave);
    });
  });

  if(sync)clearInterval(sync);
  const _syncToken=jug+'|'+ciu;
  sync=setInterval(async()=>{
    if(jugador+'|'+ciudad!==_syncToken){clearInterval(sync);sync=null;return;}
    try{
      const [r1,r2]=await Promise.all([
        fetch(`/api/city/${jug}/${ciu}/tick`,{method:'POST'}),
        fetch(`/api/city/${jug}/${ciu}/tasas`)
      ]);
      if(!r1.ok)return;
      const d=await r1.json();
      cityData=d.city||d;
      if(d.experiencia!==undefined){window._playerXP=d.experiencia;window._playerBatallas={ganadas:d.batallas_ganadas??0,perdidas:d.batallas_perdidas??0,dioses:d.dioses_abatidos??0,cuevas:d.cuevas_derrotadas??0};}
      if(r2.ok){
        const td=await r2.json();
        if(td&&td.tasas){
          const raw=td.tasas;
          tasas={
            madera:raw.MADERA?raw.MADERA/3600:0,
            piedra:raw.PIEDRA?raw.PIEDRA/3600:0,
            hierro:raw.HIERRO?raw.HIERRO/3600:0,
            carbon:raw.CARBON?raw.CARBON/3600:0,
            oro:raw.ORO?raw.ORO/3600:0,
            mana:raw.MANA?raw.MANA/3600:0,
            aldeanos_hora:raw.ALDEANOS_POR_HORA||0,
          };
        }
      }
      _render();
      if(window._resetLocalOffset) window._resetLocalOffset();
      _updateLeft();_updateRight();_updateBar();
    }catch(_){}
  },10000);
}
