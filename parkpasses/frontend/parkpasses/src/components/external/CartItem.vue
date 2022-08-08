<template>
    <div v-if="cartItem.hasOwnProperty('voucher_number')" class="accordion-item g-2">
        <h2 class="accordion-header" :id="$.vnode.key">
            <button class="accordion-button checkout-item-btn" type="button" data-bs-toggle="collapse" :data-bs-target="'#collapse' + $.vnode.key" aria-expanded="true" :aria-controls="'collapse' + $.vnode.key">
                <span class="item-type">Park Pass Voucher: {{cartItem.voucher_number}}</span> <span class="item-amount">${{cartItem.amount}}</span>
            </button>
        </h2>
        <div id="collapseOne" class="accordion-collapse collapse show" :aria-labelledby="$.vnode.key">
            <div class="accordion-body">
                <table class="table">
                    <tr><th>Voucher Code</th><td>{{cartItem.code}}</td></tr>
                    <tr><th>Recipient Name</th><td>{{cartItem.recipient_name}}</td></tr>
                    <tr><th>Recipient Email</th><td>{{cartItem.recipient_email}}</td></tr>
                    <tr><th>Date to Email</th><td>{{formatDate(cartItem.datetime_to_email)}}</td></tr>
                    <tr><th>Personal Message</th><td>{{cartItem.personal_message}}</td></tr>
                    <tr><th>Your First Name</th><td>{{cartItem.purchaser.first_name}}</td></tr>
                    <tr><th>Your Last Name</th><td>{{cartItem.purchaser.last_name}}</td></tr>
                    <tr><th>Your Email</th><td>{{cartItem.purchaser.email}}</td></tr>
                    <tr><th>Amount</th><td>${{cartItem.amount}}</td></tr>
                </table>
            </div>
        </div>
    </div>
    <div v-if="cartItem.hasOwnProperty('pass_number')" class="accordion-item">
        <h2 class="accordion-header" :id="$.vnode.key">
            <button class="accordion-button checkout-item-btn" type="button" data-bs-toggle="collapse" :data-bs-target="'#collapse' + $.vnode.key" aria-expanded="true" :aria-controls="'collapse' + $.vnode.key">
                <span class="item-type">Park Pass: {{cartItem.pass_number}}</span> <span class="item-amount">${{cartItem.price}}</span>
            </button>
        </h2>
        <div :id="'collapse' + $.vnode.key" class="accordion-collapse collapse show" :aria-labelledby="$.vnode.key">
            <div class="accordion-body">
                <table class="table">
                    <tr><th>Pass Type</th><td>{{cartItem.pass_type}}</td></tr>
                    <tr><th>Duration</th><td>{{cartItem.duration}}</td></tr>
                    <tr><th>Pass Start Date</th><td>{{formatDate(cartItem.datetime_start)}}</td></tr>
                    <tr><th>Pass Expiry Date</th><td>{{formatDate(cartItem.datetime_expiry)}}</td></tr>
                    <tr v-if="cartItem.vehicle_registration_1"><th>Vehicle Registraion <span v-if="cartItem.vehicle_registration_2">1</span></th><td>{{cartItem.vehicle_registration_1}}</td></tr>
                    <tr v-if="cartItem.vehicle_registration_2"><th>Vehicle Registraion <span v-if="cartItem.vehicle_registration_1">2</span></th><td>{{cartItem.vehicle_registration_2}}</td></tr>
                    <tr><th>Your First Name</th><td>{{cartItem.first_name}}</td></tr>
                    <tr><th>Your Last Name</th><td>{{cartItem.last_name}}</td></tr>
                    <tr><th>Your Email</th><td>{{cartItem.email}}</td></tr>
                    <tr><th>Price</th><td>${{cartItem.price}}</td></tr>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks'

export default {
    name: "CartItem",
    props: {
        cartItem: {},
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
        formatDate(dateString) {
            const date = new Date(dateString);
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                // Then specify how you want your dates to be formatted
            return date.toLocaleDateString('en-AU', options);
        },
    },
    created: function () {

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
