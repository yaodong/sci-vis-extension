import Ember from 'ember';

export default Ember.Route.extend({
  model(params) {
    return {
      job: this.get('store').findRecord('job', params.id),
      outputs: null
    };
  }
});
