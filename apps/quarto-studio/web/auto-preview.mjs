// 停止输入后合并生成请求；一次只运行一个任务，完成后接续最新修改。
export const AUTO_PREVIEW_VERSION = 2;
export function restoreAutoPreview(saved) {
  return saved?.autoPreviewVersion === AUTO_PREVIEW_VERSION ? saved.auto !== false : true;
}

export class AutoPreview {
  constructor({render, isReady = () => true, onWaiting = () => {}, onError = () => {}, delay = 500,
    now = () => Date.now(), setTimer = (callback, delay) => setTimeout(callback, delay), clearTimer = timer => clearTimeout(timer)}) {
    Object.assign(this, {render, isReady, onWaiting, onError, delay, now, setTimer, clearTimer});
    this.enabled = false;
    this.running = false;
    this.revision = 0;
    this.attempted = -1;
    this.timer = null;
    this.due = 0;
  }
  cancelPending() {
    if (this.timer !== null) this.clearTimer(this.timer);
    this.timer = null;
  }
  setEnabled(value) {
    this.enabled = Boolean(value);
    this.schedule();
  }
  changed() {
    this.revision++;
    this.due = this.now() + this.delay;
    this.schedule();
  }
  schedule() {
    this.cancelPending();
    if (!this.enabled || this.running || !this.isReady() || this.attempted === this.revision) return;
    this.onWaiting();
    this.timer = this.setTimer(() => {this.timer = null; void this.flush(false);}, Math.max(0, this.due - this.now()));
  }
  async flush(force = true) {
    this.cancelPending();
    if (this.running || !this.isReady() || (!force && (!this.enabled || this.attempted === this.revision))) return;
    const revision = this.revision;
    this.running = true;
    try {await this.render();}
    catch (error) {this.onError(error);}
    finally {
      this.attempted = revision;
      this.running = false;
      this.schedule();
    }
  }
}
