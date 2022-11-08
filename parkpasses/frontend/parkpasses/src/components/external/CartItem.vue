
<script setup>
import { breakpointsBootstrapV5, useBreakpoints } from '@vueuse/core'

const breakpoints = useBreakpoints(breakpointsBootstrapV5);
const notMobile = breakpoints.greaterOrEqual('sm');
</script>

<template>

    <div v-if="cartItem.hasOwnProperty('voucher_number')" class="card mb-1" :id="cartItem.cart_item_id">
        <div class="card-header checkout-item-header">
            <span class="item-type"><template v-if="notMobile">Park Pass </template>Voucher</span>
            <a class="accordian-header-note text-secondary d-none d-sm-block" data-bs-toggle="collapse" :href="'#collapse' + $.vnode.key" role="button" aria-expanded="false" :aria-controls="'collapse' + $.vnode.key">Click to show more details</a>
            <a class="accordian-header-note text-secondary d-block d-sm-none" data-bs-toggle="collapse" :href="'#collapse' + $.vnode.key" role="button" aria-expanded="false" :aria-controls="'collapse' + $.vnode.key">More...</a>
            <span class="item-amount">${{cartItem.amount}}</span>
            <span class="delete-button"><i @click="deleteCartItem($event, cartItem.cart_item_id)" class="fa fa-trash org-primary" aria-hidden="true"></i></span>
        </div>

        <div :id="'collapse' + $.vnode.key" class="collapse" aria-labelledby="headingOne" data-parent="#checkoutAccordion">
            <div class="card-body">
                <div class="container">
                    <div class="row">
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Voucher Code</div><div class="col-12 col-sm-6 border-bottom">{{cartItem.code}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Recipient Name</div><div class="col-12 col-sm-6 border-bottom">{{cartItem.recipient_name}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Recipient Email</div><div class="col-12 col-sm-6 border-bottom">{{cartItem.recipient_email}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Date to Email</div><div class="col-12 col-sm-6 border-bottom">{{formatDate(cartItem.datetime_to_email)}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Personal Message</div><div class="col-12 col-sm-6 border-bottom">{{cartItem.personal_message}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Your First Name</div><div class="col-12 col-sm-6 border-bottom">{{cartItem.purchaser.first_name}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Your Last Name</div><div class="col-12 col-sm-6 border-bottom">{{cartItem.purchaser.last_name}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Your Email</div><div class="col-12 col-sm-6 border-bottom">{{cartItem.purchaser.email}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Amount</div><div class="col-12 col-sm-6 border-bottom">${{cartItem.amount}}</div>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <div v-if="cartItem.hasOwnProperty('pass_number')" class="card mb-1" :id="cartItem.cart_item_id">
        <div class="card-header checkout-item-header">
            <span class="item-type d-none d-sm-block">
                {{cartItem.pass_type}}
                <span v-if="cartItem.park_group && cartItem.park_group.length">({{ cartItem.park_group }})</span>
                <span v-if="isHolidayPass(cartItem)">({{ cartItem.duration }})</span>
            </span>
            <span class="item-type d-block d-sm-none">Pass</span>
            <a class="accordian-header-note text-white d-none d-sm-block" data-bs-toggle="collapse" :href="'#collapse' + $.vnode.key" role="button" aria-expanded="false" :aria-controls="'collapse' + $.vnode.key">Click to show more details</a>
            <a class="accordian-header-note text-white d-block d-sm-none" data-bs-toggle="collapse" :href="'#collapse' + $.vnode.key" role="button" aria-expanded="false" :aria-controls="'collapse' + $.vnode.key">More...</a>

            <span class="item-amount">${{cartItem.price}}</span>
            <span class="delete-button"><i @click="deleteCartItem($event, cartItem.cart_item_id)" class="fa fa-trash" aria-hidden="true"></i></span>
        </div>

        <div :id="'collapse' + $.vnode.key" class="collapse" aria-labelledby="headingOne" data-parent="#checkoutAccordion">
            <div class="card-body">

                <div class="container">
                    <div class="row">
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Pass Type</div><div class="col-12 col-sm-6 border-bottom">{{cartItem.pass_type}}</div>
                        <div v-if="cartItem.park_group" class="col-12 col-sm-6 fw-bold border-bottom">Park Group</div><div v-if="cartItem.park_group" class="col-12 col-sm-6 border-bottom">{{cartItem.park_group}}</div>
                        <div v-if="cartItem.duration" class="col-12 col-sm-6 fw-bold border-bottom">Duration</div><div v-if="cartItem.duration" class="col-12 col-sm-6 border-bottom">{{cartItem.duration}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Pass Start Date</div><div class="col-12 col-sm-6 border-bottom">{{formatDate(cartItem.date_start)}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Pass Expiry Date</div><div class="col-12 col-sm-6 border-bottom">{{formatDate(cartItem.date_expiry)}}</div>
                        <div v-if="cartItem.renew_automatically" class="col-12 col-sm-6 fw-bold border-bottom">Renew Automatically</div><div v-if="cartItem.renew_automatically" class="col-12 col-sm-6 border-bottom"><i class="fa fa-check" style="color:green;" aria-hidden="true"></i></div>
                        <div v-if="cartItem.vehicle_registration_1" class="col-12 col-sm-6 fw-bold border-bottom">Vehicle Registration <span v-if="cartItem.vehicle_registration_2">1</span></div><div v-if="cartItem.vehicle_registration_1" class="col-12 col-sm-6 border-bottom">{{cartItem.vehicle_registration_1}}</div>
                        <div v-if="cartItem.vehicle_registration_2" class="col-12 col-sm-6 fw-bold border-bottom">Vehicle Registration <span v-if="cartItem.vehicle_registration_1">2</span></div><div v-if="cartItem.vehicle_registration_2" class="col-12 col-sm-6 border-bottom">{{cartItem.vehicle_registration_2}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Your First Name</div><div class="col-12 col-sm-6 border-bottom">{{cartItem.first_name}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Your Last Name</div><div class="col-12 col-sm-6 border-bottom">{{cartItem.last_name}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Your Email</div><div class="col-12 col-sm-6 border-bottom">{{cartItem.email}}</div>
                        <div v-if="cartItem.mobile" class="col-12 col-sm-6 fw-bold border-bottom">Mobile</div><div v-if="cartItem.mobile" class="col-12 col-sm-6 border-bottom">{{cartItem.mobile}}</div>
                        <div v-if="cartItem.company" class="col-12 col-sm-6 fw-bold border-bottom">Company</div><div v-if="cartItem.company" class="col-12 col-sm-6 border-bottom">{{cartItem.company}}</div>
                        <div v-if="cartItem.address_line_1" class="col-12 col-sm-6 fw-bold border-bottom">Address Line 1</div><div v-if="cartItem.address_line_1" class="col-12 col-sm-6 border-bottom">{{cartItem.address_line_1}}</div>
                        <div v-if="cartItem.address_line_2" class="col-12 col-sm-6 fw-bold border-bottom">Address Line 2</div><div v-if="cartItem.address_line_2" class="col-12 col-sm-6 border-bottom">{{cartItem.address_line_2}}</div>
                        <div v-if="cartItem.suburb" class="col-12 col-sm-6 fw-bold border-bottom">suburb</div><div v-if="cartItem.suburb" class="col-12 col-sm-6 border-bottom">{{cartItem.suburb}}</div>
                        <div v-if="cartItem.state" class="col-12 col-sm-6 fw-bold border-bottom">state</div><div v-if="cartItem.state" class="col-12 col-sm-6 border-bottom">{{cartItem.state}}</div>
                        <div v-if="cartItem.postcode" class="col-12 col-sm-6 fw-bold border-bottom">Postcode</div><div v-if="cartItem.postcode" class="col-12 col-sm-6 border-bottom">{{cartItem.postcode}}</div>
                        <div class="col-12 col-sm-6 fw-bold border-bottom">Price</div><div class="col-12 col-sm-6 border-bottom">${{cartItem.price}}</div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="cartItem.concession" class="row my-1 ps-3 pe-1 g-0 align-items-center discount-code-text">
            <div class="col text-secondary border-bottom">
                <template v-if="notMobile">Concession Applied: </template>{{ cartItem.concession.concession_type }}
                <span>({{ cartItem.concession.discount_percentage }}% OFF)</span>
            </div>
            <div class="col col-auto text-success border-bottom">
                -${{ concessionAmount }}
            </div>
        </div>

        <div v-if="cartItem.discount_code" class="row my-1 ps-3 pe-1 g-0 align-items-center discount-code-text">
            <div class="col text-secondary border-bottom">
                Discount Code Applied: {{ cartItem.discount_code.code }}
                <span v-if="'percentage'==cartItem.discount_code.discount_type">({{ cartItem.discount_code.discount }}% OFF)</span>
                <span v-else>(${{ cartItem.discount_code.discount }} OFF)</span>
            </div>
            <div class="col-auto text-success border-bottom">
                -${{ discountAmount }}
            </div>
        </div>

        <div v-if="cartItem.voucher" class="row my-1 ps-3 pe-1 g-0 align-items-center discount-code-text">
            <div class="col text-secondary border-bottom">
                Voucher Redemption: {{ cartItem.voucher.code }}
                (If you proceed with this transaction your voucher will have a balance of ${{ cartItem.voucher.remaining_balance }} remaining)
            </div>
            <div class="col-auto text-success border-bottom">
                -${{ voucherTransactionAmount }}
            </div>
        </div>

        <div v-if="showSubTotal" class="row my-1 ps-3 pe-1 g-0 align-items-center discount-code-text">
            <div class="col text-secondary">
                Sub total
            </div>
            <div class="col-auto">
                ${{ subTotal }}
            </div>
        </div>

    </div>

</template>


<script>
import { apiEndpoints, helpers, constants } from '@/utils/hooks'
import currency from 'currency.js'
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
        priceAfterDiscountCodeApplied() {
            return Math.max(this.cartItem.price_after_discount_code_applied, 0.00).toFixed(2);
        },
        subTotal() {
            return Math.max(this.cartItem.price_after_voucher_applied, 0.00).toFixed(2);
        },
        showSubTotal() {
            if(null!==this.cartItem.concession){return true}
            if(null!==this.cartItem.discount_code){return true}
            if(null!==this.cartItem.voucher){return true}
            return false;
        },
        concessionAmount() {
            return currency(this.cartItem.price - this.cartItem.price_after_concession_applied);
        },
        discountAmount() {
            let cartItem = this.cartItem;
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
                return currency(price);
            } else {
                let discountAmount = currency(cartItem.discount_code.discount);
                if (discountAmount >= cartItem.price) {
                    return currency(cartItem.price);
                }
                return discountAmount;
            }
        },
        voucherTransactionAmount() {
            return currency(this.priceAfterDiscountCodeApplied - this.cartItem.price_after_voucher_applied);
        },
        projectedRemainingVoucherBalance() {
            if(!this.cartItem.voucher){
                return null;
            }
            if(0.00>=this.cartItem.voucher.remaining_balance){
                return 0.00
            }
            const projectedRemainingVoucherBalance = this.cartItem.voucher.remaining_balance - this.voucherTransactionAmount;
            return Math.max(projectedRemainingVoucherBalance, 0.00).toFixed(2);
        },
    },
    methods: {
        isHolidayPass(cartItem) {
            if(!cartItem){
                return false;
            }
            return (constants.HOLIDAY_PASS_NAME==cartItem.pass_type_name ? true : false)
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
                vm.systemErrorMessage = constants.ERRORS.NETWORK;
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

    div.cart-header span.item-type {
        font-size:0.2em;
    }
    .checkout-item-header {
        /* create a grid */
        display: grid;
        /* create colums. 1fr means use available space */
        grid-template-columns: 1fr 1fr max-content max-content;
         grid-auto-flow: column;
        align-items: center;
        justify-content: center;
        grid-gap: 10px;
        background-color: #003e52;
        color:#eee;
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

    .fa-trash {
        color:#eee;
    }

    .fa-trash:hover {
        color:red;
    }
</style>
