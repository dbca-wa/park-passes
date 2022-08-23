<template>
  <div class="container" id="shopHome">
    <div class="row">

      <div class="col-4">

        <ShopSideMenu @purchase-voucher="purchaseVoucher" @purchase-pass="purchasePass" />

      </div>

      <div class="col">

        <HomeContent v-if="showHomeContent" />

        <PurchaseVoucher v-if="showPurchaseVoucher" />

        <PurchasePass v-if="showPurchasePass" :passTypeId="passTypeId" :key="passTypeId" />

      </div>
    </div>
  </div>
</template>

<script>
import { apiEndpoints } from '@/utils/hooks'
import { useStore } from '@/stores/state'
import ShopSideMenu from '@/components/external/ShopSideMenu.vue'
import HomeContent from '@/components/external/HomeContent.vue'
import PurchaseVoucher from '@/components/external/PurchaseVoucher.vue'
import PurchasePass from '@/components/external/PurchasePass.vue'

export default {
    name: "ShopHome",
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
        apiEndpoints,
        ShopSideMenu,
        HomeContent,
        PurchaseVoucher,
        PurchasePass,
    },
    methods: {
        purchaseVoucher: function () {
            this.passTypeId = 0;
            console.log('this.passTypeId = ' + this.passTypeId)
            this.$router.push({ name:'purchase-voucher' });
            this.showHomeContent = false;
            this.showPurchasePass = false;
            this.showPurchaseVoucher = true;
        },
        purchasePass: function (passTypeId) {
            this.passTypeId = passTypeId;
            this.$router.push({ name:'purchase-pass', params: { passTypeId: this.passTypeId } });
            this.showHomeContent = false;
            this.showPurchaseVoucher = false;
            this.showPurchasePass = true;
        },
        redirectToFAQ: function() {
            window.location.href = '/faq/'
        },
        redirectToHelp: function() {
            window.location.href = '/help/'
        }
    },
    created: function() {
        if('purchase-voucher'==this.$route.name){
            this.showHomeContent = false;
            this.showPurchasePass = false;
            this.showPurchaseVoucher = true;
        } else if ('purchase-pass'==this.$route.name) {
            this.passTypeId = this.$route.params.passTypeId;
            this.showHomeContent = false;
            this.showPurchaseVoucher = false;
            this.showPurchasePass = true;
        }
    },
};
</script>
