<template>
  <div class="container" id="your-park-passes">

    <h2 class="px-4 pb-3">Your Park Passes</h2>

    <div v-if="passes" id="passes" class="passes row row-cols-1 row-cols-sm-1 row-cols-md-1 row-cols-lg-1 row-cols-xl-2 row-cols-xxl-2 g-4 px-4">
        <div v-for="pass in passes" class="col-xs">
          <div class="card border-bottom-0 rounded-0 rounded-top">
            <img :src="pass.pass_type_image" class="img-fluid float-left" width="300" />
            <div class="card-body">
              <h5 class="card-title">{{ pass.pass_type }}</h5>
              <p class="card-text mt-3 rounded-bottom-0">
                <div class="border-bottom">{{  passCurrentOrFuture(pass) ? 'Start Date' : 'Started' }}:</div>
                <div class="border-bottom ps-1">{{ pass.date_start }}</div>
                <div class="border-bottom">{{  passCurrentOrFuture(pass) ? 'Expiry Date' : 'Expired' }}:</div>
                <div class="border-bottom ps-1">{{ pass.date_expiry }}</div>
                <label v-if="passCurrentOrFuture(pass)" class="orm-check-label mt-2">Renew Automatically</label>
                <div v-if="passCurrentOrFuture(pass)" class="form-check form-switch mt-2 mx-auto">
                  <input @change="updatePass(pass)" class="form-check-input" type="checkbox" id="flexSwitchCheckDefault" v-model="pass.renew_automatically">
                </div>
              </p>
            </div>
          </div>
          <div class="card-footer border-top-0 align-items-center">
            <div><span class="badge" :class="statusClass(pass)">{{ pass.processing_status_display_name }}</span></div>
            <div v-if="canUpdateVehicleDetails(pass)" class="link"><a data-bs-toggle="collapse" :href="'#updateVehicleRego'+pass.id" role="button" aria-expanded="false" :aria-controls="'updateVehicleRego'+pass.id">Update Vehicle Rego</a> <i class="fa-solid fa-car fa-lg ps-1"></i></div>
            <div v-else></div>
            <div v-if="passCurrentOrFuture(pass)" class="link"><a :href="passURL(pass.id)" target="blank">Download Pass PDF</a> <i class="fa-solid fa-file-pdf fa-lg ps-1"></i></div>
            <div v-else></div>
            <div v-if="pass.invoice_link" class="link"><a target="blank" :href="pass.invoice_link">Download Invoice</a> <i class="fa-solid fa-file-invoice fa-lg ps-1"></i></div>
            <div v-else></div>

          </div>
          <div v-if="canUpdateVehicleDetails(pass)" :id="'updateVehicleRego'+pass.id" class="showUpdateVehicleRego collapse">

            <div class="row">
              <div class="col">
                <input type="text" class="form-control form-control-sm m-3" placeholder="Vehicle 1 Registration" aria-label="Vehicle Registration 1" v-model="pass.vehicle_registration_1" maxlength="10">
              </div>
              <div class="col">
                <input type="text" class="form-control form-control-sm m-3" placeholder="Vehicle 2 Registration" aria-label="Vehicle Registration 2" v-model="pass.vehicle_registration_2" maxlength="10">
              </div>
              <div class="col">
                <button v-if="!loadingUpdatePass" @click="updatePass(pass)" class="btn btn-sm licensing-btn-primary float-end m-3 px-5">Update</button>
                <button v-else class="btn btn-sm licensing-btn-primary float-end m-3 px-5">
                    <div class="spinner-border text-light" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </button>
              </div>
            </div>

          </div>
        </div>
    </div>

    <div v-if="loading" class="d-flex justify-content-center mt-5">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>

  </div>
</template>

<script>
import { apiEndpoints, helpers } from '@/utils/hooks'
import Swal from 'sweetalert2'

export default {
  name: "externalDashboard",
  data: function () {
    return {
        loading: false,
        loadingMore: false,
        loadingUpdatePass: false,
        passes: null,
        pageIndex: 0,
        count: null,
    }
  },
  components: {

  },
  computed: {
      allResultsLoaded() {
          return this.pageIndex * 10 >= this.count;
      }
  },
  methods: {
    statusClass: function (pass) {
      switch (pass.processing_status) {
        case 'CU':
          return 'bg-success';
        case 'FU':
          return 'bg-info';
        default:
          return 'bg-danger';
      }
    },
    passURL: function(passId) {
      return apiEndpoints.externalParkPassPdf(passId);
    },
    showUpdateVehicleRego: function(passId) {
      console.log('showUpdateVehicleRego');
      $(`#updateVehicleRego${passId}`).slideDown();
    },
    passCurrentOrFuture: function (pass) {
      switch (pass.processing_status) {
        case 'CU':
          return true;
        case 'FU':
          return true;
        default:
          return false;
      }
    },
    canUpdateVehicleDetails: function (pass) {
      return this.passCurrentOrFuture(pass) && !pass.prevent_further_vehicle_updates;
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
          if(vm.passes){
              vm.passes.push(...data.results)
          } else {
              vm.passes = data.results
          }
          vm.count = data.count
          vm.loading = false;
          vm.loadingMore = false;
        })
        .catch(error => {
          this.systemErrorMessage = "ERROR: Please try again in an hour.";
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
                confirmButtonText: 'OK'
            })
            vm.loadingUpdatePass = false;
        })
        .catch(error => {
            this.systemErrorMessage = "ERROR: Please try again in an hour.";
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
/* For Mobile */
@media screen and (max-width: 540px) {
  .card {
    width:300px;
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
    width:300px;
    margin:auto;
  }
  .card-footer div {
    margin-top:10px;
  }
}

/* For Tablets */
@media screen and (min-width: 540px) and (max-width: 780px) {

}

/* For Computers */
@media screen and (min-width: 780px){
.card {
  flex-direction: row;
}
.card-title {
  font-size: 1.1em;
  color: #696969;
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

.showUpdateVehicleRego{
  background-color:rgba(0, 0, 0, 0.03);
  color: #444;
}

}



</style>
