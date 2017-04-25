import Ember from 'ember';

export default Ember.Controller.extend({
  uploadErrors: null,
  actions: {
    submit() {
      let $ = Ember.$;

      let form = $('#jobs-new-form');
      let btnSubmit = form.find('button[type=submit]');

      let form_data = {};
      $.each(form.serializeArray(), function() {
        form_data[this.name] = this.value || '';
      });

      console.log(form_data);

      let model = this.get('model');
      let that = this;

      if (!form_data['file']) {
        this.set('uploadErrors', [
          { message: 'file required' }
        ]);
      } else {
        btnSubmit.attr('disabled', 'true');
        model.set('inputs', {
          file: form.find('#files-picker-id').val(),
          data_format: form_data['data_format']
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
