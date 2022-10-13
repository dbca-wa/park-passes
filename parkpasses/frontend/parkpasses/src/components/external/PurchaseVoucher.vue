<template>
    <div>
        <h1>Buy a Park Pass Voucher</h1>

        <p>
            Enter the details of the person receiving the voucher, the voucher details
            and your own details and we will send the voucher with your text to the
            recipient at the selected date.
        </p>

        <div>
            <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
            <div class="row g-1 align-top mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    <label for="amount" class="col-form-label">Voucher Amount</label>
                </div>
                <div class="col-12 col-lg-12 col-xl-9">
                    <input type="number" id="amount" name="amount" v-model="voucher.amount" class="form-control" ref="amount" min="5" step="5" required="required">
                    <div class="invalid-feedback">
                        Please enter the voucher amount.
                    </div>
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    <label for="recipientName" class="col-form-label">Recipient Name</label>
                </div>
                <div class="col-12 col-lg-12 col-xl-9">
                    <input type="text" id="recipientName" name="recipientName" v-model="voucher.recipient_name" class="form-control" required="required">
                    <div class="invalid-feedback">
                        Please enter the recipient's name.
                    </div>
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    <label for="recipientEmail" class="col-form-label">Recipient Email Address</label>
                </div>
                <div class="col-12 col-lg-12 col-xl-9">
                    <input type="email" id="recipientEmail" name="recipientEmail" v-model="voucher.recipient_email" class="form-control" required="required">
                    <div class="invalid-feedback">
                        Please enter a valid email for the recipient.
                    </div>
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    <label for="confirmRecipientEmail" class="col-form-label">Confirm Recipient Email</label>
                </div>
                <div class="col-12 col-lg-12 col-xl-9">
                    <input @change="validateConfirmEmail" type="email" id="confirmRecipientEmail" name="confirmRecipientEmail" v-model="confirmRecipientEmail" ref="confirmRecipientEmail" class="form-control" required="required">
                    <div class="invalid-feedback">
                        Please make sure this email matches the recipient's email.
                    </div>
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    <label for="personalMessage" class="col-form-label">Message to Recipient</label>
                </div>
                <div class="col-12 col-lg-8 col-xl-9">
                    <textarea id="personalMessage" name="personalMessage" v-model="voucher.personal_message" class="form-control" style="min-width: 100%" rows="5" required="required"></textarea>
                    <div class="invalid-feedback">
                        Please enter a personal message for the recipient.
                    </div>
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    <label for="datetimeToEmail" class="col-form-label">Date to Send the Voucher</label>
                </div>
                <div class="col-12 col-lg-12 col-xl-3">
                    <input type="date" id="datetimeToEmail" name="datetimeToEmail" v-model="voucher.datetimeToEmail" class="form-control" required="required" :min="startDate()" :max="endDate()">
                </div>
                <div class="col-12 col-lg-12 col-xl-3">
                    <i class="fa-solid fa-circle-question org-icon-primary" data-bs-toggle="tooltip" data-bs-placement="right" title="Leave as today to have the voucher sent immediately"></i>
                </div>
            </div>
            <!--
            <div class="row g-1 align-top mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    <label for="firstName" class="col-form-label">Your First Name</label>
                </div>
                <div class="col-12 col-lg-12 col-xl-3">
                    <input type="text" id="firstName" name="firstName" v-model="voucher.purchaser_first_name" class="form-control" ref="firstName" required="required">
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    <label for="lastName" class="col-form-label">Your Last Name</label>
                </div>
                <div class="col-12 col-lg-12 col-xl-3">
                    <input type="text" id="lastName" name="lastName" v-model="voucher.purchaser_last_name" class="form-control" required="required">
                </div>
            </div>

            <div class="row g-1 align-top mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    <label for="email" class="col-form-label">Your Email Address</label>
                </div>
                <div class="col-12 col-lg-12 col-xl-3">
                    <input type="email" id="email" name="email" v-model="voucher.purchaser_email" class="form-control" required="required">
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    <label for="confirmEmail" class="col-form-label">Confirm Your Email</label>
                </div>
                <div class="col-12 col-lg-12 col-xl-3">
                    <input type="email" id="confirmEmail" name="confirmEmail" v-model="confirm_purchaser_email" class="form-control" required="required">
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    <label for="postcode" class="col-form-label">Your Postcode</label>
                </div>
                <div class="col-12 col-lg-12 col-xl-3">
                    <input type="text" id="postcode" name="postcode" class="form-control" pattern="[0-9]{4}">
                </div>
            </div>
            -->
            <div class="row g-3mb-2">
                <div class="col-12 col-lg-12 col-xl-3">
                    &nbsp;
                </div>
                <div class="col-12 col-lg-12 col-xl-3">
                    <button v-if="!isLoading" class="btn licensing-btn-primary px-5" type="submit">Next</button>
                    <BootstrapButtonSpinner v-else class="btn licensing-btn-primary px-5" />
                </div>
            </div>
            </form>
        </div>
    </div>
