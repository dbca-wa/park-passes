<template>
  <div class="container" id="your-park-passes">

    <h2 class="pb-3">Your Park Passes</h2>

    <div v-if="passes && passes.length > 0" id="passes" class="passes row row-cols-1 row-cols-sm-1 row-cols-md-1 row-cols-lg-1 row-cols-xl-1 row-cols-xxl-2 g-4">
        <div v-for="pass in passes" class="pass col-xs">
          <div class="card border-bottom-0 rounded-0 rounded-top">
            <img v-show="allImagesLoaded" @load="imageLoaded()" :src="pass.pass_type_image" class="img-fluid float-left" width="300" height="150" />
            <div v-show="!allImagesLoaded" class="skeleton-block rounded"></div>
            <div class="pass-number">{{pass.pass_number}}</div>

            <div class="card-body">
              <h5 class="card-title">{{ pass.pass_type }}</h5>
              <p class="card-text mt-3 rounded-bottom-0">
                <div class="border-bottom">{{  passCurrentOrFuture(pass) ? 'Start Date' : 'Started' }}:</div>
                <div class="border-bottom ps-1">{{ formatDate(pass.date_start) }}</div>
                <div class="border-bottom">{{  passCurrentOrFuture(pass) ? 'Expiry Date' : 'Expired' }}:</div>
                <div class="border-bottom ps-1">{{ formatDate(pass.date_expiry) }}</div>
                <label v-if="showAutoRenewalOption(pass)" class="orm-check-label mt-2">Auto Renew</label>
                <div v-if="showAutoRenewalOption(pass)" class="form-check form-switch mt-2 mx-auto">
                  <input @change="updatePass(pass)" class="form-check-input" type="checkbox" id="flexSwitchCheckDefault" v-model="pass.renew_automatically" :disabled="loadingUpdatePass">
                </div>
              </p>
            </div>
          </div>
          <div class="card-footer border-top-0 align-items-center m-0">
            <div><span class="badge" :class="statusClass(pass.status)">{{ pass.status_display }}</span></div>
            <div v-if="canUpdateVehicleDetails(pass)" class="link"><a data-bs-toggle="collapse" :href="'#updateVehicleRego'+pass.id" role="button" aria-expanded="false" :aria-controls="'updateVehicleRego'+pass.id">Update <span class="d-xl-none d-xxl-inline">Vehicle</span> Rego</a> <i class="fa-solid fa-car fa-lg ps-1"></i></div>
            <div v-else></div>
            <div v-if="passCurrentOrFuture(pass)" class="link"><a :href="passURL(pass.id)" target="blank">Download Pass PDF</a> <i class="fa-solid fa-file-pdf fa-lg ps-1"></i></div>
            <div v-else></div>
            <div v-if="soldViaDBCA(pass)" class="link"><a target="_blank" rel="noopener" :href="invoiceURL(pass.id)">Download Invoice</a> <i class="fa-solid fa-file-invoice fa-lg ps-1"></i></div>
            <div v-else class="link"> <a href="/contact/">Contact DBCA</a> <i class="fa-solid fa-phone fa-lg ps-1"></i></div>

          </div>
          <div v-if="canUpdateVehicleDetails(pass)" :id="'updateVehicleRego'+pass.id" class="container p-0 showUpdateVehicleRego collapse">
            <div class="row g-0">
              <div class="col-12 col-sm-4 pe-md-2">
                <input type="text" class="form-control form-control-sm my-3 mx-sm-3" placeholder="Vehicle 1 Registration" aria-label="Vehicle Registration 1" v-model="pass.vehicle_registration_1" maxlength="10" :disabled="loadingUpdatePass">
              </div>
              <div v-if="showSecondVehicleRego(pass)" class="col-12 col-sm-4 pe-md-2">
                <input type="text" class="form-control form-control-sm my-3 mx-sm-3" placeholder="Vehicle 2 Registration" aria-label="Vehicle Registration 2" v-model="pass.vehicle_registration_2" maxlength="10" :disabled="loadingUpdatePass">
              </div>
              <div class="col-12 col-sm-4 px-md-2">
                <button v-if="!loadingUpdatePass" @click="updatePass(pass)" class="btn btn-sm licensing-btn-primary mt-3 px-3 ms-md-2">Update</button>
                <button v-else class="btn btn-sm licensing-btn-primary mt-3 px-3">
                    <div class="spinner-border text-light" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </button>
              </div>
            </div>

          </div>
        </div>
    </div>
    <div v-else class="no-passes mb-4 col-12">
        <div>
            <span>You have not purchased any park passes yet.</span>
        </div>
    </div>

    <div v-if="loading || loadingMore || loadingUpdatePass">
        <BootstrapSpinner :isLoading="true" />
    </div>

    <div v-if="systemErrorMessage" class="alert alert-danger" role="alert">
        {{ systemErrorMessage }}
    </div>

  </div>
</template>

<script>
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'

import Swal from 'sweetalert2'

