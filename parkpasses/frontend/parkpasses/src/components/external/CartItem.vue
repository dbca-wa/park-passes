<template>

    <div v-if="cartItem.hasOwnProperty('voucher_number')" class="card mb-1" :id="cartItem.cart_item_id">
        <div class="card-header checkout-item-header">
            <span class="item-type">Park Pass Voucher: {{cartItem.voucher_number}} </span>
            <a class="accordian-header-note text-secondary" data-bs-toggle="collapse" :href="'#collapse' + $.vnode.key" role="button" aria-expanded="false" :aria-controls="'collapse' + $.vnode.key">Click to show details</a>
            <span class="item-amount">${{cartItem.amount}}</span>
            <span class="delete-button"><i @click="deleteCartItem($event, cartItem.cart_item_id)" class="fa fa-trash org-primary" aria-hidden="true"></i></span>
        </div>

        <div :id="'collapse' + $.vnode.key" class="collapse" aria-labelledby="headingOne" data-parent="#checkoutAccordion">
            <div class="card-body">
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

    <div v-if="cartItem.hasOwnProperty('pass_number')" class="card mb-1" :id="cartItem.cart_item_id">
        <div class="card-header checkout-item-header">
            <span class="item-type">Park Pass: {{cartItem.pass_number}}</span>
            <a class="accordian-header-note text-secondary" data-bs-toggle="collapse" :href="'#collapse' + $.vnode.key" role="button" aria-expanded="false" :aria-controls="'collapse' + $.vnode.key">Click to show details</a>
            <span class="item-amount">${{cartItem.price}}</span>
            <span class="delete-button"><i @click="deleteCartItem($event, cartItem.cart_item_id)" class="fa fa-trash org-primary" aria-hidden="true"></i></span>
        </div>

        <div :id="'collapse' + $.vnode.key" class="collapse" aria-labelledby="headingOne" data-parent="#checkoutAccordion">
            <div class="card-body">
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
import { apiEndpoints, helpers } from '@/utils/hooks'

export default {
    name: "CartItem",
    props: {
        cartItem: {},
    },
    emits: ["deleteCartItem"],
    data: function () {
        return {

        };
    },
    components: {
        apiEndpoints,
        helpers
    },
    computed: {

    },
    methods: {
        formatDate(dateString) {
            const date = new Date(dateString);
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            return date.toLocaleDateString('en-AU', options);
        },
        deleteCartItem: function(event, cart_item_id) {
            event.preventDefault();
            event.stopPropagation();
            console.log('Deleting cart item with id = ' + cart_item_id);
            let vm = this;
            fetch(apiEndpoints.deleteCartItem(cart_item_id), {method: "DELETE"})
            .then(async response => {
                console.log('response = ' + JSON.stringify(response))
                $(`#${cart_item_id}`).fadeOut(400, function(){
                    $(this).remove();
                    vm.$emit("deleteCartItem", cart_item_id);
                });
            })
            .catch(error => {
                vm.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            }).finally(() => {
                vm.loading = false;
            });
        }
    },
    created: function () {

    },
    mounted: function () {

    }
};
</script>

<style scoped>
    .checkout-item-header {
        /* create a grid */
        display: grid;
        /* create colums. 1fr means use available space */
        grid-template-columns: max-content 1fr max-content max-content max-content;
         grid-auto-flow: column;
        align-items: center;
        justify-content: center;
        grid-gap: 10px;
    }

    .delete-button {
        cursor:pointer;
    }

    .accordian-header-note {
        font-size:0.9em;
        text-decoration:none;
    }
</style>
