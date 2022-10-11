<template>
  <div>
    <div class="list-item">
      <div @click="purchaseVoucher()" :class="[
        'voucher',
        { 'opacity-25': activeItem && 'voucher' != activeItem },
      ]">
        <img src="/static/parkpasses/img/gift-voucher.jpg" width="300" height="266" />
        <div class="more-information">More Information</div>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">
      {{ errorMessage }}
    </div>

    <div class="list-item" v-for="(passType, index) in passTypes" :key="passType.id">
      <div :class="{'opacity-25': activeItem && (passType.slug != activeItem)}" @click="purchasePass(passType.slug, index)">
        <img classes="rounded" :src="passType.image" width="300" height="150" />
        <div class="more-information">More Information</div>
      </div>
      <div :class="{'opacity-50': activeItem && (passType.slug != activeItem)}" class="display-name">{{ passType.display_name }}</div>
    </div>
  </div>

</template>

<script>
import { apiEndpoints, constants } from "@/utils/hooks";

export default {
  name: "ShopSideMenu",
  emits: ["purchaseVoucher", "purchasePass"],
  data: function () {
    return {
      activeItem: null,
      passTypes: [],
      errorMessage: null,
    };
  },
  methods: {
    fetchPassTypes: function () {
      let vm = this;
      fetch(apiEndpoints.passTypes)
        .then(async (response) => {
          const data = await response.json();
          if (!response.ok) {
            const error = (data && data.message) || response.statusText;
            console.log(error);
            return Promise.reject(error);
          }
          vm.passTypes = data.results;
        })
        .catch((error) => {
          this.errorMessage = constants.ERRORS.NETWORK;
          console.error("There was an error!", error);
        });
    },
    purchasePass: function (passTypeSlug, index) {
      this.$emit('purchasePass', passTypeSlug);
      this.activeItem = passTypeSlug;
    },
    purchaseVoucher: function () {
      this.$emit('purchaseVoucher');
      this.activeItem = 'voucher';
    },
  },
  created: function () {
    this.fetchPassTypes();
    if ('purchase-voucher' == this.$route.name) {
      this.activeItem = 'voucher';
    }
    else if (this.$route.params.passTypeSlug) {
      this.activeItem = this.$route.params.passTypeSlug;
    }
  },
  mounted: function () { },
};
</script>

<style scoped>
.opacity-25 {
  opacity: 0.25;
}
.opacity-50 {
  opacity: 0.50;
}

.list-item div {
  display:flex;
  gap: 5px;
}

.list-item img {
  opacity: 1;
}

.list-item:hover {
  opacity: 0.8;
  cursor: pointer;
}

.display-name {
  position: relative;
  bottom: 40px;
  left: 6px;
  color: #fff;
  background: rgba(0, 0, 0, 0.5);
  padding: 5px;
  margin:0 0 -20px 0;
  border-radius: 5px;
  width: fit-content;
}


.more-information {
  display:flex;
  justify-content:center;
  align-items:center;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  height: 150px;
  gap:0px;
}

</style>
