<template>
    <div class="container" id="cart">
        <div class="row mx-4">
            <div class="col">
                <h1>Cart</h1>
            </div>
        </div>
        <div class="row mx-4">

            <div class="col">

                <div v-if="cartItems">
                    <div class="accordion" id="checkoutAccordion">
                        <template v-if="cartItems && cartItems.length">
                            <CartItem v-for="cartItem in cartItems" @deleteCartItem="deleteCartItem"
                                :cartItem="cartItem" :key="cartItem.id" />

                            <div>
                                <div class="row my-3 mx-1 g-0">
                                    <div class="col border-bottom">
                                        GST
                                    </div>
                                    <div class="col-md-auto border-bottom">
                                        ${{ gst }}
                                    </div>
                                </div>
                                <div class="row my-3 mx-1 g-0">
                                    <div class="col border-bottom">
                                        Sub Total for {{ cartItems.length }} Item<template v-if="cartItems.length>1">s</template>  (Inc GST)
                                    </div>
                                    <div class="col-md-auto border-bottom">
                                        ${{ totalPrice }}
                                    </div>
                                </div>
                                <div class="d-flex flex-row-reverse">
                                    <div class="col-auto align-right">
                                        <button v-if="!isRedirecting" @click="checkoutCart" class="btn licensing-btn-primary px-5" type="button">Checkout</button>
                                        <BootstrapButtonSpinner v-else class="btn licensing-btn-primary px-5" />
                                    </div>
                                </div>
                            </div>

                        </template>
                        <template v-else>
                            <div class="card mb-1">
                                <div class="card-header checkout-item-header">
                                    There are no items in your cart.
                                </div>
                            </div>
                        </template>
                    </div>
                </div>

                <div v-else>
                    <BootstrapSpinner isLoading="true" />
                </div>

                <div v-if="systemErrorMessage" class="alert alert-danger" role="alert">
                    {{ systemErrorMessage }}
                </div>

            </div>
        </div>
    </div>
</template>

<script>
import { apiEndpoints, helpers } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'
import BootstrapButtonSpinner from '@/utils/vue/BootstrapButtonSpinner.vue'
import currency from 'currency.js'
import CartItem from '@/components/external/CartItem.vue'

export default {
    name: "Cart",
    data: function () {
        return {
            cartItems: null,
            loading: false,
            isRedirecting: false,
            systemErrorMessage: null,
        };
    },
    components: {
        apiEndpoints,
        helpers,
        CartItem,
        BootstrapSpinner,
        BootstrapButtonSpinner,
    },
    computed: {
        totalPrice() {
            if(this.cartItems){
                if (0 == this.cartItems.length) {
                    return 0.00;
                } else if (1 == this.cartItems.length) {
                    let price = 0.00;
                    if (this.cartItems[0].hasOwnProperty('voucher_number')) {
                        price = currency(this.cartItems[0].amount);
                    } else {
                        price = currency(this.cartItems[0].price_after_voucher_applied);
                    }
                    console.log('price = ' + price);
                    console.log('Math.max(price, 0.00) = ' + Math.max(price, 0.00));
                    if(0.00 >= Math.max(price, 0.00)){
                        return Math.max(price, 0.00).toFixed(2);
                    }
                    return Math.max(price, 0.00).toFixed(2);
                } else {
                    let total = currency(0.00);
                    this.cartItems.forEach(function (cartItem, index) {
                        if (cartItem.hasOwnProperty('voucher_number')) {
                            total = currency(total).add(cartItem.amount);
                        } else {
                            console.log('cartItem.price_after_voucher_applied = ' + cartItem.price_after_voucher_applied);
                            total = currency(total).add(cartItem.price_after_voucher_applied);
                        }
                        console.log('total = ' + total);
                        if(0.00 >= total){
                            return currency(0.00);
                        }
                    });
                    return total;
                }
            }
        },
        gst() {
            let gst = this.totalPrice / 10;
            console.log(gst);
            return Math.max(gst, 0.00).toFixed(2);
        }
    },
    methods: {
        checkoutCart: function () {
            this.isRedirecting = true;
            window.location.href = '/ledger-checkout/';
        },
        fetchCartItems: function () {
            let vm = this;
            vm.loading = true;
            fetch(apiEndpoints.cart)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        console.log(error);
                        return Promise.reject(error);
                    }
                    vm.cartItems = data
                    $("#cart-item-count").text(` ${vm.cartItems.length} `)
                })
                .catch(error => {
                    vm.systemErrorMessage = "ERROR: Please try again in an hour.";
                    console.error("There was an error!", error);
                }).finally(() => {
                    vm.loading = false;
                });
        },
        deleteCartItem: function (cart_item_id) {
            console.log("deleteCartItem = " + cart_item_id);
            this.cartItems.splice(this.cartItems.findIndex(cartItem => cartItem.cart_item_id === cart_item_id), 1);

            if ($("#cart-item-count").text().trim() > 0) {
                $("#cart-item-count").text($("#cart-item-count").text() - 1)
            }
        }
    },
    created: function () {
        this.fetchCartItems();
    },
    mounted: function () {

    }
};
</script>

<style scoped>
</style>
