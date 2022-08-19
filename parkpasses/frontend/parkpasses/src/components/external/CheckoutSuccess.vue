<template>
    <div class="container" id="shopHome">
        <div class="row">
            <div class="col">
                <h1>Checkout Success</h1>
            </div>
        </div>
        <div class="row">
            <div class="col-md-3 p-3">
                <p>You're order has been processed successfully. Yay!</p>

                <p>Say some more stuff here.</p>
            </div>

        </div>
    </div>

</template>

<script>
import { apiEndpoints } from '@/utils/hooks'
import Loader from '@/utils/vue/Loader.vue'

export default {
    name: "FAQs",
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
