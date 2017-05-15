import Ember from 'ember';

export default Ember.Route.extend({
  model() {
    return this.get('store').findAll('job', {reload: true}).then((jobs) => {
      return jobs.sortBy('-id');
    });
  },

  afterModel(posts) {
    let interval = 1000 * 10;

    let bindReloading = function(job) {
      if (job.get('progress') < 100 && job.get('status') == -1) {
        Ember.run.later(this, (p) => {
          p.reload().then(bindReloading);
        }, job, interval);
      }
    };

    Ember.$.map(posts, (post) => {
      bindReloading(post);
    });

  }
});
