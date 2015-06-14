function validateForm(formId) {

    clearMessages();

    var inputs = $('#' + formId).find('input[required=true]');
    var errors = [];

    console.log(inputs);

    inputs.each(function() {
        var id = this.id;
        var val = $(this).val();

        if(val.length == 0) {
            var name = $("label[for=" + id + "]").text();
            errors.push(name + " is required.");
        }
    })

    if(!(errors.length === 0)) {
        pushMessage("<strong>Errors encountered while attempting to save:</strong><br>" + errors.join("<br>"), 'danger');
        return false;
    }
    return true;

}