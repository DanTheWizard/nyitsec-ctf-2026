#!/usr/bin/env node
// Deterministic, self-contained PCAP authoring program for NYITSec.
// Writes an offline synthetic capture without opening network sockets.
// All users, passwords, hosts, and addresses are fictional lab examples.
import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, fileURLToPath } from "node:url";

function buildPcap() {
  const toBytes=s=>Array.from(s, c=>c.charCodeAt(0));
  const u16=n=>[(n>>>8)&255,n&255];
  const u32=n=>[(n>>>24)&255,(n>>>16)&255,(n>>>8)&255,n&255];
  const le32=n=>[n&255,(n>>>8)&255,(n>>>16)&255,(n>>>24)&255];
  const ip=s=>s.split(".").map(Number);
  const checksum=data=>{
    let n=0;
    for(let i=0;i<data.length;i+=2)n+=((data[i]<<8)|(data[i+1]||0));
    while(n>65535)n=(n&65535)+(n>>>16);
    return (~n)&65535;
  };
  let ipid=100, tick=0;
  const frames=[], start=1794410000;
  const frame=(src,dst,sport,dport,seq,ack,flags,payload)=>{
    const a=ip(src),b=ip(dst), n=payload.length;
    const tcp=[...u16(sport),...u16(dport),...u32(seq),...u32(ack),
      ...u16((5<<12)|flags),...u16(65535),0,0,0,0];
    const tcplen=tcp.length+n;
    const sum=checksum([...a,...b,0,6,...u16(tcplen),...tcp,...payload]);
    tcp[16]=(sum>>>8)&255;tcp[17]=sum&255;
    const total=20+tcplen;
    const ipv4=[0x45,0,...u16(total),...u16(ipid++),0x40,0,64,6,0,0,...a,...b];
    const csum=checksum(ipv4);
    ipv4[10]=(csum>>>8)&255;ipv4[11]=csum&255;
    const clientMac=[2,0,0,0,0,16],serverMac=[2,0,0,0,0,32];
    const ethernet=src.startsWith("10.")?
      [...serverMac,...clientMac,8,0]:
      [...clientMac,...serverMac,8,0];
    const ethernetFrame=[...ethernet,...ipv4,...tcp,...payload];
    const us=tick++*13000;
    frames.push([start+Math.floor(us/1000000),us%1000000,ethernetFrame]);
  };
  const exchange=(i,method,path,body,ref,response,client=17,server="198.51.100.44")=>{
    const src="10.77.40."+client,dst=server,cp=42000+i,sp=80;
    let a=100000+i*1237,b=900000+i*1973;
    const send=(forward,flags,data=[])=>{
      if(forward){frame(src,dst,cp,sp,a,b,flags,data);a+=data.length+((flags&3)?1:0);}
      else{frame(dst,src,sp,cp,b,a,flags,data);b+=data.length+((flags&3)?1:0);}
    };
    send(true,2);send(false,18);send(true,16);
    const hdr=[`${method} ${path} HTTP/1.1`,"Host: "+(path.includes("/tickets/")?"helptrack.test":"relaydesk.test"),
      "User-Agent: FictionalTrainingBrowser/1.0","Connection: close"];
    if(ref)hdr.push("X-Lab-Trace: "+ref);
    if(body!==null)hdr.push("Content-Type: application/x-www-form-urlencoded",
      "Content-Length: "+body.length);
    const head=toBytes(hdr.join("\r\n")+"\r\n\r\n");
    const data=toBytes(body||"");
    const parts=ref==="LAB-7B"?
      [[...head,...data.slice(0,22)],data.slice(22,30),data.slice(30,39),data.slice(39)]:
      (body!==null && i%2 ? [[...head,...data.slice(0,16)],data.slice(16)] : [[...head,...data]]);
    for(const chunk of parts){if(chunk.length){send(true,24,chunk);send(false,16);}}
    const resBytes=toBytes(response||"<html><body>Fictional page.</body></html>");
    const responseHead=toBytes("HTTP/1.1 200 OK\r\nServer: FictionalRelay/1\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: "+resBytes.length+"\r\nConnection: close\r\n\r\n");
    const reply=[...responseHead,...resBytes];
    for(let k=0;k<reply.length;k+=700){send(false,24,reply.slice(k,k+700));send(true,16);}
    send(true,17);send(false,16);send(false,17);send(true,16);
  };
  const form=(user,pass,extra="")=>"username="+encodeURIComponent(user)+"&pass="+encodeURIComponent(pass)+(extra?"&"+extra:"");
  const rows=[
    ["GET","/",null,null,"<h1>RelayDesk portal</h1>",17],
    ["GET","/login",null,null,"<form method='post' action='/api/login'>Demo</form>",17],
    ["POST","/api/login",form("demo_alice","Moss#Train42"),"LAB-2A",'{"account":"demo_alice"}',17],
    ["GET","/forum?topic=networking",null,null,"<p>Fictional antenna notes.</p>",17],
    ["POST","/api/login",form("demo_jonas","Autumn&Test81"),"LAB-5C",'{"account":"demo_jonas"}',18],
    ["GET","/docs/faq",null,null,"<h1>Helpdesk FAQ</h1>",24],
    ["GET","/tickets/CASE-105",null,null,"<p>Unrelated case.</p>",16],
    ["POST","/api/login",form("demo_riley","Mint#Demo56"),"LAB-9D",'{"account":"demo_riley"}',19],
    ["GET","/tickets/CASE-417",null,null,"<h1>CASE-417</h1><p>Fictional incident: correlate X-Lab-Trace: LAB-7B with the portal login request. Inspect the entire form stream.</p>",16],
    ["GET","/static/app.css",null,null,"body{background:#111b31}",17],
    ["POST","/api/login",form("bob","Lumen&Branch#47","remember=on"),"LAB-7B",'{"account":"bob","status":"ok"}',17],
    ["POST","/api/login",form("demo_morgan","Cloud#Sample93"),"LAB-6E",'{"account":"demo_morgan"}',22],
    ["POST","/api/settings","theme=night&lang=en","LAB-8F",'{"status":"updated"}',17],
    ["GET","/forum?topic=soldering",null,null,"<p>Fictional soldering discussion.</p>",26],
    ["POST","/api/login",form("demo_kira","Prism&Test99"),"LAB-1G",'{"account":"demo_kira"}',20],
    ["GET","/status",null,null,"<p>Training service healthy.</p>",24],
    ["POST","/api/login",form("demo_nina","Cobalt#Draft61"),"LAB-4K",'{"account":"demo_nina"}',29],
    ["GET","/logout",null,null,"<p>Signed out.</p>",17],
    ["GET","/static/logo.svg",null,null,"<svg><text>RelayDesk</text></svg>",17],
    ["GET","/forum?topic=ctf",null,null,"<p>Test event discussion.</p>",17],
  ];
  for(let i=0;i<rows.length;i++){
    const r=rows[i];
    exchange(i+1,...r,(r[1].startsWith("/tickets/")?"198.51.100.55":"198.51.100.44"));
  }
  const all=[0xd4,0xc3,0xb2,0xa1,2,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,0,0,1,0,0,0];
  // PCAP header is exactly 24 bytes: magic, version, timezone, accuracy, snaplen, linktype.
  const header=[0xd4,0xc3,0xb2,0xa1,2,0,4,0,...le32(0),...le32(0),...le32(65535),...le32(1)];
  const out=[...header];
  for(const [sec,micros,raw] of frames){
    out.push(...le32(sec),...le32(micros),...le32(raw.length),...le32(raw.length),...raw);
  }
  return Uint8Array.from(out);
}

const outfile = new URL("../level-3/packet-detective/traffic.pcap", import.meta.url);
mkdirSync(dirname(fileURLToPath(outfile)), { recursive: true });
const bytes = buildPcap();
writeFileSync(outfile, bytes);
console.log("Built fictional HTTP capture:", bytes.length, "bytes");
