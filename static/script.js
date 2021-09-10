const str2Date = (unix_time) => (new Date(unix_time));
const secondsFromNow = (date) => Math.trunc((Date.now() - date) / 1000);
const update_signals = function() {  // signal 記録を Ajax で更新
  axios
    .get('/json/last_signal_ts')
    .then(response => {
      this.last_signal_ts = response.data;
      this.last_signal_ts.forEach((item, i) => {
        item.timestamp = str2Date(item.timestamp);
        item.past_seconds = secondsFromNow(item.timestamp);
      });
    })
    .catch(error => {
      console.log(error);
      this.errored = true;
    })
    .finally(() => this.loading = false);
};
const update_gpu_info = function() {  // gpu 記録を Ajax で更新
  axios
    .get('/json/last_gpu_info')
    .then(response => {
      this.last_gpu_info = response.data;
    })
    .catch(error => {
      console.log(error);
      this.errored = true;
    })
    .finally(() => this.loading = false);
};

// Vue Router
const hb_signals_component = {
  template: '#hb-signals',

  data: () => ({
    last_signal_ts: null,
    loading: true,
    errored: false,
    update_interval: null,
    ajax_interval: null,
  }),

  filters: {
    secondsDiff2Readable: (total_seconds) => {
      const days = Math.trunc(total_seconds / 86400);
      const hours = Math.trunc(total_seconds % 86400 / 3600);
      const minutes = Math.trunc(total_seconds % 3600 / 60);
      const seconds = Math.trunc(total_seconds % 60);

      let res = `${seconds}s`;
      if (minutes) res = `${minutes}m ` + res;
      if (hours) res = `${hours}h ` + res;
      if (days) res = `${days}day(s)`;  // 24時間以上は日数だけ表示
      return res;
    },
    date2readable: (date) =>
      `${date.getFullYear()}/${('0' + (date.getMonth() + 1)).slice(-2)}/${('0' + date.getDate()).slice(-2)} \
      ${('0' + date.getHours()).slice(-2)}:${('0' + date.getMinutes()).slice(-2)}:${('0' + date.getSeconds()).slice(-2)}`,
  },

  computed: {
    getPastSeconds: function() {
      return (function(idx) {
        return this.last_signal_ts[idx].past_seconds;
      }).bind(this);
    },
  },

  methods: {
    IsOver1Day: (seconds) => (seconds > 86400) ? 'warn' : '',
  },

  mounted() {
    setTimeout(update_signals.bind(this), 0);
    this.ajax_interval = setInterval(update_signals.bind(this), 300000);  // 5 minutes

    this.update_interval = setInterval((function() {  // 経過時間を1秒ごとに更新
      this.last_signal_ts.forEach((item, i) => {
        item.past_seconds = secondsFromNow(item.timestamp);
      });
      for (let i = 0; i < this.last_signal_ts.length; ++i) {
        this.$set(this.last_signal_ts, i, this.last_signal_ts[i]);
      };  // Vue に変更を検知させるため
    }).bind(this), 1000);
  },

  destroyed() {
    clearInterval(this.update_interval);
    clearInterval(this.ajax_interval);
  },
};

const gpgpus_info_component = {
  template: '#gpgpus-info',

  data: () => ({
    last_gpu_info: null,
    ajax_interval: null,
    loading: true,
    errored: false,
  }),

  mounted() {
    setTimeout(update_gpu_info.bind(this), 0);
    this.ajax_interval = setInterval(update_gpu_info.bind(this), 300000);  // 5 minutes
  },

  destroyed() {
    clearInterval(this.ajax_interval);
  },
};

const router = new VueRouter({
  routes: [
    {
      path: '/',
      component: hb_signals_component,
    },
    {
      path: '/gpgpus_info',
      component: gpgpus_info_component,
    },
    {
      path: '/whats_this',
      component: {
        template: '#whats-this',
      },
    },
  ],
});

// Vue.js
const vm = new Vue({
  el: '#vue_app',
  router: router,
});
