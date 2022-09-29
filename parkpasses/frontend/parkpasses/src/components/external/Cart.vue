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
                                <div v-if="isRetailer" class="row my-3 mx-1 g-0">
                                    <div class="col">
                                        <svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
                                        <symbol id="check-circle-fill" fill="currentColor" viewBox="0 0 16 16">
                                            <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
                                        </symbol>
                                        <symbol id="info-fill" fill="currentColor" viewBox="0 0 16 16">
                                            <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/>
                                        </symbol>
                                        <symbol id="exclamation-triangle-fill" fill="currentColor" viewBox="0 0 16 16">
                                            <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                                        </symbol>
                                        </svg>
                                        <div class="alert alert-primary d-flex align-items-center" role="alert">
                                            <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Info:"><use xlink:href="#info-fill"/></svg>
                                            <div>
                                                <div class="mb-2">This transaction will be processed as a 'No Payment' transaction.</div>
                                                <div class="mb-2">Please press 'Checkout' and then take payment from the customer before clicking the 'Complete Order' button.</div>
                                                <div>You will be invoiced monthly for your sales minus your commission.</div>
                                            </div>
                                        </div>
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
                                                <span class="badge org-badge-primary">{{ retailerGroupsForUser[0].name }}</span>
                                            </template>
                                        </div>
                                        <div>
                                            <div v-if="isRetailer">
                                                <input id="isNoPayment" type="hidden" name="no_payment" value="true" />

                                                <button v-if="!isRedirecting" @click="checkoutCart" class="btn licensing-btn-primary px-5 me-2" type="submit">Checkout</button>
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
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import { useStore } from '@/stores/state'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'
import BootstrapButtonSpinner from '@/utils/vue/BootstrapButtonSpinner.vue'
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
            let gst = this.totalPrice / constants.GST;
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
</style>
