import Ember from 'ember';
import moment from 'moment';

export default Ember.Route.extend({
  model() {
    return this.get('store').createRecord('job', {
      name: 'run-' + moment().format('YYYYMMDD_HHmmss'),
      inputs: {},
      outputs: {},
      percentage: 1
    })
  },
  resetController(controller, isExiting) {
    if (isExiting) {
      let model = controller.get('model');
      if (!model.id) {
        model.destroyRecord();
      }
    }
  }
});
