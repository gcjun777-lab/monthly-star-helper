const state = {
  inputDir: '',
  outputDir: '',
  templatePath: '',
  fontPath: '',
  readmePath: '',
  logs: [],
  running: false,
};

const els = {
  inputCount: document.getElementById('input-count'),
  outputCount: document.getElementById('output-count'),
  runState: document.getElementById('run-state'),
  runStateDetail: document.getElementById('run-state-detail'),
  inputDir: document.getElementById('input-dir'),
  outputDir: document.getElementById('output-dir'),
  templatePath: document.getElementById('template-path'),
  fontPath: document.getElementById('font-path'),
  templateStatus: document.getElementById('template-status'),
  backendMode: document.getElementById('backend-mode'),
  logStream: document.getElementById('log-stream'),
  recentOutputList: document.getElementById('recent-output-list'),
  inputFileList: document.getElementById('input-file-list'),
  startBtn: document.getElementById('start-btn'),
  clearLogBtn: document.getElementById('clear-log-btn'),
  openReadmeBtn: document.getElementById('open-readme-btn'),
};

function formatFileSize(size) {
  if (size >= 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }
  if (size >= 1024) {
    return `${Math.round(size / 1024)} KB`;
  }
  return `${size} B`;
}

function formatDate(isoString) {
  const date = new Date(isoString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
}

function renderFileList(container, files, emptyText) {
  container.innerHTML = '';
  if (!files.length) {
    const empty = document.createElement('div');
    empty.className = 'request-item empty';
    empty.textContent = emptyText;
    container.appendChild(empty);
    return;
  }

  files.forEach((file) => {
    const item = document.createElement('div');
    item.className = 'request-item';
    item.innerHTML = `
      <strong>${file.name}</strong>
      <div class="request-meta">${formatFileSize(file.size)} · ${formatDate(file.modifiedAt)}</div>
    `;
    container.appendChild(item);
  });
}

function renderLogs() {
  els.logStream.innerHTML = '';
  if (!state.logs.length) {
    const line = document.createElement('div');
    line.className = 'log-line';
    line.dataset.level = 'muted';
    line.textContent = '这里会实时显示生成过程、报错信息和最终统计。';
    els.logStream.appendChild(line);
    return;
  }

  state.logs.forEach((entry) => {
    const line = document.createElement('div');
    line.className = 'log-line';
    line.dataset.level = entry.level;
    line.textContent = `[${formatDate(entry.timestamp)}] ${entry.message}`;
    els.logStream.appendChild(line);
  });
  els.logStream.scrollTop = els.logStream.scrollHeight;
}

function renderState(data) {
  state.inputDir = data.inputDir;
  state.outputDir = data.outputDir;
  state.templatePath = data.templatePath;
  state.fontPath = data.fontPath || '自动检测 Windows 中文字体';
  state.readmePath = data.readmePath;
  state.running = Boolean(data.isRunning);

  els.inputCount.textContent = String(data.inputCount);
  els.outputCount.textContent = String(data.outputCount);
  els.inputDir.textContent = data.inputDir;
  els.outputDir.textContent = data.outputDir;
  els.templatePath.textContent = data.templatePath;
  els.fontPath.textContent = state.fontPath;
  els.templateStatus.textContent = data.templateExists ? '已内置' : '未找到';
  els.backendMode.textContent = data.backendMode;
  els.runState.textContent = state.running ? '运行中' : '待机';
  els.runStateDetail.textContent = state.running ? '任务执行中，请等待日志结束' : '准备就绪，随时可以开始';
  els.startBtn.disabled = state.running;
  els.startBtn.textContent = state.running ? '生成中...' : '开始生成';

  renderFileList(els.recentOutputList, data.recentOutputs || [], '输出目录还没有海报，首次运行后会显示在这里。');
  renderFileList(els.inputFileList, data.inputFiles || [], '输入目录暂时没有图片，放入后这里会实时刷新。');
}

async function refreshState() {
  const data = await window.monthlyStar.getState();
  renderState(data);
}

function pushLog(entry) {
  state.logs.push(entry);
  renderLogs();
}

async function bindActions() {
  document.querySelector('[data-action="pick-input"]').addEventListener('click', async () => {
    state.inputDir = await window.monthlyStar.chooseDirectory(state.inputDir);
    els.inputDir.textContent = state.inputDir;
  });

  document.querySelector('[data-action="pick-output"]').addEventListener('click', async () => {
    state.outputDir = await window.monthlyStar.chooseDirectory(state.outputDir);
    els.outputDir.textContent = state.outputDir;
  });

  document.querySelector('[data-action="open-input"]').addEventListener('click', () => window.monthlyStar.openPath(state.inputDir));
  document.querySelector('[data-action="open-output"]').addEventListener('click', () => window.monthlyStar.openPath(state.outputDir));
  els.openReadmeBtn.addEventListener('click', () => window.monthlyStar.openPath(state.readmePath));

  els.startBtn.addEventListener('click', async () => {
    pushLog({ level: 'muted', message: '已发起新任务，正在连接后端...', timestamp: new Date().toISOString() });
    state.running = true;
    renderState({
      inputDir: state.inputDir,
      outputDir: state.outputDir,
      templatePath: state.templatePath,
      fontPath: state.fontPath,
      readmePath: state.readmePath,
      inputCount: Number(els.inputCount.textContent),
      outputCount: Number(els.outputCount.textContent),
      inputFiles: [],
      recentOutputs: [],
      templateExists: true,
      backendMode: document.getElementById('backend-mode').textContent,
      isRunning: true,
    });

    try {
      await window.monthlyStar.startGeneration({
        inputDir: state.inputDir,
        outputDir: state.outputDir,
        templatePath: state.templatePath,
        fontPath: state.fontPath.includes('自动检测') ? '' : state.fontPath,
      });
    } catch (error) {
      pushLog({ level: 'error', message: error.message, timestamp: new Date().toISOString() });
      state.running = false;
      await refreshState();
    }
  });

  els.clearLogBtn.addEventListener('click', () => {
    state.logs = [];
    renderLogs();
  });
}

window.monthlyStar.onLog((entry) => {
  pushLog(entry);
});

window.monthlyStar.onFinished(async (payload) => {
  state.running = false;
  await refreshState();
  if (payload?.state) {
    renderState(payload.state);
  }
});

(async function init() {
  renderLogs();
  await refreshState();
  await bindActions();
})();
