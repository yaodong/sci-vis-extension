import Ember from 'ember';

export default Ember.Route.extend({

  model(params) {
    return this.get('store').findRecord('job', params.id);
  },

  activate() {
    this.controllerFor('jobs.view').set("selectedIndex", null);
  }
});
