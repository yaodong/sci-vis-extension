import Ember from 'ember';

export default Ember.Route.extend({
  model() {
    let interval = 1000 * 30;
    Ember.run.later(this, () => {
      this.model().then(function(json) {
        this.controller.set('model', json);
      }.bind(this));
    }, interval);

    return this.get('store').findAll('job', { reload: true }).then((jobs) => {
      return jobs.sortBy('-id');
    });
  }
});
