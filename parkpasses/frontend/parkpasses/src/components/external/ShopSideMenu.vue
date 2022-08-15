<template>
  <div>
    <div
      @click="purchaseVoucher()"
      :class="[
        'list-item voucher',
        { 'opacity-25': activeItem && 1 != activeItem },
      ]"
    >
      <img src="/media/gift-voucher.jpg" width="300" />
      <div class="more-information">More Information</div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">
      {{ errorMessage }}
    </div>

    <div

        v-for="(passType, index) in passTypes"
        :class="[
            'list-item pass-type',
            { 'opacity-25': activeItem && (index+2) != activeItem },
        ]"
        @click="purchasePass(passType.id, index)"
        :key="passType.id"
        >
        <img :src="passType.image" width="300" />
        <div class="more-information">More Information</div>
        <div class="display-name">{{ passType.display_name }}</div>
        </div>
    </div>

</template>

<script>
import { apiEndpoints } from "@/utils/hooks";

export default {
  name: "ShopSideMenu",
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
          this.errorMessage = "ERROR: Please try again in an hour.";
          console.error("There was an error!", error);
        });
    },
    purchasePass: function (passTypeId, index) {
        this.$emit('purchasePass', passTypeId);
        this.activeItem = index+2;
        console.log('this.activeItem = ' + this.activeItem)
    },
    purchaseVoucher: function () {
        this.$emit('purchaseVoucher');
        this.activeItem = 1;
        console.log('this.activeItem = ' + this.activeItem)
    },
  },
  created: function () {
    this.fetchPassTypes();
    console.log('this.activeItem = ' + this.activeItem);
  },
  mounted: function () {},
};
</script>

<style scoped>
.opacity-25 {
  opacity: 0.25;
}

.list-item {
  position: relative;
  display: inline-block;
}

.list-item img {
  opacity: 1;
}

.list-item img:hover {
  opacity: 0.8;
  cursor: pointer;
}

.display-name {
  position: absolute;
  bottom: 6px;
  left: 6px;
  color: #fff;
  background: rgba(0, 0, 0, 0.5);
  padding: 5px;
  border-radius: 5px;
}

.list-item,
.voucher {
  margin: 0 0 8px 0;
}

.more-information {
  display: inline-block;
  position: relative;
  margin-left: -57px;
  font-size: 1.1em;
  color: #9f9f9f;

  transform: rotate(-90deg);

  /* Legacy vendor prefixes that you probably don't need... */

  /* Safari */
  -webkit-transform: rotate(-90deg);

  /* Firefox */
  -moz-transform: rotate(-90deg);

  /* IE */
  -ms-transform: rotate(-90deg);

  /* Opera */
  -o-transform: rotate(-90deg);

  /* Internet Explorer */
  filter: progid:DXImageTransform.Microsoft.BasicImage(rotation=3);
}
</style>
