<template>
  <div class="container" id="internalOracleCodes">

    <div class="tab-content" id="pills-tabContent">
      <div
        class="tab-pane active"
        id="pills-oracle-codes"
        role="tabpanel"
        aria-labelledby="pills-oracle-codes-tab"
      >
        <FormSection
          :formCollapse="false"
          label="Oracle Codes"
          Index="oracle-codes"
        >

        <div v-if="oracleCodes && oracleCodes.length > 0">

          <div class="container mb-2">
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">District</label>
                        <select class="form-control w-30" v-model="selectedDistrict" @change="getFilteredOracleCodes()">
                          <option v-for="district in districts" :key="district">{{ district }}</option>
                        </select>
                    </div>
                </div>
            </div>
          </div>

          <form @submit.prevent @input="triggerUpdate()">
            <table class="table table-sm">
              <thead>
                <tr>
                  <th scope="col">District

                  </th>
                  <th scope="col">Pass Type</th>
                  <th scope="col">Pass Duration</th>
                  <th scope="col">Oracle Code</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(oracleCode, index) in filteredOracleCodes" :key="oracleCode.id">
                  <th v-if="index == 0">{{ oracleCode.district_name }}</th>
                  <th v-else-if="index > 0 && oracleCode.district_name != filteredOracleCodes[index-1].district_name">{{ oracleCode.district_name }}</th>
                  <th v-else>&nbsp;</th>
                  <td>{{ oracleCode.pass_type_display_name }}</td>
                  <td>{{ oracleCode.option_name }}</td>
                  <td class="col-md-4">
                    <input type="hidden" name="id" v-model="oracleCode.id" />
                    <input class="form-control" type="text" v-model="oracleCode.oracle_code" /></td>
                </tr>
              </tbody>
            </table>
          </form>

          <span v-if="updateCalled" class="badge bg-warning fs-6 d-flex align-items-center justify-content-center">
            <div class="spinner-border spinner-border-sm text-light" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <span class="ps-1">Editing</span>
          </span>
          <span v-else class="badge bg-success d-flex align-items-center justify-content-center">
            <i class="fa-solid fa-check fa-lg"></i>
            <span class="fs-6 ps-1 align-middle">Saved</span>
          </span>
        </div>

        <div v-else>
            <BootstrapSpinner :isLoading="true" />
        </div>

        <BootstrapAlert v-if="selectedDistrict == picaLabel" class="mt-3">
            Looking for the PICA oracle codes for local park passes? <a href="/admin/parkpasses/parkgroup/" target="_blank">Go here</a>
        </BootstrapAlert>

        <div v-if="systemErrorMessage" class="alert alert-danger" role="alert">
            {{ systemErrorMessage }}
        </div>

        </FormSection>

      </div>
    </div>
  </div>

</template>

<script>
import FormSection from "@/components/forms/SectionToggle.vue";
import BootstrapAlert from '@/utils/vue/BootstrapAlert.vue'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'
import BootstrapButtonSpinner from '@/utils/vue/BootstrapButtonSpinner.vue'

import { apiEndpoints, constants, helpers } from '@/utils/hooks'

export default {
    name: "InternalOracleCodes",
    data() {
        let vm = this;
        return {
            oracleCodes: [],
            filteredOracleCodes: [],
            districts: [],
            picaLabel: constants.PICA_LABEL,
            selectedDistrict: constants.PICA_LABEL,
            updateCalled: false,
            saveDelay: 1000,
            systemErrorMessage: null,
        };
    },
    components: {
        constants,
        FormSection,
        BootstrapAlert,
        BootstrapSpinner,
        BootstrapButtonSpinner,
    },
    computed: {

    },
    methods: {
        fetchOracleCodes: function(){
            let vm = this;
            fetch(apiEndpoints.oracleCodesListInternal)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    return Promise.reject(error);
                }
                vm.oracleCodes = data
                if(vm.oracleCodes && vm.oracleCodes.length > 0){
                  vm.getDistrictsFromOracleCodes();
                  vm.getFilteredOracleCodes();
                  console.log(vm.filteredOracleCodes)
                }
            })
            .catch(error => {
                //this.errorMessage = error;
                console.error("There was an error!", error);
            });
        },
        getDistrictsFromOracleCodes: function(){
            let vm = this;
            let districts = [];
            vm.oracleCodes.forEach(function(oracleCode){
                if (!districts.includes(oracleCode.district_name)){
                    districts.push(oracleCode.district_name);
                }
            });
            vm.districts = districts;
        },
        getFilteredOracleCodes: function(){
            let vm = this;
            let filteredOracleCodes = [];
            vm.oracleCodes.forEach(function(oracleCode){
                if (oracleCode.district_name == vm.selectedDistrict){
                    filteredOracleCodes.push(oracleCode);
                }
            });
            vm.filteredOracleCodes = filteredOracleCodes;
        },
        triggerUpdate: function(event) {
          let vm = this;
          console.log('calling triggerUpdate');
          if(!vm.updateCalled){
            vm.updateCalled = true;
            setTimeout(function(event) {
              vm.updateOracleCodes();
            }, vm.saveDelay);
          }
        },
        updateOracleCodes: function(event) {
          let vm = this;
          console.log('actually updating Oracle Codes');
          fetch(apiEndpoints.oracleCodesListUpdateInternal, {
              method: 'PATCH',
              body: JSON.stringify({
                'data':vm.filteredOracleCodes,
                'filter':vm.selectedDistrict
              }),
              headers: {
                'Content-type': 'application/json; charset=UTF-8',
              },
          }).then(async response => {
              if (!response.ok) {
                  const error = response.statusText;
                  return Promise.reject(error);
              }
              vm.updateCalled = false;
          })
          .catch(error => {
              //this.errorMessage = error;
              console.error("There was an error!", error);
          });
        }
    },
    created: function () {
        this.fetchOracleCodes();
    },
};
</script>

<style lang="css" scoped>
.badge {
  vertical-align: middle;
  width:100px;
  height:28px;
}
.bi-check{
  font-size: 2.5rem;
}
.section {
  text-transform: capitalize;
}
.list-group {
  margin-bottom: 0;
}
.fixed-top {
  position: fixed;
  top: 56px;
}

.nav-item {
  margin-bottom: 2px;
}

.nav-item > li > a {
  background-color: yellow !important;
  color: #fff;
}

.nav-item > li.active > a,
.nav-item > li.active > a:hover,
.nav-item > li.active > a:focus {
  color: white;
  background-color: blue;
  border: 1px solid #888888;
}

.admin > div {
  display: inline-block;
  vertical-align: top;
  margin-right: 1em;
}
.nav-pills .nav-link {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
  border-top-left-radius: 0.5em;
  border-top-right-radius: 0.5em;
  margin-right: 0.25em;
}
.nav-pills .nav-link {
  background: lightgray;
}
.nav-pills .nav-link.active {
  background: gray;
}
</style>
