const defaultData = require('../../data/subscriptions');
const { enrichRecords, loadRecords } = require('../../utils/subscription');

const REMINDER_FILTERS = ['全部', '已过期', '7天内续费', '30天内续费'];

Page({
  data: {
    filters: REMINDER_FILTERS,
    filterIndex: 0,
    records: []
  },

  onShow() {
    this.refresh();
  },

  onFilterChange(e) {
    this.setData({ filterIndex: Number(e.detail.value) });
    this.refresh();
  },

  refresh() {
    const raw = loadRecords(defaultData);
    const all = enrichRecords(raw)
      .filter((item) => item.status === '活跃')
      .sort((a, b) => {
        const left = a.daysLeft === null ? Number.MAX_SAFE_INTEGER : a.daysLeft;
        const right = b.daysLeft === null ? Number.MAX_SAFE_INTEGER : b.daysLeft;
        return left - right;
      });

    const selected = REMINDER_FILTERS[this.data.filterIndex];
    let records = all;

    if (selected !== '全部') {
      records = all.filter((item) => item.reminderLevel === selected);
    }

    this.setData({ records });
  }
});
