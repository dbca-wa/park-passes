<template>
  <div class="container" id="shopHome">
    <div class="row">

      <div class="col-4">

        Helpful Stuff will go here.

      </div>

      <div class="col">

        <h1>Cart</h1>

        <div v-if="loading" class="d-flex justify-content-center mt-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else>
            <div class="accordion" id="checkoutAccordion">
                <template v-if="cartItems && cartItems.length">
                    <CartItem v-for="cartItem in cartItems" @deleteCartItem="deleteCartItem" :cartItem="cartItem" :key="cartItem.id" />
                </template>
                <template v-else>
                    <div class="card mb-1">
                        <div class="card-header checkout-item-header">
                            There are no items in your cart.
                        </div>
                    </div>
                </template>
                <div>
                    <div class="row my-3 mx-1 g-0">
                        <div class="col">
                            Total
                        </div>
                        <div class="col-md-auto">
                            ${{totalPrice}}
                        </div>
                    </div>
                    <div v-if="totalPrice > 0" class="d-flex flex-row-reverse">
                        <div class="col-auto align-right">
                            <button @click="checkoutCart" class="btn licensing-btn-primary px-5" type="button">Pay</button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { apiEndpoints, helpers } from '@/utils/hooks'
import CartItem from '@/components/external/CartItem.vue'

export default {
    name: "Cart",
    data: function () {
        return {
            cartItems: [],
            loading: false,
        };
    },
    components: {
        apiEndpoints,
        helpers,
        CartItem
    },
    computed: {
        totalPrice() {
            if(0==this.cartItems.length){
                return '0.00'
            } else if(1==this.cartItems.length) {
                if(this.cartItems[0].hasOwnProperty('voucher_number')){
                    return this.cartItems[0].amount;
                } else {
                    return this.cartItems[0].price;
                }
            } else {
                let total = 0.00;
                this.cartItems.forEach(function(cartItem, index) {
                    if(cartItem.hasOwnProperty('voucher_number')){
                        return total += parseFloat(cartItem.amount);
                    } else {
                        return total += parseFloat(cartItem.price);
                    }
                });
                return total.toFixed(2);
            }
        }
    },
    methods: {
        checkoutCart: function () {
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
                // Do something after adding the voucher to the database and the users cart
                vm.cartItems = data
            })
            .catch(error => {
                vm.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            }).finally(() => {
                vm.loading = false;
            });
        },
        deleteCartItem: function(cart_item_id) {
            console.log("deleteCartItem = " + cart_item_id);
            this.cartItems.splice(this.cartItems.findIndex(cartItem => cartItem.cart_item_id === cart_item_id), 1);
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
