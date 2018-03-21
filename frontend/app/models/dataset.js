import DS from 'ember-data';

export default DS.Model.extend({
  name: DS.attr('string'),
  fileName: DS.attr('string'),
  format: DS.attr('string'),
  createdAt: DS.attr('date'),
  analyses: DS.hasMany('analysis')
});
