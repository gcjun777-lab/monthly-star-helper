const STORE_KEY = 'subscription_records_v1';

const PERIOD_MONTHS_MAP = {
  '月': 1,
  '季': 3,
  '年': 12,
  '2年': 24
};

function toNumber(value) {
  const n = Number(value);
  return Number.isNaN(n) ? 0 : n;
}

function round2(n) {
  return Math.round(n * 100) / 100;
}

function parseDate(dateText) {
  if (!dateText) return null;
  const date = new Date(dateText + 'T00:00:00');
  return Number.isNaN(date.getTime()) ? null : date;
}

function getDaysLeft(dateText) {
  const target = parseDate(dateText);
  if (!target) return null;

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const oneDay = 24 * 60 * 60 * 1000;
  return Math.floor((target.getTime() - today.getTime()) / oneDay);
}

function getReminderLevel(daysLeft) {
  if (daysLeft === null) return '未填写';
  if (daysLeft < 0) return '已过期';
  if (daysLeft <= 7) return '7天内续费';
  if (daysLeft <= 30) return '30天内续费';
  return '正常';
}

function normalizeRecord(record) {
  const periodMonths = PERIOD_MONTHS_MAP[record.period] || 1;
  const monthlyCost = round2(toNumber(record.price) / periodMonths);
  const yearlyCost = round2(monthlyCost * 12);
  const cancelSaving = record.status === '待取消' ? yearlyCost : 0;
  const daysLeft = getDaysLeft(record.renewalDate);

  return {
    ...record,
    price: toNumber(record.price),
    periodMonths,
    monthlyCost,
    yearlyCost,
    cancelSaving,
    daysLeft,
    reminderLevel: getReminderLevel(daysLeft)
  };
}

function enrichRecords(records) {
  return records.map(normalizeRecord).sort((a, b) => b.yearlyCost - a.yearlyCost);
}

function calcDashboard(records) {
  const enriched = enrichRecords(records);

  return {
    totalMonthly: round2(enriched.reduce((sum, item) => sum + item.monthlyCost, 0)),
    totalYearly: round2(enriched.reduce((sum, item) => sum + item.yearlyCost, 0)),
    cancelSavingYearly: round2(enriched.reduce((sum, item) => sum + item.cancelSaving, 0)),
    activeCount: enriched.filter((item) => item.status === '活跃').length,
    pendingCancelCount: enriched.filter((item) => item.status === '待取消').length,
    lowUsageCount: enriched.filter((item) => item.isFrequent === 'N').length,
    topCostList: enriched.slice(0, 3)
  };
}

function saveRecords(records) {
  wx.setStorageSync(STORE_KEY, records);
}

function loadRecords(defaultData) {
  const saved = wx.getStorageSync(STORE_KEY);
  if (Array.isArray(saved) && saved.length) {
    return saved;
  }
  saveRecords(defaultData);
  return defaultData;
}

function upsertRecord(records, input) {
  const record = { ...input };

  if (!record.id) {
    record.id = 'sub-' + Date.now();
  }

  const index = records.findIndex((item) => item.id === record.id);
  if (index >= 0) {
    records[index] = record;
  } else {
    records.unshift(record);
  }

  return records;
}

function removeRecord(records, id) {
  return records.filter((item) => item.id !== id);
}

module.exports = {
  STORE_KEY,
  PERIOD_MONTHS_MAP,
  enrichRecords,
  calcDashboard,
  loadRecords,
  saveRecords,
  upsertRecord,
  removeRecord
};
