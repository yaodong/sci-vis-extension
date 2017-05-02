import DS from 'ember-data';

export default DS.Model.extend({
  job: DS.belongsTo('job'),
  name: DS.attr('string'),
  value: DS.attr()
});
