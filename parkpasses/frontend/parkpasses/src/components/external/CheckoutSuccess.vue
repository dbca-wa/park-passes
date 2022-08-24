<template>
    <div class="container" id="shopHome">
        <div class="row ms-4 mb-3">
            <div class="col">
                <h1>Checkout Success</h1>
            </div>
        </div>
        <div class="row ms-4">
            <div class="col-md-3">
                <div class="card">
                    <h5 class="card-header">Side menu</h5>
                    <div class="card-body">
                        <h5 class="card-title">Special title treatment</h5>
                        <p class="card-text">With supporting text below as a natural lead-in to additional content.</p>
                        <a href="#" class="btn btn-primary">Go somewhere</a>
                    </div>
                </div>
            </div>

            <div class="col-md-8">

                <div v-if="order" class="card bg-white">
                    <div class="card-header checkout-success-item-header">
                        <span>Order Placed</span>
                        <span>{{ formattedOrderDate }}</span>

                        <span>Items</span>
                        <span>{{ order.items.length }}</span>

                        <span>Total</span>
                        <span>${{ order.total.toFixed(2) }}</span>

                        <span>ORDER # {{ order.order_number }}</span>
                        <span><a href="#">View Invoice</a></span>

                    </div>
                    <div class="card-body">

                        <div v-for="orderItem in order.items" class="card bg-white mb-3">
                            <div class="card-header order-item">
                                <span>{{ orderItem.description }}</span>
                                <span>${{ orderItem.amount }}</span>
                            </div>
                        </div>

                    </div>
                </div>

            </div>

        </div>
    </div>

</template>

<script>
import { apiEndpoints, helpers } from '@/utils/hooks'
import Loader from '@/utils/vue/Loader.vue'

export default {
    name: "CheckoutSuccess",
    data: function () {
        return {
            orderUUID: null,
            order: null,
            formattedOrderDate: null,
        };
    },
    components: {
        Loader
    },
    methods: {
        fetchOrder: function (uuid) {
            let vm = this;
            vm.loading = true;
            fetch(apiEndpoints.orderRetrieveExternal(uuid))
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        console.log(error);
                        return Promise.reject(error);
                    }
                    // Do something after adding the voucher to the database and the users cart
                    vm.formattedOrderDate = helpers.getPrettyDateFromDatetime(data.datetime_created)
                    vm.order = Object.assign({}, data);
                    console.log(vm.order)
                })
                .catch(error => {
                    vm.systemErrorMessage = "ERROR: Please try again in an hour.";
                    console.error("There was an error!", error);
                }).finally(() => {
                    vm.loading = false;
                });
        },
    },
    created: function() {
        this.orderUUID = this.$route.params.uuid;
        this.fetchOrder(this.orderUUID);
    }
};
</script>

<style scoped>
    .checkout-success-item-header {
        /* create a grid */
        display: grid;

        /* create colums. 1fr means use available space */
        grid-template-rows: 1fr 1fr;
        grid-template-columns: max-content max-content 1fr max-content;
         grid-auto-flow: column;
        align-items: center;
        justify-content: center;
        grid-gap: 2px 30px;
        color: #565959;
        font-size:12px;
    }

    .order-item {
        display: grid;
        grid-template-columns: 21fr max-content;
    }

</style>
