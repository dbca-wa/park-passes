<template>

    <div v-if="cartItem.hasOwnProperty('voucher_number')" class="card mb-1" :id="cartItem.cart_item_id">
        <div class="card-header checkout-item-header">
            <span class="item-type">Park Pass Voucher</span>
            <a class="accordian-header-note text-secondary" data-bs-toggle="collapse" :href="'#collapse' + $.vnode.key" role="button" aria-expanded="false" :aria-controls="'collapse' + $.vnode.key">Click to show more details</a>
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
            <span class="item-type">{{cartItem.pass_type}}
                <span v-if="cartItem.park_group && cartItem.park_group.length">({{ cartItem.park_group }})</span>
                <span v-if="isHolidayPass(cartItem)">({{ cartItem.duration }})</span>
            </span>
            <a class="accordian-header-note text-secondary" data-bs-toggle="collapse" :href="'#collapse' + $.vnode.key" role="button" aria-expanded="false" :aria-controls="'collapse' + $.vnode.key">Click to show more details</a>
            <span class="item-amount">${{cartItem.price}}</span>
            <span class="delete-button"><i @click="deleteCartItem($event, cartItem.cart_item_id)" class="fa fa-trash org-primary" aria-hidden="true"></i></span>
        </div>

        <div :id="'collapse' + $.vnode.key" class="collapse" aria-labelledby="headingOne" data-parent="#checkoutAccordion">
            <div class="card-body">
                <table class="table table-sm">
                    <tr><th>Pass Type</th><td>{{cartItem.pass_type}}</td></tr>
                    <tr v-if="cartItem.park_group && cartItem.park_group.length"><th>Park Group</th><td>{{cartItem.park_group}}</td></tr>
                    <tr><th>Duration</th><td>{{cartItem.duration}}</td></tr>
                    <tr v-if="cartItem.renew_automatically"><th>Automatically Renew</th><td><i class="fa fa-check" style="color:green;" aria-hidden="true"></i></td></tr>
                    <tr><th>Pass Start Date</th><td>{{formatDate(cartItem.datetime_start)}}</td></tr>
                    <tr><th>Pass Expiry Date</th><td>{{formatDate(cartItem.datetime_expiry)}}</td></tr>
                    <tr v-if="cartItem.vehicle_registration_1"><th>Vehicle Registration <span v-if="cartItem.vehicle_registration_2">1</span></th><td>{{cartItem.vehicle_registration_1}}</td></tr>
                    <tr v-if="cartItem.vehicle_registration_2"><th>Vehicle Registration <span v-if="cartItem.vehicle_registration_1">2</span></th><td>{{cartItem.vehicle_registration_2}}</td></tr>
                    <tr><th>Your First Name</th><td>{{cartItem.first_name}}</td></tr>
                    <tr><th>Your Last Name</th><td>{{cartItem.last_name}}</td></tr>
                    <tr><th>Your Email</th><td>{{cartItem.email}}</td></tr>
                    <tr v-if="cartItem.postcode && cartItem.postcode.length"><th>Postcode</th><td>{{cartItem.postcode}}</td></tr>
                    <tr><th>Price</th><td>${{cartItem.price}}</td></tr>
                </table>
            </div>
        </div>

        <div v-if="cartItem.discount_code" class="row my-1 ps-3 pe-1 g-0 align-items-center discount-code-text">
            <div class="col text-secondary border-bottom">
                Discount Code Applied {{ cartItem.discount_code.code }}
                <span v-if="'percentage'==cartItem.discount_code.discount_type">({{ cartItem.discount_code.discount }}% OFF)</span>
            </div>
            <div class="col-md-auto text-success border-bottom">
                -${{ discountAmount(cartItem) }}
            </div>
        </div>
        <div v-if="cartItem.discount_code" class="row my-1 ps-3 pe-1 g-0 align-items-center discount-code-text">
            <div class="col text-secondary">
                Sub total
            </div>
            <div class="col-md-auto">
                ${{cartItem.price_after_discount_code_applied.toFixed(2)}}
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
        isHolidayPass(cartItem) {
            if(!cartItem){
                return false;
            }
            return ('HOLIDAY_PASS'==cartItem.pass_type_name ? true : false)
        },
        discountAmount(cartItem) {
            if(!cartItem){
                return 0.00;
            }
            if(!cartItem.discount_code){
                return 0.00;
            }
            console.log('discountAmount = ' + cartItem.discount_code.discount);
            if('percentage'==cartItem.discount_code.discount_type){
                const priceBeforeDiscount = cartItem.price;
                const discount = cartItem.discount_code.discount;
                const percentage = discount / 100;
                const price = priceBeforeDiscount * percentage;
                const amount = parseFloat(price).toFixed(2);
                //cartItem.price = priceBeforeDiscount - amount;
                return amount;
            } else {
                return parseFloat(cartItem.discount_code.discount).toFixed(2);
            }
        },
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

    .table tr {
        border-bottom:1px solid #efefef;
    }

    .discount-code-text{
        font-size:0.9em;
    }
</style>
