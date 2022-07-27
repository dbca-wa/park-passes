
module.exports = {

    /* ========================= User Data =============================================*/

    userData:                           "/api/users/user-data/?format=json",

    /* ========================= Concessions ============================================*/

    concessions:                        "/api/concessions/concessions/?format=json",
    concession: function (id) {
        return                          `/api/concessions/concessions/${id}/?format=json`;
    },

    /* ========================= Passes =================================================*/

    passesPaginatedList:                '/api/passes/passes/',
    passProcessingStatusesDistinct:     "/api/passes/pass-processing-statuses-distinct?format=json",
    createPass:                         '/api/passes/external/passes',

    /* ========================= Pass Types =============================================*/

    passTypesDistinct:                  "/api/passes/pass-types-distinct?format=json",
    passTypes:                          "/api/passes/pass-types?format=json",
    passType: function (id) {
        return                          `/api/passes/pass-types/${id}/?format=json`;
    },

    /* ========================= Pass Options ===========================================*/

    passOptions: function (id) {
        return                          `/api/passes/pass-options-by-pass-type-id?pass_type_id=${id}`;
    },

    /* ========================= Discount Codes =========================================*/
    isDiscountCodeValid: function (id) {
        return                          `to be implimented`;
    },

    /* ========================= Vouchers ===============================================*/
    isVoucherValid: function (recipient_email, code, pin) {
        return                          `/api/vouchers/validate-voucher?recipient_email=${recipient_email}&code=${code}&pin=${pin}`;
    },
    createVoucher:                      "/api/vouchers/external/vouchers/",

    /* ========================= Postcodes ===============================================*/
    isPostcodeValid: function (postcode) {
        return                          `/api/parks/validate-postcode?postcode=${postcode}`;
    },
    parkGroupsForPostcode: function (postcode) {
        return                          `/api/parks/park-groups-for-postcode?postcode=${postcode}`;
    },

    /* ========================= Cart Items =============================================*/

    checkout:                          "/api/cart/checkout/?format=json",

}
