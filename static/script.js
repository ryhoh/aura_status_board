const str2Date = (unix_time) => (new Date(unix_time));
const secondsFromNow = (date) => Math.trunc((Date.now() - date) / 1000);

const getSignals = function() {  // signal 記録を Ajax で更新
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

const updateReturnMessage = function(device_name, return_message, access_token) {
  const params = new URLSearchParams();
  params.append('name', device_name);
  params.append('return_message', return_message);

  axios
    .post('/api/return_message', params, {
      'headers': { 'Authorization': 'Bearer ' + access_token }
    })
    .catch(error => {
      console.error(error);
    })
    .finally(() => {});
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
  },

  computed: {
    getPastSeconds: function() {
      return (function(idx) {
        return this.last_signal_ts[idx].past_seconds;
      }).bind(this);
    },
  },

  methods: {
    isOver1Day: (seconds) => (seconds > 86400) ? 'warn' : '',
  },

  mounted() {
    setTimeout(getSignals.bind(this), 0);
    this.ajax_interval = setInterval(getSignals.bind(this), 300000);  // 5 minutes

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

const reportComponent = {
  template: '#reports',

  data: () => ({
    last_signal_ts: null,
    ajax_interval: null,
    loading: true,
    errored: false,
  }),

  mounted() {
    setTimeout(getSignals.bind(this), 0);
    this.ajax_interval = setInterval(getSignals.bind(this), 300000);  // 5 minutes
  },

  destroyed() {
    clearInterval(this.ajax_interval);
  },
};

const returnMessageComponent = {
  template: '#return-message',

  data: () => ({
    last_signal_ts: null,
    loading: true,
    errored: false,
    editing_device_idx: null,
    editing_text_area: null,
  }),

  methods: {
    toggleReturnMsgEditor: function (device_idx) {
      cur_device_name = this.last_signal_ts[device_idx].device_name;
      cur_return_message = this.last_signal_ts[device_idx].return_message;
      if (this.editing_device_idx === null) {  // まだどれも編集していないなら
        this.editing_device_idx = device_idx;
        this.editing_text_area = cur_return_message;
        return;
      }
      if (this.editing_device_idx === device_idx) {  // 編集していたものを閉じようとしているなら
        this.editing_device_idx = null;
        if (this.editing_text_area !== cur_return_message) {  // 変わった場合、ajax で API に POST
          this.last_signal_ts[device_idx].return_message = this.editing_text_area;
          updateReturnMessage(cur_device_name, this.editing_text_area, vm.token.access_token);
        }
        return;
      }
      // 編集していたものを閉じて違うものを編集するなら
      if (this.editing_text_area !== cur_return_message) {  // 変わった場合、ajax で API に POST
        this.last_signal_ts[this.editing_device_idx].return_message = this.editing_text_area;
        updateReturnMessage(
          this.last_signal_ts[this.editing_device_idx].device_name,
          this.editing_text_area,
          vm.token.access_token
        );
      }
      this.editing_device_idx = device_idx;
      this.editing_text_area = cur_return_message;
    },
  },

  mounted() {
    setTimeout(getSignals.bind(this), 0);
  }
};

const deviceRegisterComponent = {
  template: '#device-register',

  data: () => ({
    new_device_name: null,
    error: null,
    loading: false,
    tried: false,
  }),

  methods: {
    registerDevice: function() {
      if (this.new_device_name === null || this.new_device_name.length < 3) {
        this.error = true;
        return;
      }

      this.loading = true;
      this.error = null;
      const params = new URLSearchParams();
      params.append('device_name', this.new_device_name);
      axios
        .post('/api/v2/register/device', params, {
          'headers': { 'Authorization': 'Bearer ' + vm.token.access_token }
        })
        .catch(error => {
          console.error(error);
          this.error = error;
        })
        .finally(() => {
          this.loading = false;
          this.tried = true;
        });
    }
  }
}


// Vue Router
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
      path: '/reports',
      component: reportComponent,
    },
    {
      path: '/return_message',
      component: {
        template: '#return-message',
        ...returnMessageComponent,
      },
    },
    {
      path: '/device_register',
      component: deviceRegisterComponent,
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
          // JWT の保管
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
    if (localStorage.length > 0) {  // LocalStorage になにかあるなら、JWT を復旧する
        if (localStorage.getItem('user_username')) this.user.username = localStorage.getItem('user_username');
        if (localStorage.getItem('token_access_token')) this.token.access_token = localStorage.getItem('token_access_token');
        if (localStorage.getItem('token_token_type')) this.token.token_type = localStorage.getItem('token_token_type');
    }
},

  router: router,
});
