// I developed this file with Codex assistance; see PROCESS_LOG.md.
"use strict";
let key = "", history = [], busy = false;
const $ = id => document.getElementById(id);
function notice(text) { $("notice").textContent = text; }
function bubble(role, text, error=false) {
  const welcome = document.querySelector(".welcome"); if (welcome) welcome.remove();
  const item = document.createElement("div"); item.className = "bubble " + role + (error ? " error" : "");
  item.textContent = text; $("messages").append(item); item.scrollIntoView({block:"nearest"});
}
function clear() { history=[]; $("messages").replaceChildren(); notice("New conversation. My saved synthetic preferences remain available."); }
$("login").addEventListener("submit", event => {
  event.preventDefault(); key=$("key").value; $("key").value="";
  $("login").hidden=true; $("message").disabled=false; $("send").disabled=false;
  $("message").focus(); notice("Connected locally. My first request will verify the access key.");
});
$("signout").onclick = () => { if(busy)return; key="";clear();$("drafts").replaceChildren();$("login").hidden=false;$("message").disabled=true;$("send").disabled=true;notice("Signed out. Chat and access key cleared from this tab."); };
$("newchat").onclick = () => { if(!busy)clear(); };
document.querySelectorAll("[data-prompt]").forEach(button => button.onclick=()=>{
  if(!key){$("key").focus();return;} $("message").value=button.dataset.prompt;$("message").focus();
});
$("chat").addEventListener("submit", async event => {
  event.preventDefault(); if(busy || !key)return;
  const text=$("message").value.trim();if(!text)return;
  busy=true;$("send").disabled=true;$("message").disabled=true;
  const user={role:"user",content:text};bubble("user",text);$("message").value="";
  notice("Working on it…");const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),155000);
  try{
    const response=await fetch("/v1/chat/completions",{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+key},
      body:JSON.stringify({model:"hermes-agent",stream:false,messages:[...history,user]}),signal:controller.signal});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error || "Request failed. Please try again.");
    const reply=data.choices?.[0]?.message?.content;
    if(typeof reply!=="string" || !reply.trim())throw new Error("No usable reply was returned.");
    history.push(user,{role:"assistant",content:reply});bubble("assistant",reply);
    notice("Email approval: in Telegram, use /review followed by the draft ID.");
  }catch(error){bubble("assistant",error.name==="AbortError"?"The request timed out. The action may still be running; check before repeating it.":error.message,true);notice("Reply not confirmed.");}
  finally{clearTimeout(timer);busy=false;$("send").disabled=false;$("message").disabled=false;$("message").focus();}
});
async function health(){try{const response=await fetch("/health",{signal:AbortSignal.timeout(5000)});const data=await response.json();const ready=response.ok&&data.status==="ready";$("health").textContent=ready?"Gateway available":"Gateway unavailable";$("indicator").classList.toggle("ready",ready);}catch{$("health").textContent="Connection unavailable";$("indicator").classList.remove("ready");}}
health();setInterval(health,30000);

async function draftRequest(path, payload) {
  if(!key)throw new Error("Connect before reviewing drafts.");
  const response=await fetch(path,{method:payload?"POST":"GET",
    headers:{"Authorization":"Bearer "+key,"Content-Type":"application/json"},
    ...(payload?{body:JSON.stringify(payload)}:{}),signal:AbortSignal.timeout(35000)});
  const data=await response.json();
  if(!response.ok)throw new Error(data.error||"Draft request failed.");
  return data;
}
async function showDrafts(){
  try{
    const data=await draftRequest("/content");
    $("drafts").replaceChildren();
    if(!data.items.length){$("drafts").textContent="No content drafts yet. Ask me to research an idea.";return;}
    for(const draft of data.items){
      const card=document.createElement("article");card.className="content-draft";
      const title=document.createElement("h3");title.textContent=draft.topic;
      const status=document.createElement("p");status.textContent="Draft · "+draft.status;status.className="note";
      const edit=document.createElement("textarea");edit.value=draft.body;edit.maxLength=3000;edit.rows=6;
      edit.setAttribute("aria-label","Revise draft: "+draft.topic);
      const sources=document.createElement("p");sources.className="draft-sources";
      sources.textContent="Sources: "+draft.sources.join(" · ");
      const actions=document.createElement("div");actions.className="draft-actions";
      for(const [label,action]of [["Copy draft","copied"],["Save revision","revise"],["Dismiss","dismiss"]]){
        const button=document.createElement("button");button.type="button";button.className="quiet";button.textContent=label;
        button.onclick=async()=>{
          button.disabled=true;
          try{
            if(action==="copied"){
              if(edit.value!==draft.body)throw new Error("Save the revision before copying it.");
              await navigator.clipboard.writeText(draft.body);
            }
            await draftRequest("/content/"+draft.id+"/review",{revision:draft.revision,action,body:edit.value});
            notice(action==="copied"?"Draft copied for my review. Nothing was published.":"Draft updated.");
            await showDrafts();
          }catch(error){notice(error.message);}
          finally{button.disabled=false;}
        };
        actions.append(button);
      }
      card.append(title,status,edit,sources,actions);$("drafts").append(card);
    }
  }catch(error){notice(error.message);}
}
$("refresh-drafts").onclick=showDrafts;
