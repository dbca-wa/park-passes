<template>
  <div class="container" id="shopHome">
    <div class="row">

      <div class="col-4">

        Helpful Stuff will go here.

      </div>

      <div class="col">

        <h1>Checkout</h1>

        <div v-if="cartItems" class="accordion" id="accordionExample">
            <CartItem v-for="cartItem in cartItems" :cartItem="cartItem" :key="cartItem.id" />
            <div v-if="cartItems">
                <div class="row my-3 mx-1 g-0">
                    <div class="col">
                        Total
                    </div>
                    <div class="col-md-auto">
                        ${{totalPrice}}
                    </div>
                </div>
                <div class="d-flex flex-row-reverse">
                    <div class="col-auto align-right">
                        <button @click="submitForm" class="btn licensing-btn-primary px-5" type="button">Pay</button>
                    </div>
                </div>
            </div>
        </div>
        <div v-else>
            There are no items in your cart.
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks'
import CartItem from '@/components/external/CartItem.vue'

export default {
    name: "Checkout",
    data: function () {
        return {
            cartItems: [],
        };
    },
    components: {
        api_endpoints,
        helpers,
        CartItem
    },
    computed: {
        totalPrice() {
            if(0==this.cartItems.length){
                return '0.00'
            } else if(1==this.cartItems.length) {
                return this.cartItems[0].amount
            } else {
                const total = this.cartItems.reduce((accumulator, object) => {
                    return accumulator + object.amount;
                }, 0);
            }
        }
    },
    methods: {
        functionName: function () {

        },
        fetchCartItems: function () {
            let vm = this;
            fetch(api_endpoints.checkout)
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
            });
            console.log(this.cartItems);
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
