<template>
    <div class="container" id="sell-a-pass">
        <div class="row">
            <div class="col pb-3">
                <h1>Sell a Pass</h1>
            </div>
        </div>
      <div class="row">

        <div class="col-4">

          <SideMenu @purchase-pass="purchasePass" />

        </div>

        <div class="col">

          <PurchasePass v-if="showPurchasePass" :passTypeId="passTypeId" :key="passTypeId" />

        </div>
      </div>
    </div>
  </template>

<script>

import { useStore } from '@/stores/state'
import SideMenu from '@/components/retailer/SideMenu.vue'
import PurchasePass from '@/components/external/PurchasePass.vue'

export default {
    name: "SellPass",
    data: function () {
        return {
            passTypeId: -1,
            showHomeContent: true,
            showPurchaseVoucher: false,
            showPurchasePass: false,
            errorMessage: null,
            store: useStore()
        };
    },
    components: {
        SideMenu,
        PurchasePass
    },
    methods: {
        purchasePass: function (passTypeId) {
            this.passTypeId = passTypeId;
            this.$router.push({ name:'sell-a-pass', params: { passTypeId: this.passTypeId } });
            this.showHomeContent = false;
            this.showPurchaseVoucher = false;
            this.showPurchasePass = true;
        },
    },
    created: function() {
        if ('purchase-pass'==this.$route.name) {
            this.passTypeId = this.$route.params.passTypeId;
            this.showHomeContent = false;
            this.showPurchaseVoucher = false;
            this.showPurchasePass = true;
        }
    },
    mounted: function () {

    }
}

</script>

<style scoped>

</style>
