import Ember from 'ember';

export default Ember.Controller.extend({
  uploadErrors: null,
  actions: {
    submit() {
      let $ = Ember.$;

      let form = $('#datasets-new-form');
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
        model.set('name', form_data['name']);
        model.set('format', form_data['format']);
        model.set('filename', form_data['file']);

        model.save().then(() => {
          that.transitionToRoute('datasets');
        }, () => {
          btnSubmit.attr('disabled', null);
        });
      }
    }
  }
});
