import Ember from 'ember';
const d3 = window.d3;

export default Ember.Component.extend({
  table: Ember.computed('outputs', function() {
    let colors = ["#ffffea", "#ffffd9", "#edf8b1", "#c7e9b4", "#7fcdbb", "#41b6c4", "#1d91c0", "#225ea8", "#253494", "#081d58"];
    let table = [[]];
    let min_distance = this.get('outputs.best_projection')[2];
    let max_distance = this.get('outputs.worst_projection')[2];
    let range = max_distance - min_distance;

    this.get('outputs.bottleneck_distances').forEach(function(d) {
      let [zx, zy, distance] = d;
      if (table[zx] === undefined) {
        table[zx] = [];
      }
      let percentage_range = (range - distance) / range * 10;
      let i = parseInt(percentage_range);
      let color = colors[i];
      if (min_distance === distance) {
        color = 'red';
      }
      table[zx][zy] = [distance, color, zx, zy];
    });

    let sorted = [];
    let angle_range = this.get('range');
    Ember.$.each(angle_range, function(idx, angle_out) {
      let sorted_row = [];
      Ember.$.each(angle_range, function(idx, angle_in) {
        sorted_row.push(table[angle_out][angle_in]);
      });
      sorted.push(sorted_row);
    });
    return sorted;
  }),

  range: Ember.computed(function() {
    let range = [];
    let cur = -90;
    while (cur < 90) {
      range.push(cur);
      cur += 5;
    }
    return range
  }),

  didRender() {
    this._super(...arguments);
    this.$("#hm .cell").each(function(index, cell) {
      let $cell = Ember.$(cell);
      $cell.css('background', $cell.data('color'));
    });
    let indexes = this.$("#hm td.index-column");
    let value = -90;
    Ember.$.each(indexes, function(idx, el) {
      Ember.$(el).text(value);
      value = value + 5;
    });
  }
});
