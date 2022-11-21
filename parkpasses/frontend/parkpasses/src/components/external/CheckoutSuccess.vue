<template>
    <div class="container" id="shopHome">
        <div class="row ms-4 mb-3">
            <div class="col">
                <h1>Checkout Success</h1>
            </div>
        </div>
        <div class="row ms-4 g-4 pe-3">

            <div v-if="isRetailer" class="col-md-3">
                <div class="card">
                    <h5 class="card-header">What Next?</h5>
                    <div class="card-body">
                        <p class="card-text"><a href="/retailer/sell-a-pass">Sell Another Pass</a></p>
                        <p class="card-text"><a href="/retailer/reports">View Invoices &amp Reports</a></p>
                        <p class="card-text"><a href="/">Return home</a></p>
                    </div>
                </div>
            </div>

            <div v-else class="col-md-3">
                <div class="card">
                    <h5 class="card-header text-white">What Next?</h5>
                    <div class="card-body">
                        <p class="card-text"><a href="/your-park-passes">View Your Park Passes</a></p>
                        <p class="card-text"><a href="/your-orders">View Your Orders</a></p>
                        <p class="card-text"><a href="/">Return home</a></p>
                    </div>
                </div>
            </div>

            <div class="col-md-8">

                <div v-if="order" class="card">
                    <div class="card-header checkout-success-item-header text-white">
                        <span class="heading">Order Placed</span>
                        <span class="d-none d-sm-block">{{ formattedOrderDate }}</span>
                        <span class="d-bloack d-sm-none">{{ formattedOrderDateShort }}</span>

                        <span class="heading">Items</span>
                        <span>{{ order.items.length }}</span>

                        <span class="heading">Total</span>
                        <span>${{ order.total.toFixed(2) }}</span>

                        <span class="heading">ORDER # {{ order.order_number }}</span>
                        <span><a :href="invoiceURL(order.id)" target="_blank">View Invoice</a></span>
                    </div>
                    <div class="card-body">

                        <div v-for="orderItem in order.items" class="mb-3">
                            <div class="card-header order-item">
                                <span>{{ orderItem.description }}</span>
                                <span>${{ orderItem.amount }}</span>
                            </div>
                        </div>

                        <BootstrapAlert>
                            You may check your email for further confirmation of purchase.
                        </BootstrapAlert>

                    </div>
                </div>

            </div>

        </div>
    </div>

</template>

<script>
import { useStore } from '@/stores/state'
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import BootstrapAlert from '@/utils/vue/BootstrapAlert.vue'

import DOMPurify from 'dompurify'

export default {
    name: "CheckoutSuccess",
    data: function () {
        return {
            store: useStore(),
            isRetailer: false,
            orderUUID: null,
            order: null,
            formattedOrderDate: null,
            formattedOrderDateShort: null,
        };
    },
    components: {
        BootstrapAlert
    },
    methods: {
        invoiceURL: function(orderId) {
            return apiEndpoints.externalOrderInvoice(orderId);
        },
        fetchOrder: function (uuid) {
            let vm = this;
            vm.loading = true;
            // deepcode ignore Ssrf: uuid is sanitized in the created method. Snyk is wrong.
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
                    vm.formattedOrderDateShort = helpers.getShortDate(data.datetime_created)
                    vm.order = Object.assign({}, data);
                    console.log(vm.order)
                })
                .catch(error => {
                    vm.systemErrorMessage = constants.ERRORS.NETWORK;
                    console.error("There was an error!", error);
                }).finally(() => {
                    vm.loading = false;
                });
        },
    },
    created: function() {
        this.orderUUID = DOMPurify.sanitize(this.$route.params.uuid);
        this.fetchOrder(this.orderUUID);
    },
    mounted: function() {
        let vm = this;
        if(vm.store.userData){
            if(vm.store.userData.is_authenticated && 'retailer'==vm.store.userData.authorisation_level) {
                vm.isRetailer = true;
            }
        }
    }
};
</script>

<style scoped>

    .card-header{
        background-color: #003e52;
    }
    .checkout-success-item-header {
        /* create a grid */
        display: grid;

        /* create colums. 1fr means use available space */
        grid-template-rows: 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
        grid-template-columns: max-content;
        grid-auto-flow: column;
        align-items: center;
        justify-content: center;
        grid-gap: 2px 3px;

        font-size:12px;
    }

    .checkout-success-item-header .heading{
        font-weight: bold;
    }

    .order-item {
        display: grid;
        grid-template-columns: 21fr max-content;
        font-size:0.8em;
        background-color: #EDE5D9;
    }

    @media (min-width: 425px) {
        .checkout-success-item-header {
            grid-template-rows: 1fr 1fr 1fr 1fr;
            grid-template-columns: 1fr 1fr;
        }


        .order-item {
            font-size:0.8em;
        }
    }

    @media (min-width: 768px) {
        .checkout-success-item-header {
            /* create a grid */
            display: grid;

            /* create colums. 1fr means use available space */
            grid-template-rows: 1fr 1fr;
            grid-template-columns: max-content max-content 1fr max-content;
            grid-auto-flow: column;
            align-items: center;
            justify-content: center;
            grid-gap: 2px 14px;
            color: #565959;
            font-size:12px;
        }

        .checkout-success-item-header .heading{
            font-weight: bold;
        }

        .order-item {
            font-size:0.9em;
        }
    }

    @media (min-width: 1024px) {
        .checkout-success-item-header {
            grid-gap: 2px 30px;
        }
    }

</style>
