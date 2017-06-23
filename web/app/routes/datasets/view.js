import Ember from 'ember';

export default Ember.Route.extend({

  model(params) {
    return this.get('store').findRecord('dataset', params.id);
  },

  setupController(controller, model) {
    this._super(controller, model);
  }
});
