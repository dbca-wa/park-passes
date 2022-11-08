<template>
    <div class="container" id="your-orders">

        <h2 class="pb-3">Your Orders</h2>

        <div v-if="orders" id="orders" class="orders row row-cols-1 row-cols-sm-1 row-cols-md-1 row-cols-lg-1 row-cols-xl-2 row-cols-xxl-2 g-4 pb-5">
            <div v-for="order in orders" class="order col-xs">
                <div class="card-header order-list-item-header">
                    <span class="heading">Order Placed</span>
                    <span class="d-none d-sm-block"> {{ formattedOrderDate(order.datetime_created) }} </span>
                    <span class="d-bloack d-sm-none"> formattedOrderDateShort </span>

                    <span class="heading">Items</span>
                    <span><a data-bs-toggle="collapse" :href="'#order'+order.id" role="button" aria-expanded="false" :aria-controls="'order'+order.id">{{ order.items.length }}</a></span>

                    <span class="heading">Total</span>
                    <span>${{ order.total.toFixed(2) }}</span>

                    <span class="heading">ORDER #{{ order.order_number }}</span>
                    <span><a :href="invoiceURL(order.id)" target="_blank">View Invoice</a></span>
                </div>
                <div class="card-body p-0">

                    <div :id="'order'+order.id" class="container p-0 pt-2 collapse">
                        <div v-for="orderItem in order.items" class="bg-white">
                            <div class="card-header order-item">
                                <span>{{ orderItem.description }}</span>
                                <span>${{ orderItem.amount }}</span>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>

        <div v-if="loading || loadingMore ">
            <BootstrapSpinner :isLoading="true" />
        </div>

        <div v-if="systemErrorMessage" class="alert alert-danger" role="alert">
            {{ systemErrorMessage }}
        </div>

    </div>
</template>

<script>
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'

export default {
    name: "YourOrders",
        data() {
        return {
            loading: false,
            loadingMore: false,
            orders: null,
            imagesLoaded: 0,
            pageIndex: 0,
            count: null,
            allImagesLoaded: false,
            systemErrorMessage: null,
        };
    },
    components: {
        BootstrapSpinner
    },
    computed: {
        allResultsLoaded() {
          return this.pageIndex * 30 >= this.count;
      }
    },
    methods: {
        invoiceURL: function(orderId) {
            return apiEndpoints.externalOrderInvoice(orderId);
        },
        formattedOrderDate: function (datetime) {
            return helpers.getPrettyDateFromDatetime(datetime)
        },
        fetchOrders: function () {
            let vm = this;
            vm.pageIndex++;
            if(!vm.orders){
                vm.loading = true;
            }
            fetch(apiEndpoints.ordersListExternal + '?page=' + vm.pageIndex)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                if(vm.orders && vm.orders.length>0){
                    vm.orders.push(...data.results)
                } else {
                    vm.orders = data.results
                }
                vm.count = data.count

                // Load more passes if there are no enough to fill the screen.
                var hasVScroll = document.body.scrollHeight > document.body.clientHeight;
                var cStyle = document.body.currentStyle||window.getComputedStyle(document.body, "");
                hasVScroll = cStyle.overflow == "visible"
                            || cStyle.overflowY == "visible"
                            || (hasVScroll && cStyle.overflow == "auto")
                            || (hasVScroll && cStyle.overflowY == "auto");
                if(!hasVScroll && !vm.allResultsLoaded){
                    this.fetchPasses();
                }

                vm.loading = false;
                vm.loadingMore = false;
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
    },
    created: function () {
        this.fetchOrders();
    },
    mounted: function () {
        let vm = this;
        window.onscroll = async function(ev) {
            if(!vm.loadingMore && !vm.allResultsLoaded) {
                let element = document.getElementById('orders');
                if (element.getBoundingClientRect().bottom < window.innerHeight) {
                    vm.loadingMore = true;
                    await vm.fetchOrders();
                }
            }
        };
    }
};
</script>

<style lang="css" scoped>
    .order-list-item-header {
        /* create a grid */
        display: grid;

        /* create colums. 1fr means use available space */
        grid-template-rows: 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
        grid-template-columns: max-content;
        grid-auto-flow: column;
        align-items: center;
        justify-content: center;
        grid-gap: 2px 3px;
        color: #565959;
        background-color: #EDE5D9;
        font-size:12px;
    }

    .order-list-item-header .heading{
        font-weight: bold;
    }


    .order-item {
        display: grid;
        grid-template-columns: 21fr max-content;
        font-size: 0.8em;
        margin-bottom: 4px;
    }

    @media (min-width: 425px) {
        .order-list-item-header {
            grid-template-rows: 1fr 1fr 1fr 1fr;
            grid-template-columns: 1fr 1fr;
        }


        .order-item {
            font-size:0.8em;
        }
    }

    @media (min-width: 768px) {
        .order-list-item-header {
            /* create a grid */
            display: grid;

            /* create colums. 1fr means use available space */
            grid-template-rows: 1fr 1fr;
            grid-template-columns: 2fr 0.5fr 0.5fr 1.5fr;
            grid-auto-flow: column;
            align-items: center;
            justify-content: center;
            grid-gap: 2px 14px;
            color: #565959;
            font-size:12px;
        }

        .order-list-item-header .heading{
            font-weight: bold;
        }

        .order-item {
            font-size:0.9em;
        }
    }

    @media (min-width: 1024px) {
        .order-list-item-header {
            grid-gap: 2px 30px;
        }
    }
</style>
