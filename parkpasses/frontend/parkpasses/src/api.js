
module.exports = {
    passesPaginatedList: '/api/passes/passes/', // both for external and internal
    discard_proposal: function (id) {
        return `/api/proposal/${id}.json`;
    },
    passTypesDistinct:"/api/passes/pass-types-distinct?format=json",
    passProcessingStatusesDistinct:"/api/passes/pass-processing-statuses-distinct?format=json",
}
