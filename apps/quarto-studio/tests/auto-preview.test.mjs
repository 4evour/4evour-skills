import {test} from 'node:test';
import assert from 'node:assert/strict';
import {AutoPreview, restoreAutoPreview, AUTO_PREVIEW_VERSION} from '../web/auto-preview.mjs';

function clock() {
  let time = 0, nextId = 0;
  const timers = new Map();
  return {
    now: () => time,
    setTimer: (callback, delay) => {const id = ++nextId; timers.set(id, {callback, at: time + delay}); return id;},
    clearTimer: id => timers.delete(id),
    async tick(delta) {
      time += delta;
      for (const [id, timer] of [...timers]) if (timer.at <= time) {timers.delete(id); timer.callback();}
      for (let index = 0; index < 8; index++) await Promise.resolve();
    },
    get pending() {return timers.size;},
  };
}
function deferred() {let resolve, reject; const promise = new Promise((a,b) => {resolve=a; reject=b;}); return {promise, resolve, reject};}

test('进入页面自动生成；同一轮输入只在停顿后生成一次', async () => {
  const timer = clock(); let calls = 0;
  const preview = new AutoPreview({...timer, render: async () => calls++});
  preview.setEnabled(true); await timer.tick(0);
  assert.equal(calls, 1);
  preview.changed(); await timer.tick(300);
  preview.changed(); await timer.tick(300);
  preview.changed(); await timer.tick(499);
  assert.equal(calls, 1);
  await timer.tick(1);
  assert.equal(calls, 2); assert.equal(timer.pending, 0);
});

test('编译期间连续编辑只接续最新内容，并且任务不重叠', async () => {
  const timer = clock(), first = deferred(); let text = '初稿'; const submitted = [];
  const preview = new AutoPreview({...timer, render: async () => {submitted.push(text); if (submitted.length === 1) await first.promise;}});
  preview.setEnabled(true); await timer.tick(0);
  text = '中间稿'; preview.changed(); await timer.tick(700);
  text = '最终稿'; preview.changed(); await timer.tick(700);
  assert.deepEqual(submitted, ['初稿']);
  first.resolve(); await timer.tick(0); await timer.tick(0);
  assert.deepEqual(submitted, ['初稿', '最终稿']); assert.equal(timer.pending, 0);
});

test('长编译刚结束时仍尊重最后一次输入的防抖时间', async () => {
  const timer=clock(), first=deferred(); let calls=0;
  const preview=new AutoPreview({...timer,render:async()=>{if (++calls===1) await first.promise;}});
  preview.setEnabled(true); await timer.tick(0); await timer.tick(1000);
  preview.changed(); first.resolve(); await timer.tick(0); await timer.tick(499);
  assert.equal(calls,1); await timer.tick(1); assert.equal(calls,2);
});

test('关闭自动更新会取消等待任务，手动更新仍可用', async () => {
  const timer=clock(); let calls=0;
  const preview=new AutoPreview({...timer,render:async()=>calls++});
  preview.setEnabled(true); preview.setEnabled(false); await timer.tick(1000);
  assert.equal(calls,0); await preview.flush(); assert.equal(calls,1);
  preview.changed(); await timer.tick(1000); assert.equal(calls,1);
});

test('关闭后重新开启会处理等待的修改', async () => {
  const timer=clock(); let calls=0;
  const preview=new AutoPreview({...timer,render:async()=>calls++});
  preview.changed(); await timer.tick(1000); preview.setEnabled(true); await timer.tick(0);
  assert.equal(calls,1);
});

test('失败不自动无限重试，修改后可继续生成', async () => {
  const timer=clock(); let calls=0, errors=0;
  const preview=new AutoPreview({...timer,render:async()=>{if (++calls===1) throw Error('无效文档');},onError:()=>errors++});
  preview.setEnabled(true); await timer.tick(0); await timer.tick(10000);
  assert.equal(calls,1); assert.equal(errors,1); assert.equal(timer.pending,0);
  preview.changed(); await timer.tick(500); assert.equal(calls,2);
});

test('中文输入组合或空文档未就绪时不启动编译', async () => {
  const timer=clock(); let ready=false, calls=0;
  const preview=new AutoPreview({...timer,isReady:()=>ready,render:async()=>calls++});
  preview.setEnabled(true); preview.changed(); await timer.tick(1000); assert.equal(calls,0);
  ready=true; preview.changed(); await timer.tick(500); assert.equal(calls,1);
});

test('旧默认迁移为自动更新，用户新版手动关闭的偏好保留', () => {
  assert.equal(restoreAutoPreview(undefined),true);
  assert.equal(restoreAutoPreview({auto:false}),true);
  assert.equal(restoreAutoPreview({auto:false,autoPreviewVersion:AUTO_PREVIEW_VERSION}),false);
  assert.equal(restoreAutoPreview({auto:true,autoPreviewVersion:AUTO_PREVIEW_VERSION}),true);
});
