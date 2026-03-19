const defaultData = require('../../data/subscriptions');
const { calcDashboard, loadRecords } = require('../../utils/subscription');

Page({
  data: {
    stats: {
      totalMonthly: 0,
      totalYearly: 0,
      cancelSavingYearly: 0,
      activeCount: 0,
      pendingCancelCount: 0,
      lowUsageCount: 0,
      topCostList: []
    }
  },

  onShow() {
    const records = loadRecords(defaultData);
    this.setData({
      stats: calcDashboard(records)
    });
  }
});
