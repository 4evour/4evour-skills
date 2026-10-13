import type { LayoutConfig } from '../domain/document';
import { canvasHeight, cardBottomPadding, cardContentWidth } from '../domain/card-metrics';

export { canvasHeight, cardBottomPadding, cardContentWidth };

function headingSizes(config: LayoutConfig): { h2: number; h3: number } {
  if (config.density === 'relaxed') return { h2: 50, h3: 38 };
  if (config.density === 'compact') return { h2: 43, h3: 32 };
  if (config.density === 'balanced') return { h2: 48, h3: 36 };
  return { h2: Math.round(config.bodyFontSize * 1.6), h3: Math.round(config.bodyFontSize * 1.2) };
}

export function cardStyle(config: LayoutConfig): Record<string, string> {
  const headings = headingSizes(config);
  const style: Record<string, string> = {
    '--body-font': `"${config.bodyFontFamily || 'Noto Sans SC Variable'}", "Microsoft YaHei", sans-serif`,
    '--heading-font': `"${config.headingFontFamily || 'Microsoft YaHei'}", "Noto Sans SC Variable", sans-serif`,
    '--quote-font': `"${config.quoteFontFamily || 'KaiTi'}", "Noto Sans SC Variable", serif`,
    '--card-height': `${canvasHeight(config.ratio)}px`,
    '--card-horizontal-padding': `${config.cardHorizontalPadding}px`,
    '--card-top-padding': `${config.cardVerticalPadding}px`,
    '--card-bottom-padding': `${cardBottomPadding(config)}px`,
    '--body-size': `${config.bodyFontSize}px`,
    '--body-line-height': String(config.bodyLineHeight),
    '--block-gap': `${config.blockGap}px`,
    '--heading-2': `${headings.h2}px`,
    '--heading-3': `${headings.h3}px`,
    '--heading-2-before-space': `${config.headingH2BeforeSpacing}px`,
    '--heading-3-before-space': `${config.headingH3BeforeSpacing}px`,
    '--code-size': `${config.codeFontSize}px`,
    '--table-font-size': `${config.tableFontSize}px`,
    '--image-max-height': `${Math.round(canvasHeight(config.ratio) * config.imageMaxHeightPercent / 100)}px`,
  };
  if (config.accentColor) style['--theme-primary'] = config.accentColor;
  if (config.textColor) style['--theme-on-surface'] = config.textColor;
  if (config.backgroundColor) {
    style['--theme-surface'] = config.backgroundColor;
    style['background-color'] = config.backgroundColor;
  }
  const color = config.accentColor || '#7b6b8c';
  if (config.backgroundPattern === 'plain') style['background-image'] = 'none';
  if (config.backgroundPattern === 'dots') {
    style['background-image'] = `radial-gradient(${color}20 1.5px, transparent 1.5px)`;
    style['background-size'] = '24px 24px';
  }
  if (config.backgroundPattern === 'grid') {
    style['background-image'] = `linear-gradient(${color}18 1px, transparent 1px), linear-gradient(90deg, ${color}18 1px, transparent 1px)`;
    style['background-size'] = '32px 32px';
  }
  return style;
}
