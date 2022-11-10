<template>
    <div class="container p-0" id="cart">
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
                                    <div class="col-auto border-bottom">
                                        ${{ gst }}
                                    </div>
                                </div>
                                <div class="row my-3 mx-1 g-0">
                                    <div class="col border-bottom d-none d-sm-block">
                                        Sub Total for {{ cartItems.length }} Item<template v-if="cartItems.length>1">s</template>  (Inc GST)
                                    </div>
                                    <div class="col border-bottom float-end d-block d-sm-none">
                                        Total (Inc GST)
                                    </div>
                                    <div class="col-auto border-bottom">
                                        ${{ totalPrice }}
                                    </div>
                                </div>
                                <div v-if="isRetailer" class="row my-3 mx-1 g-0">
                                    <div class="col">
                                        <BootstrapAlert>
                                            <div class="mb-2">Please take payment from the customer and then click 'Create Pass'</div>
                                            <div>{{retailerGroupsForUser[0].name}} will be invoiced monthly for any sales minus commission.</div>
                                        </BootstrapAlert>
                                    </div>
                                </div>
                                <form ref="checkoutForm" action="/ledger-checkout/" method="post">
                                    <input type="hidden" name="csrfmiddlewaretoken" :value="csrftoken" />
                                    <div class="d-flex flex-row justify-content-end">
                                        <div v-if="isRetailer" class="me-2 d-flex align-items-center">
                                            <label class="d-inline">Sold Via: </label>
                                        </div>
                                        <div v-if="isRetailer" class="me-5 d-flex align-items-center">
                                            <template v-if="retailerGroupsForUser && retailerGroupsForUser.length>1">
                                                <select class="form-select" name="retailer_group_id">
                                                    <option v-for="retailerGroup in retailerGroupsForUser" :value="retailerGroup.id">{{ retailerGroup.name }}</option>
                                                </select>
                                            </template>
                                            <template v-else>
                                                <input type="hidden" name="retailer_group_id" :value="retailerGroupsForUser[0].id" />
                                                <span class="badge org-badge-primary">{{ retailerGroupsForUser[0].name }}</span>
                                            </template>
                                        </div>
                                        <div>
                                            <div v-if="isRetailer">
                                                <input id="isNoPayment" type="hidden" name="no_payment" value="true" />

                                                <button v-if="!isRedirecting" @click="checkoutCart" class="btn licensing-btn-primary px-5 me-2" type="submit">Create Pass</button>
                                                <BootstrapButtonSpinner v-if="isRedirecting" class="btn licensing-btn-primary px-5" />
                                            </div>
                                            <div v-else class="col-auto align-right">
                                                <button v-if="!isRedirecting" @click="checkoutCart" class="btn licensing-btn-primary px-5" type="button">Checkout</button>
                                                <BootstrapButtonSpinner v-if="isRedirecting" class="btn licensing-btn-primary px-5" />
                                            </div>

                                        </div>
                                    </div>
                                </form>

                            </div>

                        </template>
                        <template v-else>
                            <div class="no-passes mb-4 col-12">
                                <div class="no-items">
                                    There are no items in your cart.
                                </div>
                            </div>
                        </template>
                    </div>
                </div>

                <div v-else>
                    <BootstrapSpinner :isLoading="true" />
                </div>

                <div v-if="systemErrorMessage" class="alert alert-danger" role="alert">
                    {{ systemErrorMessage }}
                </div>

            </div>
        </div>
    </div>
</template>

<script>
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import { useStore } from '@/stores/state'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'
import BootstrapButtonSpinner from '@/utils/vue/BootstrapButtonSpinner.vue'
import BootstrapAlert from '@/utils/vue/BootstrapAlert.vue'

import currency from 'currency.js'
import CartItem from '@/components/external/CartItem.vue'

export default {
    name: "Cart",
    data: function () {
        return {
            store: useStore(),
            cartItems: null,
            loading: false,
            isRetailer: false,
            retailerGroupsForUser: [],
            isRedirecting: false,
            csrftoken: helpers.getCookie('csrftoken'),
            systemErrorMessage: null,
        };
    },
    components: {
        apiEndpoints,
        helpers,
        CartItem,
        BootstrapSpinner,
        BootstrapButtonSpinner,
        BootstrapAlert,
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
                    });
                    console.log('total = ' + total);
                    if(0.00 >= total){
                        return currency(0.00);
                    }
                    return total;
                }
            }
        },
        gst() {
            let gst = currency(helpers.getGstFromTotalIncludingGst(constants.GST, this.totalPrice));
            console.log(gst);
            return Math.max(gst, 0.00).toFixed(2);
        }
    },
    methods: {
        checkoutCart: function (isCashPayment) {
            this.isRedirecting = true;
            if(isCashPayment){
                $('input#isNoPayment').val(true);
            }
            this.$refs.checkoutForm.submit();
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
                    vm.systemErrorMessage = constants.ERRORS.NETWORK;
                    console.error("There was an error!", error);
                }).finally(() => {
                    vm.loading = false;
                });
        },
        fetchRetailerGroupsForUser: function () {
            let vm = this;
            vm.loading = true;
            fetch(apiEndpoints.retailerGroupsForUser)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                vm.retailerGroupsForUser = data
                console.log(vm.retailerGroupsForUser);
            })
            .catch(error => {
                vm.systemErrorMessage = constants.ERRORS.NETWORK;
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
        let vm = this;
        if(vm.store.userData){
            if('retailer'==vm.store.userData.authorisation_level) {
                vm.isRetailer = true;
                vm.fetchRetailerGroupsForUser();
            }
            console.log('vm.isRetailer = ' + vm.isRetailer);
        }
        //$('').val(); csrfmiddlewaretoken
    }
};
</script>

<style scoped>
.card {
    background-color: #EDE5D9;
}
.no-items{
    background-color: #EDE5D9;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    border: 1px solid rgba(0, 0, 0, 0.125);
}
</style>
