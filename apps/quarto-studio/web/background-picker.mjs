const $ = id => document.getElementById(id);

export function createBackgroundPicker({entries, getSettings, onSelect, toast}) {
  const library = [...entries];
  let activeCategory = 'all';
  const categoryOrder = ['花笺山水', '淡彩渐变', '彩色肌理', '古典纸纹', '我的上传'];
  function categories() {
    return [...new Set(library.map(entry => entry.category || '我的上传'))].sort((a, b) => {
      const rank = category => categoryOrder.includes(category) ? categoryOrder.indexOf(category) : categoryOrder.length;
      return rank(a) - rank(b);
    });
  }
  function visibleEntries() {
    if (activeCategory !== 'all') return library.filter(entry => (entry.category || '我的上传') === activeCategory);
    // “全部”交错展示不同风格，第一屏就能看到纸纹、渐变和肌理。
    const groups = categories().map(category => library.filter(entry => (entry.category || '我的上传') === category));
    const visible = [];
    for (let index = 0; groups.some(group => index < group.length); index++) {
      for (const group of groups) if (group[index]) visible.push(group[index]);
    }
    return visible;
  }
  function buildFilters() {
    const filters = $('background-filters'); filters.replaceChildren();
    for (const category of ['all', ...categories()]) {
      const button = document.createElement('button'); button.type = 'button';
      const count = category === 'all' ? library.length : library.filter(entry => (entry.category || '我的上传') === category).length;
      button.textContent = `${category === 'all' ? '全部' : category} ${count}`;
      button.setAttribute('aria-pressed', String(activeCategory === category));
      button.addEventListener('click', () => {activeCategory = category; buildGallery();});
      filters.append(button);
    }
  }
  function buildGallery() {
    const gallery = $('background-gallery');
    gallery.replaceChildren();
    buildFilters();
    for (const entry of visibleEntries()) {
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'background-choice'; button.dataset.backgroundImage = entry.id;
      button.setAttribute('aria-label', `使用${entry.label}底图`);
      const image = document.createElement('img'); image.src = entry.thumbnailUrl; image.alt = ''; image.loading = 'lazy';
      const label = document.createElement('span'); label.textContent = entry.label;
      button.append(image, label); button.addEventListener('click', () => onSelect(entry.id)); gallery.append(button);
    }
    $('background-library-empty').hidden = library.length > 0;
    $('background-library-count').textContent = `${library.length} 款`;
    gallery.scrollTop = 0;
    sync();
  }
  function sync() {
    const settings = getSettings();
    const entry = library.find(item => item.id === settings.backgroundImage);
    for (const button of $('background-gallery').children) button.setAttribute('aria-pressed', String(button.dataset.backgroundImage === settings.backgroundImage));
    $('background-image-controls').hidden = !settings.backgroundImage;
    $('clear-background-image').disabled = !settings.backgroundImage;
    const source = $('background-source'); source.replaceChildren();
    if (entry) {
      const info = document.createElement('span'); info.textContent = `${entry.label}${entry.author ? ` · ${entry.author}` : ''}`; source.append(info);
      if (entry.sourceUrl) {
        const link = document.createElement('a'); link.href = entry.sourceUrl; link.target = '_blank'; link.rel = 'noreferrer'; link.textContent = '查看来源 ↗'; source.append(link);
      }
      if (entry.usage) {const usage = document.createElement('small'); usage.textContent = entry.usage; source.append(usage);}
    } else if (settings.backgroundImage) source.textContent = '这张底图不在当前本机图库，请重新上传或选择。';
  }
  $('clear-background-image').addEventListener('click', () => onSelect(''));
  $('import-background').addEventListener('change', async event => {
    const input = event.target; const file = input.files[0]; if (!file) return;
    input.disabled = true;
    try {
      if (file.size > 12000000) throw new Error('底图请控制在 12 MB 内。');
      if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) throw new Error('请选择 PNG、JPEG 或 WebP 图片。');
      const data = await new Promise((resolve, reject) => {const reader = new FileReader(); reader.onload = () => resolve(reader.result); reader.onerror = () => reject(new Error('图片读取失败。')); reader.readAsDataURL(file);});
      const preview = new Image(); preview.src = data;
      try {await preview.decode();} catch {throw new Error('这张图片无法读取，请换一张底图。');}
      $('background-upload-status').textContent = '正在保存底图…';
      const response = await fetch('/api/backgrounds', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({data, label: file.name.replace(/\.[^.]+$/, '').slice(0, 80)})});
      const entry = await response.json(); if (!response.ok) throw new Error(entry.error || '底图保存失败。');
      if (!library.some(item => item.id === entry.id)) library.push(entry);
      activeCategory = entry.category || '我的上传'; buildGallery();
      onSelect(entry.id); toast('底图已保存到本机图库。');
    } catch (error) {toast(error.message);}
    finally {input.disabled = false; input.value = ''; $('background-upload-status').textContent = '';}
  });
  buildGallery();
  return {sync};
}
