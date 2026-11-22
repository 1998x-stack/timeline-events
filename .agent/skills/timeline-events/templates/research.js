// Evidence audit: semantic buttons and non-destructive content filtering.
(()=>{
  const buttons=[...document.querySelectorAll('[data-audit-filter]')];
  const cards=[...document.querySelectorAll('[data-audit-group]')];
  buttons.forEach(button=>button.addEventListener('click',()=>{
    const category=button.dataset.auditFilter;
    buttons.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    cards.forEach(card=>{card.hidden=category!=='all'&&card.dataset.auditGroup!==category});
  }));
})();
