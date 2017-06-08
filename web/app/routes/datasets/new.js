import Ember from 'ember';

export default Ember.Route.extend({
  model() {
    return this.get('store').createRecord('dataset', {
      name: 'run-' + moment().format('YYYYMMDD_HHmmss')
    });
  }
});
