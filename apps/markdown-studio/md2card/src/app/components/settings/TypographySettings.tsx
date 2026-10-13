import type { LayoutConfig } from '../../../domain/document';
import { FONT_LIBRARY } from '../../../data/fonts';

type UpdateConfig = <Key extends keyof LayoutConfig>(key: Key, value: LayoutConfig[Key]) => void;
export function TypographySettings({config, onConfigChange}: {config: LayoutConfig; onConfigChange: UpdateConfig}) {
  return <section class="settings-category-content typography-settings">
    <h3>字体与配色</h3>
    <p class="field-help">12 种中文字体，按标题、正文和引用分别搭配。开源字体随项目保存，无需联网加载。</p>
    {([{key: 'headingFontFamily', label: '标题字体'}, {key: 'bodyFontFamily', label: '正文字体'}, {key: 'quoteFontFamily', label: '引用字体'}] as const).map(({key, label}) => <label class="studio-font-field" key={key}>
      <span>{label}</span>
      <select aria-label={label} value={config[key]} onChange={event => onConfigChange(key, event.currentTarget.value)}>
        {FONT_LIBRARY.map(font => <option key={font.family} value={font.family}>{font.label} · {font.category}</option>)}
      </select>
      <span class="studio-font-sample" style={{fontFamily: `"${config[key]}", "Microsoft YaHei"`}}>把日常，写成值得收藏的故事。</span>
    </label>)}
    <h4>自定义配色</h4>
    <div class="studio-colors">
      {([{key: 'accentColor', label: '强调色', fallback: '#66558f'}, {key: 'backgroundColor', label: '背景色', fallback: '#fcf9ff'}, {key: 'textColor', label: '正文色', fallback: '#201a2a'}] as const).map(({key, label, fallback}) => <label key={key}>
        <span>{label}</span><input aria-label={label} type="color" value={config[key] || fallback} onInput={event => onConfigChange(key, event.currentTarget.value)} />
        <small>{config[key] || '跟随主题'}</small>
      </label>)}
    </div>
    <label class="studio-font-field"><span>背景纹理</span><select aria-label="背景纹理" value={config.backgroundPattern} onChange={event => onConfigChange('backgroundPattern', event.currentTarget.value as LayoutConfig['backgroundPattern'])}>
      <option value="theme">跟随主题</option><option value="plain">纯色</option><option value="dots">细点纸</option><option value="grid">方格纸</option>
    </select></label>
    <button class="secondary-button" type="button" onClick={() => {onConfigChange('accentColor', ''); onConfigChange('backgroundColor', ''); onConfigChange('textColor', ''); onConfigChange('backgroundPattern', 'theme');}}>恢复主题配色</button>
    <h4>字体试衣间</h4>
    <p class="field-help">点击字样，把这款字体用于标题。</p>
    <div class="studio-font-gallery">{FONT_LIBRARY.map(font => <button type="button" key={font.family} aria-label={`标题使用${font.label}`} class={config.headingFontFamily === font.family ? 'selected' : ''} onClick={() => onConfigChange('headingFontFamily', font.family)}>
      <span style={{fontFamily: `"${font.family}", "Microsoft YaHei"`}}>见字如面</span><small>{font.label}</small>
    </button>)}</div>
  </section>;
}
