import { apiEndpoints, constants } from '@/utils/hooks'

export default {
    uploadOrgModelDocuments: function(contentType, objectId, files){
        for(let i=0;i<files.length;i++){
            console.log(files[0]);
            let formData = new FormData();
            formData.append('content_type', contentType);
            formData.append('object_id', objectId);
            formData.append('_file', files[i]);
            fetch(apiEndpoints.uploadOrgModelDocuments, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'multipart/form-data'
                },
                body: formData
            }).then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    this.errors = data;
                    return Promise.reject(error);
                }
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        }
    },
}