export default {
  name: "externalDashboard",
  data: function () {
    return {
        loading: false,
        loadingMore: false,
        loadingUpdatePass: false,
        passes: null,
        imagesLoaded: 0,
        pageIndex: 0,
        count: null,
        allImagesLoaded: false,
        systemErrorMessage: null,
    }
  },
  components: {
      BootstrapSpinner
  },
  computed: {
      allResultsLoaded() {
          return this.pageIndex * 10 >= this.count;
      }
  },
  methods: {
    imageLoaded: function() {
      this.imagesLoaded += 1;
      if(this.passes && (this.passes.length==this.imagesLoaded)){
        this.allImagesLoaded = true;
      }
    },
    formatDate: function(date){
      return helpers.getShorterDate(date);
    },
    statusClass: function (status) {
      switch (status) {
        case 'CU':
          return 'bg-success';
        case 'FU':
          return 'bg-info';
        default:
          return 'bg-danger';
      }
    },
    showSecondVehicleRego: function (pass) {
        console.log(pass);
        return constants.HOLIDAY_PASS_NAME==pass.pass_type_name ? false : true
    },
    passURL: function(passId) {
        return apiEndpoints.externalParkPassPdf(passId);
    },
    invoiceURL: function(passId) {
        return apiEndpoints.externalParkPassInvoice(passId);
    },
    soldViaDBCA: function(pass) {
        return constants.DEFAULT_SOLD_VIA == pass.sold_via_name;
    },
    showAutoRenewalOption: function(pass) {
        if('EX' == pass.processing_status){
            return false;
        }
        if('DAY_ENTRY_PASS' == pass.pass_type_name ||
        'HOLIDAY_PASS' == pass.pass_type_name) {
            return false;
        }
        return true;
    },
    passCurrentOrFuture: function (pass) {
        if('CU'==pass.status ||'FU'==pass.status){
          return true;
        }
        return false;
    },
    canUpdateVehicleDetails: function (pass) {
      if(constants.PINJAR_PASS_NAME==pass.pass_type_name){
          return false;
      }
      if(pass.prevent_further_vehicle_updates){
        return false;
      }
      return this.passCurrentOrFuture(pass);
    },
    fetchPasses: function () {
      let vm = this;
      vm.pageIndex++;
      if(!vm.passes){
          vm.loading = true;
      }
      fetch(apiEndpoints.passesListExternal + '?page=' + vm.pageIndex)
        .then(async response => {
          const data = await response.json();
          if (!response.ok) {
            const error = (data && data.message) || response.statusText;
            console.log(error)
            return Promise.reject(error);
          }
          if(vm.passes && vm.passes.length>0){
              vm.passes.push(...data.results)
          } else {
              vm.passes = data.results
          }
          vm.count = data.count

          // Load more passes if there are no enough to fill the screen.
          var hasVScroll = document.body.scrollHeight > document.body.clientHeight;
          var cStyle = document.body.currentStyle||window.getComputedStyle(document.body, "");
          hasVScroll = cStyle.overflow == "visible"
                      || cStyle.overflowY == "visible"
                      || (hasVScroll && cStyle.overflow == "auto")
                      || (hasVScroll && cStyle.overflowY == "auto");
          if(!hasVScroll && !vm.allResultsLoaded){
            this.fetchPasses();
          }
          vm.loading = false;
          vm.loadingMore = false;
        })
        .catch(error => {
          this.systemErrorMessage = constants.ERRORS.NETWORK;
          console.error("There was an error!", error);
        });
    },
    handleScroll: function(e) {
        let vm = this;
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
            console.log('At bottom of page');
        }
    },
    updatePass: function (pass) {
        let vm = this;
        vm.loadingUpdatePass = true;
        pass.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
        const requestOptions = {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(pass)
        };
        fetch(apiEndpoints.updatePassExternal(pass.id), requestOptions)
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                const error = (data && data.message) || response.statusText;
                console.log(error);
                return Promise.reject(error);
            }
            Swal.fire({
                title: 'Success',
                text: 'Park Pass updated successfully.',
                icon: 'success',
                showConfirmButton: false,
                timer: 1500
            })
            vm.loadingUpdatePass = false;
        })
        .catch(error => {
            this.systemErrorMessage = constants.ERRORS.NETWORK;
            console.error("There was an error!", error);
        });
    },
  },
  created: function () {
      this.fetchPasses();
  },
  mounted: function () {
    let vm = this;
    window.onscroll = async function(ev) {
        if(!vm.loadingMore && !vm.allResultsLoaded) {
            let element = document.getElementById('passes');
            if (element.getBoundingClientRect().bottom < window.innerHeight) {
                vm.loadingMore = true;
                await vm.fetchPasses();
            }
        }
    };

  },

};
</script>

<style scoped>
/* For small mobile */
@media screen and (max-width: 320px) {
  h2 {
    font-size:1.4em;
  }
}

@media screen and (max-width: 767px) {
  .card {
    max-width:300px;
  }
  .card-title {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 270px;
  }
  .card img {
    flex-direction: column;
    width:300px;
  }

  .card-text {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-gap: 5px;
    background-color: #fff;
    color: #444;
    font-size: 0.9em;
  }

  .card-footer {
    max-width:300px;
  }
  .card-footer div {
    margin-top:10px;
  }

  .showUpdateVehicleRego{
    max-width: 300px;
  }
}
/* For Tablets */
@media (min-width: 576px) {

}

/* For Computers */
@media (min-width: 768px) {
  .card {
    flex-direction: row;
  }
  .card-title {
    font-size: 1.1em;
    color: #696969;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 260px;

  }

  .card-body {
    padding:12px;
  }

  .card-text {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-gap: 5px;
    background-color: #fff;
    color: #444;
    font-size: 0.9em;
  }

  .card-footer {
    display: grid;
    grid-template-columns: 1fr max-content max-content max-content;
    grid-gap: 20px;
    color: #444;
  }

  .card-footer .link {
    font-size: 0.8em;
  }

  .pass{
    max-width:600px;
  }
}

.passes {
  min-height: 200px;
}

.pass-number {
  position:absolute;
  top: 6px;
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

.showUpdateVehicleRego{
    background-color:#EDE5D9;
    color: #444;
  }

.no-passes {
    background-color: #EDE5D9;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    border: 1px solid rgba(0, 0, 0, 0.125);
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

.card-footer {
  background-color: #EDE5D9;
}

</style>
