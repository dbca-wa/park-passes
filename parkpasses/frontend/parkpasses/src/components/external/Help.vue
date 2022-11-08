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

                <div v-else>
                    <BootstrapSpinner :isLoading="true" />
                </div>

                <div v-if="systemErrorMessage" class="alert alert-danger" role="alert">
                    {{ systemErrorMessage }}
                </div>

            </div>
        </div>
    </div>

</template>

<script>
import { apiEndpoints, constants } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'

export default {
    name: "Help",
    data: function () {
        return {
            generalHelp: null,
            systemErrorMessage: null,
        };
    },
    components: {
        BootstrapSpinner
    },
    methods: {
        fetchGeneralHelp: function () {
            let vm = this;
            fetch(apiEndpoints.helpDetailByLabel('general'))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.generalHelp = data;
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
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
