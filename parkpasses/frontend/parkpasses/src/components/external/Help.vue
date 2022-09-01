<template>
    <div class="container" id="shopHome">
        <div class="row">
            <div class="col">
                <h1>Help</h1>
            </div>
        </div>
        <div class="row">
            <div class="col p-3">
                <div id="help">
                    <p>The help page will go here.</p>
                </div>
            </div>
        </div>
    </div>

</template>

<script>
import { apiEndpoints } from '@/utils/hooks'
import Loader from '@/utils/vue/Loader.vue'

export default {
    name: "Help",
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
