import { defineStore } from 'pinia'
import { api_endpoints } from '@/utils/hooks'

export const useStore = defineStore('main', {
    state: () => ({
        userData: {
            isAuthenticated: false,
            authorisationLevel: 'external',
            retailerGroup: ''
        }
    }),
    actions: {
        async fetchUserData() {
            fetch(api_endpoints.userData)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                console.log(data);
                this.userData = data
            })
            .catch(error => {
                this.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
        }
    }
});