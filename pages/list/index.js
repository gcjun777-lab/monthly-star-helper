const defaultData = require('../../data/subscriptions');
const {
  enrichRecords,
  loadRecords,
  saveRecords,
  upsertRecord,
  removeRecord
} = require('../../utils/subscription');

const STATUS_FILTERS = ['全部', '活跃', '待取消'];
const PERIOD_OPTIONS = ['月', '季', '年', '2年'];
const FREQUENT_OPTIONS = ['Y', 'N'];
const IMPORTANCE_OPTIONS = ['高', '中', '低'];
const STATUS_OPTIONS = ['活跃', '待取消'];

function defaultForm() {
  const now = new Date();
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');
  const today = `${now.getFullYear()}-${mm}-${dd}`;

  return {
    id: '',
    service: '',
    category: '',
    period: '月',
    price: '',
    renewalDate: today,
    isFrequent: 'Y',
    importance: '中',
    status: '活跃',
    note: ''
  };
}

Page({
  data: {
    statusFilters: STATUS_FILTERS,
    periodOptions: PERIOD_OPTIONS,
    frequentOptions: FREQUENT_OPTIONS,
    importanceOptions: IMPORTANCE_OPTIONS,
    statusOptions: STATUS_OPTIONS,
    filterIndex: 0,
    rawRecords: [],
    records: [],
    showForm: false,
    isEdit: false,
    form: defaultForm(),
    periodIndex: 0,
    frequentIndex: 0,
    importanceIndex: 1,
    statusIndex: 0
  },

  onShow() {
    const rawRecords = loadRecords(defaultData);
    this.setData({ rawRecords });
    this.applyFilter();
  },

  onFilterChange(e) {
    this.setData({ filterIndex: Number(e.detail.value) });
    this.applyFilter();
  },

  applyFilter() {
    const { rawRecords, filterIndex, statusFilters } = this.data;
    const selectedStatus = statusFilters[filterIndex];
    const all = enrichRecords(rawRecords);

    const records = selectedStatus === '全部'
      ? all
      : all.filter((item) => item.status === selectedStatus);

    this.setData({ records });
  },

  onOpenCreate() {
    this.setData({
      showForm: true,
      isEdit: false,
      form: defaultForm(),
      periodIndex: 0,
      frequentIndex: 0,
      importanceIndex: 1,
      statusIndex: 0
    });
  },

  onOpenEdit(e) {
    const { id } = e.currentTarget.dataset;
    const target = this.data.rawRecords.find((item) => item.id === id);
    if (!target) return;

    this.setData({
      showForm: true,
      isEdit: true,
      form: { ...target },
      periodIndex: PERIOD_OPTIONS.indexOf(target.period),
      frequentIndex: FREQUENT_OPTIONS.indexOf(target.isFrequent),
      importanceIndex: IMPORTANCE_OPTIONS.indexOf(target.importance),
      statusIndex: STATUS_OPTIONS.indexOf(target.status)
    });
  },

  onCloseForm() {
    this.setData({ showForm: false });
  },

  noop() {},

  onInput(e) {
    const { field } = e.currentTarget.dataset;
    this.setData({
      [`form.${field}`]: e.detail.value
    });
  },

  onPeriodChange(e) {
    const index = Number(e.detail.value);
    this.setData({
      periodIndex: index,
      'form.period': PERIOD_OPTIONS[index]
    });
  },

  onFrequentChange(e) {
    const index = Number(e.detail.value);
    this.setData({
      frequentIndex: index,
      'form.isFrequent': FREQUENT_OPTIONS[index]
    });
  },

  onImportanceChange(e) {
    const index = Number(e.detail.value);
    this.setData({
      importanceIndex: index,
      'form.importance': IMPORTANCE_OPTIONS[index]
    });
  },

  onStatusChange(e) {
    const index = Number(e.detail.value);
    this.setData({
      statusIndex: index,
      'form.status': STATUS_OPTIONS[index]
    });
  },

  onDateChange(e) {
    this.setData({ 'form.renewalDate': e.detail.value });
  },

  onSubmitForm() {
    const { form } = this.data;

    if (!form.service || !form.category || !form.price || !form.renewalDate) {
      wx.showToast({ title: '请补全必填信息', icon: 'none' });
      return;
    }

    const payload = {
      ...form,
      price: Number(form.price)
    };

    if (Number.isNaN(payload.price) || payload.price <= 0) {
      wx.showToast({ title: '价格需大于0', icon: 'none' });
      return;
    }

    const next = upsertRecord([...this.data.rawRecords], payload);
    saveRecords(next);

    wx.showToast({ title: '已保存', icon: 'success' });
    this.setData({ rawRecords: next, showForm: false });
    this.applyFilter();
  },

  onDelete(e) {
    const { id } = e.currentTarget.dataset;

    wx.showModal({
      title: '删除确认',
      content: '确认删除这条订阅吗？',
      success: (res) => {
        if (!res.confirm) return;

        const next = removeRecord(this.data.rawRecords, id);
        saveRecords(next);

        wx.showToast({ title: '已删除', icon: 'success' });
        this.setData({ rawRecords: next });
        this.applyFilter();
      }
    });
  }
});
