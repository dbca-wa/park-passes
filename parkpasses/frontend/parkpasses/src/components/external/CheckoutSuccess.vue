<template>
    <div class="container" id="shopHome">
        <div class="row">
            <div class="col">
                <h1>Checkout Success</h1>
            </div>
        </div>
        <div class="row gx-4">
            <div class="col-md-3 p-3">
                <p>Maybe add some reassuring text here.</p>

                <p>Mauris a purus lorem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae;
                Nam sollicitudin lectus lacus. Morbi id nibh in mauris pharetra porta. Aliquam at lectus massa.
                Nulla elit dolor, fermentum quis dignissim id, finibus quis purus. Donec sed efficitur metus, nec sagittis neque.
                Sed at aliquam turpis. Cras mauris felis, rhoncus nec turpis ac, eleifend imperdiet dui.</p>

                <p>Proin aliquam pulvinar neque, pharetra cursus libero auctor eu. Ut hendrerit eros at nisl efficitur blandit.
                Proin luctus gravida tortor. Fusce ut diam eu augue sollicitudin fringilla. Praesent accumsan ultricies porttitor.
                Nam sollicitudin condimentum nisi, eget vulputate magna varius sollicitudin.</p>

                <p>Integer vel erat aliquam, viverra dolor eu, interdum augue. Sed magna purus, accumsan id suscipit at, gravida ac nisl.</p>
            </div>

            <div class="col-md-8">

                <div class="card">
                    <h5 class="card-header">Your Order has been processed successfully</h5>
                    <div class="card-body">
                        <h5 class="card-title">Special title treatment</h5>
                        <p class="card-text">With supporting text below as a natural lead-in to additional content.</p>
                        <a href="#" class="btn btn-primary">Go somewhere</a>
                    </div>
                </div>

            </div>

        </div>
    </div>

</template>

<script>
import { apiEndpoints } from '@/utils/hooks'
import Loader from '@/utils/vue/Loader.vue'

export default {
    name: "CheckoutSuccess",
    data: function () {
        return {
            faqs: null
        };
    },
    components: {
        Loader
    },
    methods: {

    },
    created: function() {

    }
};
</script>

<style scoped>

</style>
