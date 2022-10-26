<template>
  <div>

    <div v-if="!isRetailer" class="list-item">
      <div @click="purchaseVoucher()" :class="[
        'voucher',
        { 'opacity-25': activeItem && 'voucher' != activeItem },
      ]">
        <img class="img-fluid" src="/static/parkpasses/img/gift-voucher.jpg" width="300" height="266" />
        <div class="more-information">More Information</div>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">
      {{ errorMessage }}
    </div>

    <div v-if="passTypes" class="list-item" v-for="(passType, index) in passTypes" :key="passType.id">
      <div :class="{'opacity-25': activeItem && (passType.slug != activeItem)}" @click="purchasePass(passType.slug, index)">
        <img v-show="allImagesLoaded" class="img-fluid rounded" width="300" height="150" @load="imageLoaded()" :src="passType.image" />
        <div v-show="!allImagesLoaded" class="skeleton-block rounded"></div>
        <div class="more-information">More Information</div>
      </div>
      <div :class="{'opacity-50': activeItem && (passType.slug != activeItem)}" class="display-name text-truncate">{{ passType.display_name }}</div>
    </div>

    <div v-if="!passTypes">
        <BootstrapSpinner :isLoading="true" :centerOfScreen="false" />
    </div>
  </div>

</template>

<script>
import { apiEndpoints, constants } from "@/utils/hooks";
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'

export default {
  name: "ShopSideMenu",
  emits: ["purchaseVoucher", "purchasePass"],
  props: {
    isRetailer: {
      type: Boolean,
      default: false
    },
  },
  data: function () {
    return {
      activeItem: null,
      passTypes: null,
      imagesLoaded: 0,
      allImagesLoaded: false,
      errorMessage: null,
    };
  },
  components: {
    BootstrapSpinner,
  },
  methods: {
    imageLoaded: function() {
      this.imagesLoaded += 1;
      if(this.passTypes && (this.passTypes.length==this.imagesLoaded)){
        this.allImagesLoaded = true;
      }
    },
    getPassTypeApiEndpoint: function() {
      if(this.isRetailer){
        return apiEndpoints.passTypesRetailer
      }
      return apiEndpoints.passTypesExternal
    },
    fetchPassTypes: function () {
      let vm = this;
      fetch(vm.getPassTypeApiEndpoint())
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
  max-width: 100%;
  height: auto;
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
  width: -moz-fit-content;
  width: fit-content;
  text-overflow: ellipsis;
  max-width: 95%;
}


.more-information {
  display:flex;
  justify-content:center;
  align-items:center;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  gap:0px;
}

.skeleton-block {
  display: block;
  background: linear-gradient(
      to right,
      rgba(255, 255, 255, 0),
      rgba(255, 255, 255, 0.5) 50%,
      rgba(255, 255, 255, 0) 80%
    ),
    lightgray;
  background-repeat: repeat-y;
  background-size: 50px 200px;
  background-position: 0 0;
  width:300px;
  height:150px;
  animation: shine 1s infinite;
}
@keyframes shine {
  to {
    background-position: 100% 0, /* move highlight to right */ 0 0;
  }
}
</style>
