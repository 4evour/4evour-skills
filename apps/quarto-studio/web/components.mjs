// 组件标记只包裹选中文字；分隔线可在光标处插入。
const TITLES = {takeaway: '核心结论', note: '阅读备注', info: '阅读提示', alert: '需要留意', success: '值得保留', step: '操作步骤'};
export function componentMarkup(kind, selected, source = '') {
  if (!['lead','takeaway','pullquote','note','info','alert','success','step','tags','divider'].includes(kind)) throw Error('不支持的组件');
  if (!selected.trim() && kind !== 'divider') throw Error('先在正文里选中一段文字，再选择标记。');
  const runs = [...selected.matchAll(/^(:{3,})/gm)].map(item => item[1].length);
  const fence = ':'.repeat(Math.max(3, ...runs.map(length => length + 1)));
  const title = TITLES[kind];
  const next = kind === 'step' ? [...source.matchAll(/\.kami-step\b/g)].length + 1 : 0;
  return `\n\n${fence} {.kami-${kind}${title ? ` title="${title}"` : ''}${next ? ` value="${String(next).padStart(2,'0')}"` : ''}}\n${selected.trim()}\n${fence}\n\n`;
}
