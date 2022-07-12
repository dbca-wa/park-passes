<template>
    <div v-if="cartItem.hasOwnProperty('voucher_number')" class="accordion-item">
        <h2 class="accordion-header" id="headingOne">
            <button class="accordion-button checkout-item-btn" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                <span class="item-type">Park Pass Voucher: {{cartItem.voucher_number}}</span> <span class="item-amount">${{cartItem.amount}}</span>
            </button>
        </h2>
        <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
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
        formatDate(dateString) {
            console.log(dateString)
            const date = new Date(dateString);
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                // Then specify how you want your dates to be formatted
            return date.toLocaleDateString('en-AU', options);
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
