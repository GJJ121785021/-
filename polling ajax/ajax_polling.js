new Vue({
    el: '#polling',
    data: {
        num: null
    },
    mounted() {
        timer = window.setInterval(() => {
            setTimeout(this.polling_func, 0)
        }, 1000);
    },
    methods: {
        polling_func: function () {
            if (this.num && this.num < 0.2) {
                window.clearInterval(timer);
                alert('恭喜你中奖了');
            } else {
                axios
                    .get('/vue/api_polling/')
                    .then(response => this.num = response.data.num,
                        function (e) {
                            console.log(e)
                        });
            }
        }
    }
});

