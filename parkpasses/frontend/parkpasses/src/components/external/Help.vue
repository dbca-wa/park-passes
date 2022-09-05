<template>
    <div class="container" id="shopHome">
        <div class="row">
            <div class="col">
                <h1>Help</h1>
            </div>
        </div>
        <div class="row">
            <div class="col p-3">
                <div v-if="generalHelp" v-html="generalHelp.content" id="generalHelp">
                </div>

                <div v-if="systemErrorMessage" class="alert alert-danger" role="alert">
                    {{ systemErrorMessage }}
                </div>

                <div v-if="loading" class="d-flex justify-content-center mt-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<script>
import { apiEndpoints } from '@/utils/hooks'
import Loader from '@/utils/vue/Loader.vue'

export default {
    name: "Help",
    data: function () {
        return {
            generalHelp: null,
            loading: false,
            systemErrorMessage: null,
        };
    },
    components: {
        Loader
    },
    methods: {
        fetchGeneralHelp: function () {
            let vm = this;
            vm.loading = true;
            fetch(apiEndpoints.helpDetailByLabel('general'))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.generalHelp = data;
                vm.loading = false;
            })
            .catch(error => {
                this.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
        }
    },
    created: function() {
        this.fetchGeneralHelp();
    }
}

</script>

<style scoped>

</style>