</template>

<script>
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import BootstrapButtonSpinner from '@/utils/vue/BootstrapButtonSpinner.vue'
import { useStore } from '@/stores/state'

export default {
    name: "PurchaseVoucher",
    title: "Buy a Park Pass Voucher",
    data: function () {
        return {
            voucher: {
                amount: 0,
                datetimeToEmail: this.startDate(),
                recipient_email: ''
            },
            confirmRecipientEmail: '',
            store: useStore(),
            isLoading: false,
        };
    },
    components: {
        apiEndpoints,
        helpers,
        BootstrapButtonSpinner,
    },
    computed: {

    },
    methods: {
        startDate: function () {
            const today = new Date();
            return today.toISOString().split('T')[0];
        },
        endDate: function () {
            let today = new Date();
            today.setFullYear(today.getFullYear() + 1);
            return today.toISOString().split('T')[0];
        },
        validateConfirmEmail: function () {
            console.log(this.voucher.recipient_email.length)
            if(this.voucher.recipient_email.length && this.confirmRecipientEmail.length){
                if(this.confirmRecipientEmail!=this.voucher.recipient_email){
                    this.$refs.confirmRecipientEmail.setCustomValidity("Invalid field.");
                    return false;
                } else {
                    this.$refs.confirmRecipientEmail.setCustomValidity("");
                }
            }
        },
        submitForm: function () {
            let vm = this;
            vm.isLoading = true;
            vm.voucher.datetime_to_email = new Date(vm.voucher.datetimeToEmail);
            vm.voucher.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.voucher)
            };
            fetch(apiEndpoints.saveVoucher, requestOptions)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                // Deliberately redirect here rather than router so session is forced to update
                // and re-render django template countaining cart item count.
                window.location.href = '/cart/';
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
            console.log(this.voucher);
            return false;
        },
        validateForm: function () {
            let vm = this;
            var forms = document.querySelectorAll('.needs-validation');

            this.validateConfirmEmail();

            Array.prototype.slice.call(forms)
            .forEach(function (form) {
                if(form.checkValidity()){
                    vm.submitForm();
                } else {
                    form.classList.add('was-validated');
                    $(".invalid-feedback:visible:first").siblings('input').focus();
                }
            });

            console.log(this.voucher);
            return false;
        }
    },
    created: function () {

    },
    mounted: function () {
        this.$refs.amount.focus();
    }
};
</script>

<style scoped>
h1 {
    font-size:1.2em;

}
p {
    font-size:0.9em;
}

@media (min-width: 576px) {
    h1 {
        font-size:1.3em;
    }
    p {
        font-size:0.9em;
    }
}

@media (min-width: 768px) {
    h1 {
        font-size:1.8em;
    }
    p {
        font-size:1em;
    }
}

@media (min-width: 992px) {
    h1 {
        font-size:1.8em;
    }
    p {
        font-size:1em;
    }
}

@media (min-width: 1200px) {
    h1 {
        font-size:2em;
    }
    p {
        font-size:1em;
    }
}

@media (min-width: 1400px) {
    h1 {
        font-size:2em;
    }
    p {
        font-size:1em;
    }
}

@media (min-width: 2560px) {
    h1 {
        font-size:3em;
    }
    p {
        font-size:1.3em;
    }
}
</style>
