import { defineStore } from 'pinia'
import { useSessionStorage } from '@vueuse/core'
import { apiEndpoints, constants } from '@/utils/hooks'

export const useStore = defineStore('main', {
    state: () => ({
        userData: useSessionStorage("userData", {
            user: {
                id: '',
                firstName: '',
                lastName: '',
                email: ''
            },
            is_authenticated: false,
            authorisation_level: 'external',
            retailerGroups: []
        })
    }),
    actions: {
        async fetchUserData() {
            fetch(apiEndpoints.userData)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                this.userData = data
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        }
    }
});
