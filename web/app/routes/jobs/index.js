import Ember from 'ember';

export default Ember.Route.extend({
  model() {
    let interval = 1000 * 30;
    Ember.run.later(this, function() {
      this.model().then(function(json) {
        this.controller.set('model', json);
      }.bind(this));
    }, interval);

    return this.get('store').findAll('job').then(function (jobs) {
      return jobs.sortBy('-id');
    });
  }
});
