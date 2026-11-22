'use strict';
(function () {
  const $ = (x) => document.getElementById(x);
  let catalog = {taxonomies: [], events: []};
  let selected = 'all';
  let query = '';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const revealObserver = ('IntersectionObserver' in window && !reducedMotion.matches) ? new IntersectionObserver(entries => {
    for(const entry of entries){
      if(entry.isIntersecting){entry.target.classList.add('in-view');revealObserver.unobserve(entry.target);}
    }
  }, {threshold:.08,rootMargin:'0px 0px -24px 0px'}) : null;
  function reveal(node){if(revealObserver){node.classList.add('reveal');revealObserver.observe(node);}}
  const statusLabels = {reference_transcription:'原图复刻 · 尚未核验',verified:'已完成资料审校'};

  function el(tag, className, text){
    const node=document.createElement(tag);
    if(className) node.className=className;
    if(text!==undefined) node.textContent=text;
    return node;
  }
  function renderFilters(){
    const root=$('category-filters');root.replaceChildren();
    const all=[{id:'all',name:'全部主题'},...catalog.taxonomies];
    for(const cat of all){
      const btn=el('button','filter-pill',cat.name);
      btn.type='button';btn.dataset.id=cat.id;
      btn.setAttribute('aria-pressed',String(selected===cat.id));
      btn.addEventListener('click',()=>{selected=cat.id;renderFilters();renderCards();});
      root.append(btn);
    }
  }
  function renderCards(){
    const root=$('catalog-items');root.replaceChildren();
    const q=query.toLocaleLowerCase('zh-CN');
    const entries=catalog.events.filter(entry=>{
      const group=selected==='all'||entry.category===selected;
      const terms=[entry.title,entry.description,entry.range,...entry.tags].join(' ').toLocaleLowerCase('zh-CN');
      return group&&(!q||terms.includes(q));
    });
    $('result-count').textContent=entries.length+' 个条目';
    $('catalog-empty').hidden=entries.length>0;
    for(const entry of entries){
      const category=catalog.taxonomies.find(x=>x.id===entry.category);
      const card=el('a','catalog-card');
      card.href=entry.url;
      card.setAttribute('aria-label',entry.title+'，打开可交互时间轴');
      const media=el('div','catalog-card-media');
      const graphic=el('div','card-graphic');
      graphic.append(el('small','', 'EVENT STUDY / '+entry.range));
      graphic.append(el('h3','',entry.title));
      const line=el('div','card-timeline');
      for(let i=0;i<6;i++) line.append(el('i'));
      graphic.append(line);
      media.append(graphic,el('span','card-media-label','EDITABLE HTML'));
      const body=el('div','catalog-card-body');
      const meta=el('div','card-meta');
      meta.append(el('span','tag',category?category.name:'未分类'),el('span','',entry.range),el('span','',entry.nodes+' 个节点'));
      body.append(meta,el('h3','',entry.title),el('p','',entry.description));
      const foot=el('div','card-foot');
      foot.append(el('span','status-unverified',statusLabels[entry.status]||'待确认'));
      const link=el('span','card-link','查看时间轴 ↗');
      foot.append(link);body.append(foot);card.append(media,body);root.append(card);reveal(card);
    }
  }
  function renderTaxonomy(){
    const root=$('taxonomy');root.replaceChildren();
    for(const tax of catalog.taxonomies){
      const count=catalog.events.filter(ev=>ev.category===tax.id).length;
      const card=el('button','taxonomy-card');
      card.type='button';
      card.setAttribute('aria-label','筛选'+tax.name+'分类的事件');
      card.addEventListener('click',()=>{
        selected=tax.id;query='';$('catalog-search').value='';
        renderFilters();renderCards();
        $('explore').scrollIntoView({behavior:reducedMotion.matches?'auto':'smooth',block:'start'});
        requestAnimationFrame(()=>document.querySelector('.filter-pill[aria-pressed=true]')?.focus({preventScroll:true}));
      });
      const top=el('span','taxonomy-top');
      top.append(el('span','taxonomy-symbol',tax.symbol),el('span','taxonomy-count',count+' 个已发布'));
      card.append(top,el('span','taxonomy-heading',tax.name),el('span','taxonomy-description',tax.description));
      const tags=el('span','taxonomy-tags');
      for(const t of tax.tags)tags.append(el('span','',t));
      card.append(tags);root.append(card);reveal(card);
    }
  }
  async function loadCatalog(){
    try{
      const response=await fetch('./data/catalog.json',{cache:'no-cache'});
      if(!response.ok)throw new Error('HTTP '+response.status);
      const data=await response.json();
      if(!Array.isArray(data.events)||!Array.isArray(data.taxonomies))throw new Error('Invalid catalog');
      catalog=data;
      $('stat-events').textContent=data.events.length;
      $('stat-nodes').textContent=data.events.reduce((n,x)=>n+(x.nodes||0),0);
      renderFilters();renderCards();renderTaxonomy();
    }catch(err){
      $('result-count').textContent='资料库暂时无法加载';
      $('catalog-empty').hidden=false;
      $('catalog-empty').textContent='当前无法读取目录数据，请稍后刷新，或前往 GitHub 仓库查看静态事件页面。';
      console.warn('Could not load catalog',err);
    }
  }
  $('catalog-search').addEventListener('input',(event)=>{query=event.target.value.trim();renderCards();});
  $('prompt-form').addEventListener('submit',function(event){
    event.preventDefault();
    const topic=$('prompt-topic').value.trim(),range=$('prompt-range').value.trim(),focus=$('prompt-focus').value.trim();
    if(!topic){$('prompt-topic').focus();return;}
    const output=$('prompt-output').value;
    const message=[
      '使用 1998x-stack/timeline-events 仓库中的 timeline-events SKILL。',
      '事件主题：'+topic,
      range?'时间范围：'+range:'时间范围：根据可靠证据确定，并明确资料截止日期。',
      focus?'研究重点：'+focus:'研究重点：重要转折、因果与争议、关键阶段。',
      '严格执行：检索原始资料→交叉核验关键节点→生成 JSON 证据数据→渲染 '+output+'→自动测试→人工复核。',
      '请使用财经白底深蓝时间轴版式，历史节点为蓝色，最后一个节点红色，事件日期上下交错排列；输出移动端可读的 HTML。',
      '禁止编造事件、日期、轮次、协议或 URL。需交付逐节点来源与事实争议说明。'
    ].join('\n');
    $('generated-prompt').value=message;
    $('prompt-result').hidden=false;
    $('copy-status').textContent='这是任务指令，不是在本站执行 AI 生成。';
  });
  $('copy-prompt').addEventListener('click',async()=>{
    const ta=$('generated-prompt');
    try{await navigator.clipboard.writeText(ta.value);$('copy-status').textContent='已复制任务指令。';$('copy-prompt').textContent='✓ 已复制';setTimeout(()=>{$('copy-prompt').textContent='复制指令';},1500);}
    catch{ta.focus();ta.select();$('copy-status').textContent='浏览器不支持自动复制，请选中后手动复制。';}
  });
  for(const button of document.querySelectorAll('.example-subject')){
    button.addEventListener('click',()=>{$('prompt-topic').value=button.dataset.subject;document.getElementById('create').scrollIntoView({behavior:reducedMotion.matches?'auto':'smooth'});$('prompt-topic').focus({preventScroll:true});});
  }
  const menu=$('menu-toggle');
  menu.addEventListener('click',()=>{const list=$('mobile-nav');const visible=list.hidden;list.hidden=!visible;menu.setAttribute('aria-expanded',String(visible));});
  for(const a of document.querySelectorAll('#mobile-nav a'))a.addEventListener('click',()=>{$('mobile-nav').hidden=true;menu.setAttribute('aria-expanded','false');});
  // Intentional motion: reveal content once, not during every scroll frame.
  if(revealObserver){
    document.documentElement.classList.add('motion-ready');
    for(const node of document.querySelectorAll('.hero-copy,.hero-visual,.section-header,.process-grid article,.create-copy,.create-form'))reveal(node);
  }
  // Subtle editorial cover parallax, only for fine pointers and full-motion users.
  const visual=document.querySelector('.hero-visual');
  if(visual && !reducedMotion.matches && window.matchMedia('(hover:hover) and (pointer:fine)').matches){
    visual.addEventListener('pointermove',event=>{
      const rect=visual.getBoundingClientRect();
      const x=(event.clientX-rect.left)/rect.width-.5;
      const y=(event.clientY-rect.top)/rect.height-.5;
      visual.style.setProperty('--cover-ry',(x*4).toFixed(2)+'deg');
      visual.style.setProperty('--cover-rx',(-y*3).toFixed(2)+'deg');
    },{passive:true});
    visual.addEventListener('pointerleave',()=>{visual.style.setProperty('--cover-ry','0deg');visual.style.setProperty('--cover-rx','0deg');});
  }
  const progress=document.querySelector('.scroll-progress');
  const masthead=document.querySelector('.masthead');
  let scheduled=false;
  function updateScroll(){
    const height=Math.max(1,document.documentElement.scrollHeight-window.innerHeight);
    if(progress)progress.style.transform='scaleX('+Math.min(1,window.scrollY/height)+')';
    masthead?.classList.toggle('is-scrolled',window.scrollY>22);
    scheduled=false;
  }
  window.addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(updateScroll);}},{passive:true});
  updateScroll();
  loadCatalog();
})();
