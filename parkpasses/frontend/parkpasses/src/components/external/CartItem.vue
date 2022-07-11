<template>
    <div v-if="cartItem.hasOwnProperty('voucher_number')" class="accordion-item">
        <h2 class="accordion-header" id="headingOne">
            <button class="accordion-button checkout-item-btn" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                <span class="item-type">Park Pass Voucher: {{cartItem.voucher_number}}</span> <span class="item-amount">${{cartItem.amount}}</span>
            </button>
        </h2>
        <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
            <div class="accordion-body">
                <table class="table table-sm">
                    <tr><th>Voucher Number</th><td>{{cartItem.voucher_number}}</td></tr>
                    <tr><th>Recipient Name</th><td>{{cartItem.recipient_name}}</td></tr>
                    <tr><th>Recipient Email</th><td>{{cartItem.voucher_number}}</td></tr>
                    <tr><th>Date to Email</th><td>{{cartItem.datetime_to_email.toLocaleString()}}</td></tr>
                    <tr><th>Your First Name</th><td>{{cartItem.first_name}}</td></tr>
                    <tr><th>Your Last Name</th><td>{{cartItem.last_name}}</td></tr>
                    <tr><th>Your Email</th><td>{{cartItem.purchaser_email}}</td></tr>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks'

export default {
    name: "Checkout",
    props: {
        cartItem: {}
    },
    data: function () {
        return {

        };
    },
    components: {
        api_endpoints,
        helpers
    },
    computed: {

    },
    methods: {
        functionName: function () {

        },
    },
    created: function () {
        console.log(this.cartItem)
    },
    mounted: function () {

    }
};
</script>

<style scoped>
    button.checkout-item-btn {
    /* create a grid */
    display: grid;
    /* create colums. 1fr means use available space */
    grid-template-columns: 1fr max-content max-content;
    align-items: center;
    grid-gap: 10px;
    }
</style>
