import {componentMarkup} from './components.mjs';
import {AutoPreview, AUTO_PREVIEW_VERSION, restoreAutoPreview} from './auto-preview.mjs';

const $ = id => document.getElementById(id);
const state = {bootstrap: null, settings: {}, images: [], result: null, revision: 0, busy: false, dirty: true, zoom: 0, saveTimer: null, loading: true, composing: false};
const autoPreview = new AutoPreview({
  render,
  isReady: () => !state.loading && !state.composing && Boolean(state.bootstrap?.tools.quarto) && Boolean($('markdown').value.trim()),
  onWaiting: () => status(state.result ? '等待输入结束后自动更新，当前保留上次预览' : '等待输入结束后自动生成预览', 'working'),
  onError: error => {status('自动更新失败，请重试', 'error'); notice(error.message, true);},
});
const database = new Promise((resolve, reject) => {
  const request = indexedDB.open('quarto-studio-draft', 1);
  request.onupgradeneeded = () => request.result.createObjectStore('drafts');
  request.onsuccess = () => resolve(request.result);
  request.onerror = () => reject(request.error);
});
async function readDraft() {
  const db = await database;
  return new Promise((resolve, reject) => {
    const request = db.transaction('drafts').objectStore('drafts').get('current');
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}
async function saveDraft() {
  try {
    const db = await database;
    await new Promise((resolve, reject) => {
      const transaction = db.transaction('drafts', 'readwrite');
      transaction.objectStore('drafts').put({...payload(), auto: $('auto-render').checked, autoPreviewVersion: AUTO_PREVIEW_VERSION}, 'current');
      transaction.oncomplete = resolve;
      transaction.onerror = () => reject(transaction.error);
    });
    $('save-status').textContent = '已保存到此浏览器';
  } catch { $('save-status').textContent = '本地存储不可用，请保存原文'; }
}
function payload() {return {markdown: $('markdown').value, title: $('title').value, subtitle: $('subtitle').value, author: $('author').value, settings: {...state.settings}, images: state.images.map(({name, data}) => ({name, data}))};}
function toast(message) {$('toast').textContent = message; $('toast').hidden = false; setTimeout(() => $('toast').hidden = true, 3800);}
function status(message, kind = '') {$('render-status').textContent = message; $('status-dot').className = `status-dot ${kind}`;}
function notice(message, isError = false) {$('notice').textContent = message; $('notice').hidden = !message; $('notice').className = `notice${isError ? ' error' : ''}`;}
function dirty() {
  if (state.loading) return;
  state.revision++; state.dirty = true;
  $('word-count').textContent = `${$('markdown').value.length.toLocaleString()} 字符`;
  $('save-status').textContent = '保存中…';
  clearTimeout(state.saveTimer); state.saveTimer = setTimeout(saveDraft, 500);
  if (state.busy) status($('auto-render').checked ? '正在排版，新修改会自动接续更新' : '正在排版，另有未生成的修改', 'working');
  else if (!$('auto-render').checked) status(state.result ? '有未生成的修改，点击“立即更新”' : '已修改，点击“立即更新”');
  autoPreview.changed();
}
function palette() {return state.bootstrap.themes[state.settings.theme] || state.bootstrap.themes.magazine;}
function syncControls() {
  for (const element of document.querySelectorAll('[data-setting]')) {
    const key = element.dataset.setting;
    if (element.type === 'checkbox') element.checked = Boolean(state.settings[key]);
    else if (element.type === 'color') {
      const fallback = {accentColor: 'accent', paperColor: 'paper', textColor: 'ink'}[key];
      element.value = state.settings[key] || palette()[fallback];
      $(`${key}-value`).textContent = state.settings[key] || '跟随主题';
    } else element.value = state.settings[key];
    const output = $(`${key}-value`);
    if (output && element.type === 'range') {
      const units = {fontSize: ' pt', headingSize: ' pt', coverSize: ' pt', leading: ' em', paragraphSpacing: ' em', marginX: ' in', marginY: ' in', backgroundStrength: '%'};
      output.textContent = `${Number(key === 'backgroundStrength' ? state.settings[key] * 100 : state.settings[key]).toFixed(['leading','paragraphSpacing','marginX','marginY'].includes(key) ? 2 : 1)}${units[key] || ''}`;
    }
  }
  const selectedTemplate = state.bootstrap.templates.find(item => item.id === state.settings.template);
  $('template-description').textContent = selectedTemplate?.description || '';
  $('component-toolbar').hidden = selectedTemplate?.group !== 'kami';
  $('decoration-field').hidden = selectedTemplate?.group !== 'kami';
  $('codeStyle').disabled = selectedTemplate?.group === 'kami';
  $('quoteStyle').disabled = selectedTemplate?.group === 'kami';
  for (const button of $('layout-gallery').children) button.setAttribute('aria-pressed', String(button.dataset.template === state.settings.template));
  $('vibrant-palette-field').hidden = state.settings.template !== 'vibrant-color';
  $('cover').disabled = selectedTemplate?.independentCover === false;
  $('heading-sample').style.fontFamily = `"${state.settings.headingFont}", "Microsoft YaHei", serif`;
  $('body-sample').style.fontFamily = `"${state.settings.bodyFont}", "Microsoft YaHei", serif`;
  for (const button of $('paper-presets').children) {
    const preset = state.bootstrap.paperPresets.find(item => item.id === button.dataset.paperPreset);
    button.setAttribute('aria-pressed', String(preset.theme === state.settings.theme && preset.background === state.settings.background && !state.settings.paperColor));
  }
  for (const button of $('themes').children) button.setAttribute('aria-pressed', String(button.dataset.theme === state.settings.theme));
}
function applyTemplate(template) {
  state.settings = {...state.settings, ...template.settings};
  syncControls(); dirty();
}
function buildSettings() {
  for (const preset of state.bootstrap.paperPresets) {
    const button = document.createElement('button'); button.type = 'button'; button.className = `paper-choice texture-${preset.background}`;
    button.dataset.paperPreset = preset.id; button.style.setProperty('--paper', state.bootstrap.themes[preset.theme].paper); button.style.setProperty('--ink', state.bootstrap.themes[preset.theme].accent); button.textContent = preset.label;
    button.addEventListener('click', () => {state.settings = {...state.settings, theme: preset.theme, background: preset.background, paperColor: '', textColor: '', accentColor: ''}; syncControls(); dirty();});
    $('paper-presets').append(button);
  }
  for (const template of state.bootstrap.templates.filter(item => item.group === 'kami')) {
    const button = document.createElement('button'); button.type = 'button'; button.className = 'layout-choice'; button.dataset.template = template.id;
    const preview = document.createElement('img'); preview.src = `/previews/${template.id}.webp`; preview.alt = ''; preview.loading = 'lazy';
    const label = document.createElement('strong'); label.textContent = template.label.replace('Kami · ', '');
    const caption = document.createElement('small'); caption.textContent = {'kami-reading':'单栏 · 连续阅读','kami-brief':'摘要 · 双栏分析','kami-cards':'3:4 · 章节起页'}[template.id];
    button.append(preview, label, caption); button.title = template.description;
    button.setAttribute('aria-label', `使用${label.textContent}版式`); button.addEventListener('click', () => applyTemplate(template));
    $('layout-gallery').append(button);
  }
  for (const template of state.bootstrap.templates) {
    const option = document.createElement('option'); option.value = template.id; option.textContent = template.label; $('template').append(option);
  }
  $('template-preset').addEventListener('click', () => {
    const template = state.bootstrap.templates.find(item => item.id === state.settings.template);
    if (template) {applyTemplate(template);}
  });
  for (const [id, theme] of Object.entries(state.bootstrap.themes)) {
    const button = document.createElement('button'); button.type = 'button'; button.className = 'theme-choice'; button.dataset.theme = id;
    const swatch = document.createElement('span'); swatch.className = 'theme-swatch'; swatch.textContent = 'Aa'; swatch.style.background = theme.paper; swatch.style.color = theme.accent;
    const label = document.createElement('span'); label.textContent = theme.label;
    button.append(swatch, label); button.addEventListener('click', () => {state.settings.theme = id; state.settings.accentColor = ''; state.settings.paperColor = ''; state.settings.textColor = ''; syncControls(); dirty();});
    $('themes').append(button);
  }
  for (const key of ['headingFont','bodyFont','quoteFont','codeFont']) {
    for (const font of state.bootstrap.fonts) {
      const option = document.createElement('option'); option.value = font.family; option.textContent = `${font.label} · ${font.category}${font.available ? '' : '（未安装）'}`; option.disabled = !font.available; $(key).append(option);
    }
  }
  const fontStyles = document.createElement('style');
  fontStyles.textContent = state.bootstrap.fonts.filter(font => font.available && font.previewUrl).map(font => `@font-face{font-family:${JSON.stringify(font.family)};src:url(${JSON.stringify(font.previewUrl)}) format(${JSON.stringify(font.previewFormat || "truetype")});font-weight:${font.previewWeight || (font.family === 'Noto Serif SC' ? '100 900' : '400')};font-display:swap;}`).join('\n');
  document.head.append(fontStyles);
  for (const example of state.bootstrap.examples) {
    const button = document.createElement('button'); button.type = 'button'; button.className = 'example-choice'; button.textContent = example.name;
    const hint = document.createElement('small'); hint.textContent = example.id === 'decorations' ? '纸面、提示卡、步骤、胶囊标签与章节分隔，适合体验装饰样式' : example.id === 'kami' ? '同一篇内容，包含导语、指标、重点块、表格与引用；适合切换三套版式比较' : example.id === 'comparison' ? '相同原文，3:4 纸张、浅紫色和庆科黄油标题，便于并排看' : '中文、引用、表格、公式、代码和 Mermaid'; button.append(hint);
    button.addEventListener('click', () => {
      if ($('markdown').value.trim() && !confirm('用示例替换当前正文？请先保存需要保留的原文。')) return;
      $('markdown').value = example.markdown; $('title').value = ''; $('subtitle').value = ''; $('author').value = '';
      if (example.id === 'kami' || example.id === 'decorations') state.settings = {...state.settings, ...state.bootstrap.templates.find(item => item.id === (state.settings.template.startsWith('kami-') ? state.settings.template : 'kami-reading')).settings};
      if (example.id === 'decorations') state.settings = {...state.settings, ...state.bootstrap.templates.find(item => item.id === 'kami-cards').settings, decoration: 'soft', theme: 'sage', background: 'linen', backgroundStrength: 0.28};
      if (example.id === 'comparison') state.settings = {...state.bootstrap.defaults, theme: 'lavender', paper: 'portrait', headingFont: 'ZCOOL QingKe HuangYou', fontSize: 17, headingSize: 34, marginX: 0.6, marginY: 0.55, background: 'dots', cover: false, header: false};
      syncControls(); dirty(); $('examples-dialog').close();
    });
    $('example-list').append(button);
  }
}
function setTab(name) {
  for (const tab of ['content','design']) {$(`tab-${tab}`).setAttribute('aria-selected', String(tab === name)); $(`${tab}-panel`).hidden = tab !== name;}
}
function enableLink(id, url, download = false) {
  const link = $(id); link.classList.toggle('disabled', !url); link.setAttribute('aria-disabled', String(!url));
  if (url) {link.href = url + (download ? '?download=1' : ''); if (download) link.setAttribute('download', '');}
  else {link.removeAttribute('href'); link.removeAttribute('download');}
}
function showResult(result) {
  state.result = result;
  enableLink('pdf-link', result.pdfUrl);
  enableLink('png-link', result.zipUrl, true);
  $('page-count').textContent = result.pageCount ? `${result.pageCount} 页` : '';
  $('render-time').textContent = `${result.elapsed} s`;
  $('artifact-info').textContent = `${(result.bytes / 1024).toFixed(0)} KB · PDF / 150 DPI PNG`;
  const fragment = document.createDocumentFragment();
  for (const page of result.pages) {
    const figure = document.createElement('figure'); figure.className = 'pdf-page';
    const caption = document.createElement('figcaption');
    const label = document.createElement('span'); label.textContent = `${String(page.number).padStart(2,'0')} / ${String(result.pageCount).padStart(2,'0')}`;
    const detail = document.createElement('span'); detail.textContent = 'PDF 实际页面'; caption.append(label, detail);
    const image = document.createElement('img'); image.src = page.url; image.alt = `PDF 第 ${page.number} 页`; image.loading = page.number <= 2 ? 'eager' : 'lazy';
    if (result.widthPt && result.heightPt) image.style.aspectRatio = `${result.widthPt} / ${result.heightPt}`;
    figure.append(caption, image); fragment.append(figure);
  }
  if (result.pages.length) $('preview-pages').replaceChildren(fragment);
  else {
    const message = document.createElement('div'); message.className = 'empty-preview'; message.textContent = 'PDF 已生成。安装 Poppler 可查看页面图片，也可以点击“打开 PDF”。'; $('preview-pages').replaceChildren(message);
  }
  notice((result.warnings || []).join(' '));
  $('task-info').textContent = `完成 ${result.pageCount} 页，用时 ${result.elapsed} 秒。\nPDF：${result.pdfPath}\n页面图片：${result.pagePath}`;
  $('task-info').style.whiteSpace = 'pre-wrap';
  const artifactLinks = [['打开 PDF',result.pdfUrl],['下载切页 PNG',result.zipUrl],['查看原始 Markdown',result.markdownUrl],['查看转换后的 QMD',result.qmdUrl],['查看 Typst 源码',result.typUrl],['下载样式 JSON',result.settingsUrl],['查看渲染日志',result.logUrl]];
  $('artifact-links').replaceChildren();
  for (const [label,url] of artifactLinks) {
    if (!url) continue;
    const link = document.createElement('a'); link.href = url; link.target = '_blank'; link.rel = 'noreferrer'; link.textContent = label; $('artifact-links').append(link);
  }
  $('error-detail').hidden = true;
}
async function jsonResponse(response) {let result; try {result = await response.json();} catch {throw new Error('服务返回格式不正确，请检查本地服务是否仍在运行。');} if (!response.ok) throw new Error(result.error || '请求失败'); return result;}
async function preloadPages(result) {
  await Promise.all(result.pages.slice(0, 2).map(async page => {
    const image = new Image(); image.src = page.url;
    try {await image.decode();} catch {}
  }));
}
async function render() {
  if (state.busy) return;
  if (!$('markdown').value.trim()) {toast('请先填写文章内容。'); return;}
  state.busy = true;
  const revision = state.revision;
  $('render-button').disabled = true; $('render-button').textContent = '正在排版…';
  status('正在提交排版任务…', 'working'); notice('');
  let lastTask;
  try {
    lastTask = await jsonResponse(await fetch('/api/render', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload())}));
    while (['queued','running'].includes(lastTask.status)) {
      status(state.revision !== revision && $('auto-render').checked ? '正在排版，新修改会自动接续更新' : lastTask.message, 'working');
      await new Promise(resolve => setTimeout(resolve, 650));
      lastTask = await jsonResponse(await fetch(`/api/jobs/${lastTask.id}`));
    }
    if (lastTask.status !== 'succeeded') throw new Error(lastTask.error || '排版失败，请查看日志。');
    await preloadPages(lastTask);
    state.dirty = state.revision !== revision;
    if (!state.dirty || !$('auto-render').checked) {
      const scrollTop = $('preview-scroll').scrollTop;
      showResult(lastTask);
      $('preview-scroll').scrollTop = scrollTop;
    }
    status(state.dirty ? ($('auto-render').checked ? '正在接续处理最新修改' : '已生成；还有新的修改尚未排版') : `${lastTask.pageCount} 页已更新，预览与导出使用同一份 PDF`, state.dirty ? 'working' : 'success');
    await saveDraft();
  } catch (error) {
    status('生成失败，已保留上一次成功的预览', 'error'); notice(error.message, true);
    $('error-detail').textContent = error.message; $('error-detail').hidden = false;
    if (lastTask?.logUrl) {const link = document.createElement('a'); link.href = lastTask.logUrl; link.target = '_blank'; link.rel = 'noreferrer'; link.textContent = '查看本次失败日志'; $('artifact-links').prepend(link);}
  } finally {
    state.busy = false; $('render-button').disabled = false; $('render-button').innerHTML = '<span>↻</span> 立即更新';
  }
}
function download(content, name, type) {const link = document.createElement('a'); link.href = URL.createObjectURL(new Blob([content], {type})); link.download = name; link.click(); setTimeout(() => URL.revokeObjectURL(link.href), 60000);}
function safeName() {return ($('title').value || $('markdown').value.match(/^#\s+(.+)$/m)?.[1] || '文章').replace(/[\\/:*?"<>|]/g,'-').slice(0,70);}
function updateZoom(direction) {
  state.zoom = Math.max(-2, Math.min(5, state.zoom + direction));
  if (!state.zoom) {$('preview-pages').style.removeProperty('--preview-width'); $('zoom-label').textContent = '适合宽度';}
  else {const percent = 100 + state.zoom * 15; $('preview-pages').style.setProperty('--preview-width', `${720 * percent / 100}px`); $('zoom-label').textContent = `${percent}%`;}
}
function renderImages() {
  $('attachment-count').textContent = state.images.length;
  $('image-list').replaceChildren();
  state.images.forEach((image, index) => {
    const row = document.createElement('div'); row.className = 'image-row'; const thumbnail = document.createElement('img'); thumbnail.src = image.data; thumbnail.alt = image.name;
    const reference = document.createElement('input'); reference.value = image.name; reference.setAttribute('aria-label', `图片 ${index+1} 的引用路径`); reference.addEventListener('change', () => {image.name = reference.value; dirty();});
    const remove = document.createElement('button'); remove.className = 'icon-button'; remove.textContent = '×'; remove.setAttribute('aria-label', `移除图片 ${index+1}`); remove.addEventListener('click', () => {state.images.splice(index,1); renderImages(); dirty();});
    row.append(thumbnail,reference,remove); $('image-list').append(row);
  });
}
function readDataUrl(file) {return new Promise((resolve,reject) => {const reader = new FileReader(); reader.onload = () => resolve(reader.result); reader.onerror = reject; reader.readAsDataURL(file);});}
async function init() {
  try {
    state.bootstrap = await jsonResponse(await fetch('/api/bootstrap'));
    buildSettings();
    let saved; try {saved = await readDraft();} catch {}
    state.settings = {...state.bootstrap.defaults, ...(saved?.settings || {})};
    $('markdown').value = saved?.markdown ?? state.bootstrap.examples[1].markdown;
    for (const key of ['title','subtitle','author']) $(key).value = saved?.[key] || '';
    state.images = saved?.images || []; $('auto-render').checked = restoreAutoPreview(saved);
    $('word-count').textContent = `${$('markdown').value.length.toLocaleString()} 字符`;
    syncControls(); renderImages();
    const tools = state.bootstrap.tools;
    $('engine-ready').textContent = tools.quarto ? 'Quarto 已就绪' : '需要安装 Quarto';
    if (!tools.quarto) notice('未找到 Quarto。安装并加入 PATH 后，重新启动控制台即可生成 PDF。', true);
    else if (!tools.pdftoppm) notice('PDF 生成可用；页面预览与 PNG 导出需要安装 Poppler。');
    $('render-button').disabled = !tools.quarto;
    state.loading = false; status('准备就绪，点击“立即更新”');
    autoPreview.setEnabled($('auto-render').checked);
    if (saved?.autoPreviewVersion !== AUTO_PREVIEW_VERSION) await saveDraft();
  } catch (error) {notice(`初始化失败：${error.message}`, true); status('本地服务连接失败', 'error'); state.loading = false;}
}
for (const button of document.querySelectorAll('[data-component]')) button.addEventListener('click', () => {
  const editor = $('markdown');
  const selected = editor.value.slice(editor.selectionStart, editor.selectionEnd);
  let replacement;
  try {replacement = componentMarkup(button.dataset.component, selected, editor.value);}
  catch (error) {toast(error.message); return;}
  editor.setRangeText(replacement, editor.selectionStart, editor.selectionEnd, 'select');
  editor.focus(); dirty();
});
$('tab-content').addEventListener('click', () => setTab('content'));
$('tab-design').addEventListener('click', () => setTab('design'));
for (const field of ['markdown','title','subtitle','author']) {
  $(field).addEventListener('input', dirty);
  $(field).addEventListener('compositionstart', () => {state.composing = true; autoPreview.cancelPending();});
  $(field).addEventListener('compositionend', () => {state.composing = false; dirty();});
}
for (const element of document.querySelectorAll('[data-setting]')) element.addEventListener('input', () => {if (element.dataset.setting === 'template' && element.value.startsWith('kami-')) {applyTemplate(state.bootstrap.templates.find(item => item.id === element.value)); return;} state.settings[element.dataset.setting] = element.type === 'checkbox' ? element.checked : element.type === 'range' ? Number(element.value) : element.value; syncControls(); dirty();});
$('render-button').addEventListener('click', () => autoPreview.flush());
$('auto-render').addEventListener('change', () => {
  autoPreview.setEnabled($('auto-render').checked);
  saveDraft();
  if (!$('auto-render').checked && !state.busy) status(state.dirty ? '自动更新已关闭，点击“立即更新”应用修改' : '自动更新已关闭，当前预览已是最新');
});
$('reset-settings').addEventListener('click', () => {state.settings = {...state.bootstrap.defaults}; syncControls(); dirty();});
$('reset-colors').addEventListener('click', () => {for (const key of ['accentColor','paperColor','textColor']) state.settings[key] = ''; syncControls(); dirty();});
$('zoom-in').addEventListener('click', () => updateZoom(1)); $('zoom-out').addEventListener('click', () => updateZoom(-1));
$('example-button').addEventListener('click', () => $('examples-dialog').showModal());
$('details-button').addEventListener('click', () => $('details-dialog').showModal());
for (const button of document.querySelectorAll('[data-close]')) button.addEventListener('click', () => $(button.dataset.close).close());
$('download-original').addEventListener('click', () => download($('markdown').value, `${safeName()}.md`, 'text/markdown;charset=utf-8'));
$('export-settings').addEventListener('click', () => download(JSON.stringify({title: $('title').value, subtitle: $('subtitle').value, author: $('author').value, settings: state.settings}, null, 2), `${safeName()}-样式.json`, 'application/json'));
$('import-markdown').addEventListener('change', async event => {
  const file = event.target.files[0]; if (!file) return;
  if (file.size > 2000000) {toast('文章超过 2 MB。'); event.target.value = ''; return;}
  if ($('markdown').value.trim() && !confirm('导入后会替换当前正文。需要保留时请先保存原文。')) {event.target.value = ''; return;}
  $('markdown').value = await file.text(); $('title').value = ''; $('source-label').textContent = file.name; dirty(); event.target.value = '';
});
$('import-settings').addEventListener('change', async event => {
  const file = event.target.files[0]; if (!file) return;
  try {const data = JSON.parse(await file.text()); if (!data.settings || typeof data.settings !== 'object') throw new Error('未找到样式设置。'); state.settings = {...state.bootstrap.defaults, ...Object.fromEntries(Object.entries(data.settings).filter(([key]) => key in state.bootstrap.defaults))}; syncControls(); dirty(); toast($('auto-render').checked ? '已导入样式，预览会自动更新。' : '已导入样式，点击“立即更新”查看。');}
  catch (error) {toast(`导入失败：${error.message}`);} event.target.value = '';
});
$('import-images').addEventListener('change', async event => {
  try {for (const file of event.target.files) {if (state.images.length >= 30) throw new Error('最多提供 30 张图片。'); if (file.size > 12000000) throw new Error('单张图片请控制在 12 MB 内。'); state.images.push({name: file.name, data: await readDataUrl(file)});} renderImages(); dirty();}
  catch (error) {renderImages(); dirty(); toast(error.message);} event.target.value = '';
});
init();
