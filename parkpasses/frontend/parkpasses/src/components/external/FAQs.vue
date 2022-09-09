<template>
    <div class="container" id="shopHome">
        <div class="row">
            <div class="col">
                <h1>FAQs</h1>
            </div>
        </div>
        <div class="row">
            <div class="col-md-3 p-3">
                <p>Maybe add some reassuring text here.</p>

                <p>Mauris a purus lorem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae;
                Nam sollicitudin lectus lacus. Morbi id nibh in mauris pharetra porta. Aliquam at lectus massa.
                Nulla elit dolor, fermentum quis dignissim id, finibus quis purus. Donec sed efficitur metus, nec sagittis neque.
                Sed at aliquam turpis. Cras mauris felis, rhoncus nec turpis ac, eleifend imperdiet dui.</p>

                <p>Proin aliquam pulvinar neque, pharetra cursus libero auctor eu. Ut hendrerit eros at nisl efficitur blandit.
                Proin luctus gravida tortor. Fusce ut diam eu augue sollicitudin fringilla. Praesent accumsan ultricies porttitor.
                Nam sollicitudin condimentum nisi, eget vulputate magna varius sollicitudin.</p>

                <p>Integer vel erat aliquam, viverra dolor eu, interdum augue. Sed magna purus, accumsan id suscipit at, gravida ac nisl.</p>
            </div>
            <div class="col-md-8">

                <div v-if="faqs" class="accordion my-3" id="faqAccordian">

                    <div v-for="(faq, index) in faqs" class="accordion-item">
                        <h2 class="accordion-header" :id="'heading' + index">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" :data-bs-target="'#collapse' + index" :aria-expanded="index==0" :aria-controls="'collapse' + index">
                                {{ index+1 }}. {{ faq.question }}
                            </button>
                        </h2>
                        <div :id="'collapse' + index" class="accordion-collapse collapse" :class="index ? '' : 'show' " :aria-labelledby="'heading' + index" data-bs-parent="#faqAccordian">
                            <div class="accordion-body">
                            {{ faq.answer }}
                            </div>
                        </div>
                    </div>

                </div>
                <div v-else>
                    <BootstrapSpinner isLoading="true" />
                </div>
            </div>
        </div>
    </div>

</template>

<script>
import { apiEndpoints } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'

export default {
    name: "FAQs",
    data: function () {
        return {
            faqs: null
        };
    },
    components: {
        BootstrapSpinner
    },
    methods: {
        fetchFAQs: function () {
            let vm = this;
            fetch(apiEndpoints.faqsList)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.faqs = data.results
            })
            .catch(error => {
                this.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
        },
    },
    created: function() {
        this.fetchFAQs();
    }
};
</script>

<style scoped>

</style>
