<template>
    <div class="container" id="sell-a-pass">

        <div class="row">

            <div class="col-4">

                <ShopSideMenu :is-retailer="true" @purchase-pass="purchasePass" />

            </div>

            <div class="col">

                <PurchasePass v-if="showPurchasePass" :is-retailer="true" :passTypeSlug="passTypeSlug" :key="passTypeSlug" />
                <h1 v-else>&#8592; &#8592; &#8592; Select a Pass Type</h1>
            </div>

        </div>
    </div>
  </template>

<script>

import { useStore } from '@/stores/state'
import ShopSideMenu from '@/components/external/ShopSideMenu.vue'
import PurchasePass from '@/components/external/PurchasePass.vue'

export default {
    name: "SellPass",
    data: function () {
        return {
            passTypeSlug: '',
            showHomeContent: true,
            showPurchaseVoucher: false,
            showPurchasePass: false,
            errorMessage: null,
            store: useStore()
        };
    },
    components: {
        ShopSideMenu,
        PurchasePass
    },
    methods: {
        purchasePass: function (passTypeSlug) {
            this.passTypeSlug = passTypeSlug;
            this.$router.push({ name:'retailer-sell-a-pass-by-slug', params: { passTypeSlug: this.passTypeSlug } });
            this.showHomeContent = false;
            this.showPurchaseVoucher = false;
            this.showPurchasePass = true;
        },
    },
    created: function() {
        if ('retailer-sell-a-pass-by-slug'==this.$route.name) {
            this.passTypeSlug = this.$route.params.passTypeSlug;
            this.showHomeContent = false;
            this.showPurchaseVoucher = false;
            this.showPurchasePass = true;
        }
    },
    mounted: function () {
        console.log(this.$route.name);
    }
}

</script>

<style scoped>

</style>
