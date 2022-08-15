<template>
    <div>
        <h1>Buy a Park Pass Voucher</h1>

        <p>
            Enter the details of the person receiving the voucher, the voucher details
            and your own details and we will send the couvher with your text to the
            recipient at the selected date.
        </p>

        <div>
            <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
            <div class="row g-1 align-top mb-2">
                <div class="col-md-4">
                    <label for="amount" class="col-form-label">Voucher Amount</label>
                </div>
                <div class="col-auto">
                    <input type="number" id="amount" name="amount" v-model="voucher.amount" class="form-control" ref="amount" min="5" step="5" required="required" autofocus>
                    <div class="invalid-feedback">
                        Please enter a valid voucher amount.
                    </div>
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-md-4 mt-auto align-top">
                    <label for="recipientName" class="col-form-label">Recipient Name</label>
                </div>
                <div class="col-auto">
                    <input type="text" id="recipientName" name="recipientName" v-model="voucher.recipient_name" class="form-control" required="required">
                    <div class="invalid-feedback">
                        Please enter the recipient's name.
                    </div>
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-md-4">
                    <label for="recipientEmail" class="col-form-label">Recipient Email Address</label>
                </div>
                <div class="col-auto">
                    <input type="email" id="recipientEmail" name="recipientEmail" v-model="voucher.recipient_email" class="form-control" required="required">
                    <div class="invalid-feedback">
                        Please enter a valid email for the recipient.
                    </div>
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-md-4">
                    <label for="confirmRecipientEmail" class="col-form-label">Confirm Recipient Email Address</label>
                </div>
                <div class="col-auto">
                    <input @change="validateConfirmEmail" type="email" id="confirmRecipientEmail" name="confirmRecipientEmail" v-model="confirmRecipientEmail" ref="confirmRecipientEmail" class="form-control" required="required">
                    <div class="invalid-feedback">
                        Please make sure this email matches the recipient's email.
                    </div>
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-md-4">
                    <label for="personalMessage" class="col-form-label">Message to Recipient</label>
                </div>
                <div class="col-auto">
                    <textarea id="personalMessage" name="personalMessage" v-model="voucher.personal_message" class="form-control personalMessage" required="required"></textarea>
                    <div class="invalid-feedback">
                        Please enter a personal message for the recipient.
                    </div>
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-md-4 align-top">
                    <label for="datetimeToEmail" class="col-form-label">Date to Send the Voucher</label>
                </div>
                <div class="col-auto">
                    <input type="date" id="datetimeToEmail" name="datetimeToEmail" v-model="voucher.datetimeToEmail" class="form-control" required="required" :min="startDate()" :max="endDate()">
                </div>
                <div class="col-auto">
                    <i class="fa-solid fa-circle-question org-icon-primary" data-bs-toggle="tooltip" data-bs-placement="right" title="Leave as today to have the voucher sent immediately"></i>
                </div>
            </div>
            <!--
            <div class="row g-1 align-top mb-2">
                <div class="col-md-4">
                    <label for="firstName" class="col-form-label">Your First Name</label>
                </div>
                <div class="col-auto">
                    <input type="text" id="firstName" name="firstName" v-model="voucher.purchaser_first_name" class="form-control" ref="firstName" required="required">
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-md-4">
                    <label for="lastName" class="col-form-label">Your Last Name</label>
                </div>
                <div class="col-auto">
                    <input type="text" id="lastName" name="lastName" v-model="voucher.purchaser_last_name" class="form-control" required="required">
                </div>
            </div>

            <div class="row g-1 align-top mb-2">
                <div class="col-md-4">
                    <label for="email" class="col-form-label">Your Email Address</label>
                </div>
                <div class="col-auto">
                    <input type="email" id="email" name="email" v-model="voucher.purchaser_email" class="form-control" required="required">
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-md-4">
                    <label for="confirmEmail" class="col-form-label">Confirm Your Email</label>
                </div>
                <div class="col-auto">
                    <input type="email" id="confirmEmail" name="confirmEmail" v-model="confirm_purchaser_email" class="form-control" required="required">
                </div>
            </div>
            <div class="row g-1 align-top mb-2">
                <div class="col-md-4">
                    <label for="postcode" class="col-form-label">Your Postcode</label>
                </div>
                <div class="col-auto">
                    <input type="text" id="postcode" name="postcode" class="form-control" pattern="[0-9]{4}">
                </div>
            </div>
            -->
            <div class="row g-3mb-2">
                <div class="col-md-4">
                    &nbsp;
                </div>
                <div class="col-auto">
                    <button class="btn licensing-btn-primary px-5" type="submit">Next</button>
                </div>
            </div>
            </form>
        </div>
    </div>
</template>

<script>
import { apiEndpoints, helpers } from '@/utils/hooks'
import { useStore } from '@/stores/state'

export default {
    name: "PurchaseVoucher",
    data: function () {
        return {
            voucher: {
                amount: 5,
                datetimeToEmail: this.startDate(),
                recipient_email: ''
            },
            confirmRecipientEmail: '',
            store: useStore(),
        };
    },
    components: {
        apiEndpoints,
        helpers
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
                window.location.href = 'checkout/';
            })
            .catch(error => {
                this.systemErrorMessage = "ERROR: Please try again in an hour.";
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
        console.log(this.store.userData);
    }
};
</script>

<style scoped>
    .form-control{
        width:350px;
    }
    .personalMessage{
        height:200px;
    }
</style>
