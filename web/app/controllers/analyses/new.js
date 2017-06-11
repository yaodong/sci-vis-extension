import Ember from 'ember';

export default Ember.Controller.extend({
  queryParams: ['dataset_id'],
  dataset_id: null,

  actions: {
    submit() {
      const that = this;
      const analysis = this.get('model.analysis');

      analysis.set('dataset', this.get('model.dataset'));

      analysis.save().then(() => {
        // that.transitionToRoute('datasets');
      });
    }
  }

});
