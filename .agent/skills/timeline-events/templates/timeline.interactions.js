'use strict';
(function(){
  const payload=document.getElementById('timeline-event-data');
  const sheet=document.getElementById('event-detail');
  if(!payload||!sheet||!('showModal' in sheet))return;
  let model;
  try{model=JSON.parse(payload.textContent);}catch(error){console.warn('Timeline data malformed',error);return;}
  const events=model.events||[];
  const sources=new Map((model.sources||[]).map(source=>[source.id,source]));
  const $=id=>document.getElementById(id);
  const title=$('detail-title'),date=$('detail-date'),description=$('detail-description');
  const references=$('detail-references'),counter=$('detail-counter');
  const previous=$('detail-previous'),next=$('detail-next'),close=$('detail-close');
  let selected=-1,restoreFocus=null;

  function showEvent(index){
    if(index<0||index>=events.length)return;
    selected=index;
    const event=events[index];
    date.textContent=event.date;
    title.textContent=event.title;
    description.textContent=event.description;
    counter.textContent=(index+1)+' / '+events.length;
    previous.disabled=index===0;
    next.disabled=index===events.length-1;
    references.replaceChildren();
    if(model.verification_state==='reference_transcription'){
      const warning=document.createElement('p');
      warning.className='detail-warning';
      warning.textContent='原图内容转录 · 未经独立事实审计。此处只展示参考图中已有的文字。';
      references.append(warning);
    }else{
      const label=document.createElement('h3');label.textContent='关联资料';references.append(label);
      let count=0;
      for(const id of event.source_ids||[]){
        const source=sources.get(id);if(!source)continue;
        const a=document.createElement('a');
        a.href=source.url;
        a.target='_blank';a.rel='noopener noreferrer';
        a.textContent=source.publisher+' · '+source.title+' ↗';
        references.append(a);count++;
      }
      if(!count){const note=document.createElement('p');note.textContent='该节点暂无可展示的来源链接。';references.append(note);}
    }
    document.querySelectorAll('.event').forEach((node,i)=>node.classList.toggle('is-selected',i===index));
  }
  function openEvent(index,trigger){
    if(!sheet.open){restoreFocus=trigger;sheet.showModal();}
    showEvent(index);
    close.focus({preventScroll:true});
  }
  document.querySelectorAll('[data-event-index]').forEach(button=>{
    button.addEventListener('click',()=>openEvent(Number(button.dataset.eventIndex),button));
  });
  previous.addEventListener('click',()=>{showEvent(selected-1);previous.focus();});
  next.addEventListener('click',()=>{showEvent(selected+1);next.focus();});
  close.addEventListener('click',()=>sheet.close());
  sheet.addEventListener('click',event=>{
    if(event.target!==sheet)return;
    const bounds=sheet.getBoundingClientRect();
    if(event.clientX<bounds.left||event.clientX>bounds.right||event.clientY<bounds.top||event.clientY>bounds.bottom)sheet.close();
  });
  sheet.addEventListener('keydown',event=>{
    if(event.key==='ArrowLeft' && selected>0){event.preventDefault();showEvent(selected-1);}
    if(event.key==='ArrowRight' && selected<events.length-1){event.preventDefault();showEvent(selected+1);}
  });
  sheet.addEventListener('close',()=>{
    selected=-1;
    document.querySelectorAll('.event.is-selected').forEach(node=>node.classList.remove('is-selected'));
    if(restoreFocus && document.contains(restoreFocus))restoreFocus.focus({preventScroll:true});
  });
})();
