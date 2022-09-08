<template>
  <div class="container" id="your-park-passes">

    <h2 class="px-4 pb-3">Your Park Passes</h2>

    <div v-if="loading" class="d-flex justify-content-center mt-5">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>

    <div v-else class="row row-cols-1 row-cols-sm-1 row-cols-md-1 row-cols-lg-1 row-cols-xl-2 row-cols-xxl-2 g-4 px-4">
        <div v-for="pass in passes" class="col-xs">
          <div class="card border-bottom-0 rounded-0 rounded-top">
            <img :src="pass.pass_type_image" class="img-fluid float-left" width="300" />
            <div class="card-body">
              <h5 class="card-title">{{ pass.pass_type }}</h5>
              <p class="card-text mt-3 rounded-bottom-0">
                <div class="border-bottom">Start Date:</div><div class="border-bottom ps-1">{{ pass.date_start }}</div>
                <div class="border-bottom">Expiry Date:</div><div class="border-bottom ps-1">{{ pass.date_expiry }}</div>
                <label class="orm-check-label mt-2">Renew Automatically</label>
                <div class="form-check form-switch mt-2 mx-auto">
                  <input class="form-check-input" type="checkbox" id="flexSwitchCheckDefault" v-model="pass.renew_automatically">
                </div>
              </p>
            </div>
          </div>
          <div class="card-footer border-top-0 align-items-center">
            <div><span class="badge" :class="statusClass(pass)">{{ pass.processing_status_display_name }}</span></div>
            <!--
            <button type="button" class="btn licensing-btn-primary btn-sm"><i class="fa-solid fa-car fa-lg"></i> Update Vehicle Rego</button>
            <button type="button" class="btn licensing-btn-primary btn-sm"><i class="fa-solid fa-file-invoice fa-lg"></i> Download Invoice</button>
            <button type="button" class="btn licensing-btn-primary btn-sm"><i class="fa-solid fa-file-pdf fa-lg"></i> Download Pass</button>
            -->
            <div class="link"><a @click="" data-bs-toggle="collapse" :href="'#updateVehicleRego'+pass.id" role="button" aria-expanded="false" :aria-controls="'updateVehicleRego'+pass.id">Update Vehicle Rego</a> <i class="fa-solid fa-car fa-lg ps-1"></i></div>
            <div class="link"><a href="">Download Invoice</a> <i class="fa-solid fa-file-invoice fa-lg ps-1"></i></div>
            <div class="link"><a :href="passURL(pass.id)" target="blank">Download Pass</a> <i class="fa-solid fa-file-pdf fa-lg ps-1"></i></div>
          </div>
          <div :id="'updateVehicleRego'+pass.id" class="showUpdateVehicleRego collapse">

            <div class="row">
              <div class="col">
                <input type="text" class="form-control form-control-sm m-3" placeholder="Vehicle 1 Registration" aria-label="Vehicle Registration 1" v-model="pass.vehicle_registration_1">
              </div>
              <div class="col">
                <input type="text" class="form-control form-control-sm m-3" placeholder="Vehicle 2 Registration" aria-label="Vehicle Registration 2" v-model="pass.vehicle_registration_2">
              </div>
              <div class="col">
                <button class="btn btn-sm licensing-btn-primary float-end m-3">Update</button>
              </div>
            </div>

          </div>
        </div>
    </div>

  </div>
</template>

<script>
import { apiEndpoints } from '@/utils/hooks'

export default {
  name: "externalDashboard",
  data: function () {
    return {
      loading: false,
      passes: null,
    }
  },
  components: {

  },
  computed: {

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
    fetchPasses: function () {
      let vm = this;
      vm.loading = true;
      fetch(apiEndpoints.passesListExternal)
        .then(async response => {
          const data = await response.json();
          if (!response.ok) {
            const error = (data && data.message) || response.statusText;
            console.log(error)
            return Promise.reject(error);
          }
          vm.passes = data.results
          vm.loading = false;
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
