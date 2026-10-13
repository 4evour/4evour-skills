import { jsPDF } from 'jspdf';
import { getFontEmbedCSS, toPng } from 'html-to-image';

export async function exportCardPdf(cards: HTMLElement[], filename: string, onProgress: (done: number, total: number) => void) {
  if (!cards.length) throw new Error('没有可导出的页面。');
  await document.fonts.ready;
  await new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
  if (cards.some(card => {const content=card.querySelector<HTMLElement>('.card-content'); return Boolean(content && content.scrollHeight > content.clientHeight + 1);})) throw new Error('检测到卡片内容溢出，请调整排版后导出。');
  const width = cards[0].offsetWidth;
  const height = cards[0].offsetHeight;
  const pdf = new jsPDF({orientation: 'portrait', unit: 'px', format: [width, height], hotfixes: ['px_scaling']});
  pdf.setProperties({title: filename, creator: 'Md2Card 本地排版工作台'});
  const fontEmbedCSS = await getFontEmbedCSS(cards[0]);
  for (let index = 0; index < cards.length; index++) {
    const card = cards[index];
    await Promise.all(Array.from(card.querySelectorAll('img')).map(image => image.decode().catch(() => {throw new Error('有图片无法加载，请先处理图片提示。');})));
    const image = await toPng(card, {fontEmbedCSS, pixelRatio: 1, width, height, cacheBust: false});
    if (index) pdf.addPage([width, height], 'portrait');
    pdf.addImage(image, 'PNG', 0, 0, width, height, undefined, 'FAST');
    onProgress(index + 1, cards.length);
    await new Promise(resolve => setTimeout(resolve, 0));
  }
  const link = document.createElement('a');
  link.href = URL.createObjectURL(pdf.output('blob'));
  link.download = `${(filename || '卡片').replace(/[\\/:*?"<>|]/g, '-').slice(0, 80)}.pdf`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 60_000);
}
