// Playwright test-harness init script — NOT part of the shipped tool.
//
// Mocks the File System Access API (showDirectoryPicker / showOpenFilePicker /
// showSaveFilePicker, and the handle objects they return) against the REAL local
// filesystem, via Python-side bridge functions exposed on `window` by harness.py
// (__fsListDir/__fsReadFile/__fsWriteFile/__fsIsDir/__fsIsFile/__fsMkdir/__fsMtime).
//
// Why this exists: headless Chromium implements these APIs (typeof check passes) but
// calling the real showDirectoryPicker()/showOpenFilePicker()/showSaveFilePicker() hangs
// forever waiting for a native OS dialog that can never appear under automation. This
// harness lets Claude Code drive the Design Process Tool's actual browser-dependent flows
// (folder connect, decision-log save, the two Studios' file-based save/load/sync) without
// a human at the keyboard, while every read/write still hits real files on disk — nothing
// here is a synthetic in-memory fixture.
//
// Known gap: storing a real FileSystemDirectoryHandle in IndexedDB (the persisted-handle
// "reconnect" feature) relies on structured-clone preserving the handle's native prototype.
// These mock objects are plain classes — structured-clone strips their methods — so the
// reconnect-from-IndexedDB path is NOT exercised by this harness, only the first-connect
// picker path. Worth knowing if a reconnect-specific bug is ever suspected.
//
// Controlling which path a picker "returns": set window.__NEXT_DIR_PATH / __NEXT_OPEN_PATH /
// __NEXT_SAVE_PATH from Python (page.evaluate) immediately before triggering the click that
// calls the corresponding picker. Each is read-and-cleared once. Leaving it unset simulates
// a real user hitting Cancel (AbortError), matching how these tools already handle that case.
(function () {
  function abortError() { const e = new Error('The user aborted a request.'); e.name = 'AbortError'; return e; }
  function notFoundError() { const e = new Error('A requested file or directory could not be found.'); e.name = 'NotFoundError'; return e; }
  function baseName(path) { return path.split(/[\\/]/).filter(Boolean).pop(); }

  class MockFile {
    constructor(path, name, mtime) { this._path = path; this.name = name; this.lastModified = mtime; }
    async text() { return await window.__fsReadFile(this._path); }
  }
  class MockWritable {
    constructor(path) { this._path = path; this._buf = ''; }
    async write(data) { this._buf += (typeof data === 'string' ? data : String(data)); }
    async close() { await window.__fsWriteFile(this._path, this._buf); }
  }
  class MockFileHandle {
    constructor(path, name) { this.kind = 'file'; this.name = name; this._path = path; }
    async getFile() {
      const mtime = await window.__fsMtime(this._path);
      return new MockFile(this._path, this.name, mtime);
    }
    async createWritable() { return new MockWritable(this._path); }
    async queryPermission() { return 'granted'; }
    async requestPermission() { return 'granted'; }
  }
  class MockDirHandle {
    constructor(path, name) { this.kind = 'directory'; this.name = name; this._path = path; }
    async getDirectoryHandle(name, opts) {
      const p = this._path + '/' + name;
      const isDir = await window.__fsIsDir(p);
      if (!isDir) {
        if (opts && opts.create) await window.__fsMkdir(p);
        else throw notFoundError();
      }
      return new MockDirHandle(p, name);
    }
    async getFileHandle(name, opts) {
      const p = this._path + '/' + name;
      const isFile = await window.__fsIsFile(p);
      if (!isFile) {
        if (opts && opts.create) await window.__fsWriteFile(p, '');
        else throw notFoundError();
      }
      return new MockFileHandle(p, name);
    }
    async *entries() {
      const list = JSON.parse(await window.__fsListDir(this._path));
      for (const e of list) {
        yield [e.name, e.isDir ? new MockDirHandle(this._path + '/' + e.name, e.name) : new MockFileHandle(this._path + '/' + e.name, e.name)];
      }
    }
    async *values() { for await (const [, h] of this.entries()) yield h; }
    async *keys() { for await (const [n] of this.entries()) yield n; }
    async queryPermission() { return 'granted'; }
    async requestPermission() { return 'granted'; }
  }

  window.showDirectoryPicker = async function () {
    const path = window.__NEXT_DIR_PATH;
    if (!path) throw abortError();
    window.__NEXT_DIR_PATH = null;
    return new MockDirHandle(path, baseName(path));
  };
  window.showOpenFilePicker = async function () {
    const path = window.__NEXT_OPEN_PATH;
    if (!path) throw abortError();
    window.__NEXT_OPEN_PATH = null;
    if (!(await window.__fsIsFile(path))) throw notFoundError();
    return [new MockFileHandle(path, baseName(path))];
  };
  window.showSaveFilePicker = async function () {
    const path = window.__NEXT_SAVE_PATH;
    if (!path) throw abortError();
    window.__NEXT_SAVE_PATH = null;
    return new MockFileHandle(path, baseName(path));
  };
})();
