import Ember from 'ember';

export default Ember.Controller.extend({
  uploadErrors: null,
  actions: {
    submit() {
      let $ = Ember.$;

      let form = $('#jobs-new-form');
      let btnSubmit = form.find('button[type=submit]');

      let model = this.get('model');
      let fileId = $("#files-picker-id").val();
      let that = this;

      if (!fileId) {
        this.set('uploadErrors', [
          { message: 'file required' }
        ]);
      } else {
        btnSubmit.attr('disabled', 'true');
        model.set('inputs', {
          file: form.find('#files-picker-id').val(),
        });

        model.set('method', form.find('input[name=method]').val());
        model.save().then(() => {
          that.transitionToRoute('jobs');
        }, () => {
          btnSubmit.attr('disabled', null);
        });
      }
    }
  }
});
