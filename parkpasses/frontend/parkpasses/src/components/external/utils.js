import api from './api'
import {helpers} from '@/utils/hooks'

export default {
    fetchProfile: function (){
        return new Promise ((resolve,reject) => {
            fetch(api.profile).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });

    },
    fetchProposal: function(id){
        return new Promise ((resolve,reject) => {
            fetch(helpers.add_endpoint_json(api.proposals,id)).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });
    },
    fetchCountries: function (){
        return new Promise ((resolve,reject) => {
            fetch(api.countries).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });

    },
    fetchOrganisationPermissions: function(id){
        return new Promise ((resolve,reject) => {
            fetch(helpers.add_endpoint_json(api.my_organisations,id)).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });
    },
    fetchOrganisation: function(id){
        return new Promise ((resolve,reject) => {
            fetch(helpers.add_endpoint_json(api.organisations,id)).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });
    },
}
