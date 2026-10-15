import {test} from 'node:test';
import assert from 'node:assert/strict';
import {componentMarkup} from '../web/components.mjs';
test('所有标记都保留原始选中文字', () => {
  for (const kind of ['lead','takeaway','pullquote','note','info','alert','success','step','tags']) assert.ok(componentMarkup(kind, '原文事实 42\n第二行。').includes('原文事实 42\n第二行。'));
});
test('步骤编号根据现有步骤递增', () => {assert.match(componentMarkup('step','第二步','::: {.kami-step value="01"}'), /value="02"/);});
test('分隔可直接插入，其他组件需要选择文字', () => {assert.match(componentMarkup('divider',''), /kami-divider/);assert.throws(() => componentMarkup('info',''));});
test('嵌套组件使用更长围栏，代码与原文保留', () => {const selected='::: {.kami-note}\n保留内容\n:::';const result=componentMarkup('takeaway',selected);assert.ok(result.startsWith('\n\n:::: '));assert.ok(result.includes(selected));});
