const str2Date = (unix_time) => (new Date(unix_time));
const secondsFromNow = (date) => Math.trunc((Date.now() - date) / 1000);

const updateSignals = function() {  // signal 記録を Ajax で更新
  axios
    .get('/json/signals')
    .then(response => {
      this.last_signal_ts = response.data;
      this.last_signal_ts.forEach((item, i) => {
        item.timestamp = str2Date(item.last_heartbeat_timestamp);
        item.past_seconds = secondsFromNow(item.timestamp);
      });
    })
    .catch(error => {
      console.error(error);
      this.errored = true;
    })
    .finally(() => this.loading = false);
};

const updateGpuInfo = function() {  // gpu 記録を Ajax で更新
  axios
    .get('/json/last_gpu_info')
    .then(response => {
      this.last_gpu_info = response.data;
    })
    .catch(error => {
      console.error(error);
      this.errored = true;
    })
    .finally(() => this.loading = false);
};

// Vue Router
const hbSignalsComponent = {
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
    date2readable: (date) => {
      if (date === null)
        return '-';
      return `${date.getFullYear()}/${('0' + (date.getMonth() + 1)).slice(-2)}/${('0' + date.getDate()).slice(-2)} \
        ${('0' + date.getHours()).slice(-2)}:${('0' + date.getMinutes()).slice(-2)}:${('0' + date.getSeconds()).slice(-2)}`;
    },
    arrangeReturnMessage: (message) => {
      if (message === null)
        return '# default';
      return message;
    },
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
    setTimeout(updateSignals.bind(this), 0);
    this.ajax_interval = setInterval(updateSignals.bind(this), 300000);  // 5 minutes

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

const gpgpusInfoComponent = {
  template: '#gpgpus-info',

  data: () => ({
    last_gpu_info: null,
    ajax_interval: null,
    loading: true,
    errored: false,
  }),

  mounted() {
    setTimeout(updateGpuInfo.bind(this), 0);
    this.ajax_interval = setInterval(updateGpuInfo.bind(this), 300000);  // 5 minutes
  },

  destroyed() {
    clearInterval(this.ajax_interval);
  },
};

const returnMessageComponent = {
  template: '#return-message',
}

const router = new VueRouter({
  routes: [
    {
      path: '/',
      component: {
        template: '#hb-signals',
        ...hbSignalsComponent,
      },
    },
    {
      path: '/gpgpus_info',
      component: gpgpusInfoComponent,
    },
    {
      path: '/return_message',
      component: {
        template: '#return-message',
        ...hbSignalsComponent,
      },
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

  data: () => ({
    token: {},
    user: {
      username: '',
      password: '',
    },
  }),

  methods: {
    loginProcedure: function() {
      this.token = {
        msg: 'Processing...',
        accessing: true,
      };

      const params = new URLSearchParams();
      params.append('username', this.user.username);
      params.append('password', this.user.password);

      axios
        .post('/api/token', params)
        .then(response => {
          this.token = response.data;
          localStorage.setItem('user_username', this.user.username);
          localStorage.setItem('token_access_token', this.token.access_token);
          localStorage.setItem('token_token_type', this.token.token_type);
        })
        .catch(error => {
          console.error(error);
          this.token = {
            msg: 'Login failed.',
            error: true,
          };
        });
    },
  },

  mounted() {
    if (localStorage.length > 0) {
        if (localStorage.getItem('user_username')) this.user.username = localStorage.getItem('user_username');
        if (localStorage.getItem('token_access_token')) this.token.access_token = localStorage.getItem('token_access_token');
        if (localStorage.getItem('token_token_type')) this.token.token_type = localStorage.getItem('token_token_type');
    }
},

  router: router,
});
