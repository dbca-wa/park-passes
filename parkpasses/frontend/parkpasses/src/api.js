
module.exports = {

    /* ========================= Concessions ============================================*/

    concessions:                        "/api/concessions/concessions/?format=json",
    concession: function (id) {
        return                          `/api/concessions/concessions/${id}/?format=json`;
    },

    /* ========================= Passes =================================================*/

    passesPaginatedList:                '/api/passes/passes/',
    passProcessingStatusesDistinct:     "/api/passes/pass-processing-statuses-distinct?format=json",

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
    isVoucherValid: function (id) {
        return                          `to be implimented`;
    },
    createVoucher:                      "/api/vouchers/external/vouchers/",

    /* ========================= Cart Items =============================================*/

    checkout:                          "/api/cart/checkout/?format=json",

}
