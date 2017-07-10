import Ember from 'ember';
import config from 'webapp/config/environment';

export default Ember.Component.extend({
  store: Ember.inject.service(),
  ajax: Ember.inject.service(),

  didInsertElement() {
    this._super(...arguments);

    this.get('ajax').post(config.APP.API_HOST + '/api/analyses/query', {
      data: {
        'analysis_id': this.get('analysis.id'),
        'function': 'best_linear_projection_iteration_chart'
      }
    }).then((response) => {
      this.set('data', response);
      this.plot();
    });
  },

  plot() {
    const d3 = window.d3;
    const data = this.get('data.iterations');

    // ref: https://bl.ocks.org/d3noob/c506ac45617cf9ed39337f99f8511218

    // set the dimensions and margins of the graph
    var margin = {top: 20, right: 20, bottom: 30, left: 50},
        width = 660 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    // set the ranges
    var x = d3.scaleLinear().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);

    // define the line
    var valueline = d3.line()
        .x(function(d) { return x(d['index']); })
        .y(function(d) { return y(d['distance']); });

    var svg = d3.select("svg#com-iteration-chart")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");

    // gridlines in x axis function
    function make_x_gridlines() {
      return d3.axisBottom(x).ticks(5);
    }

    // gridlines in y axis function
    function make_y_gridlines() {
      return d3.axisLeft(y).ticks(5);
    }

    // Scale the range of the data
    x.domain(d3.extent(data, function(d) { return d['index']; }));
    y.domain([d3.min(data, function(d) { return d['distance']; }) / 1.05, d3.max(data, function(d) { return d['distance']; }) * 1.05]);

    // add the X gridlines
    svg.append("g")
      .attr("class", "grid")
      .attr("transform", "translate(0," + height + ")")
      .call(make_x_gridlines()
            .tickSize(-height)
            .tickFormat(""));

    // add the Y gridlines
    svg.append("g")
      .attr("class", "grid")
      .call(make_y_gridlines()
            .tickSize(-width)
            .tickFormat(""));

    // add the valueline path.
    svg.append("path")
      .data([data])
      .attr("class", "line")
      .attr("d", valueline);

    // add the X Axis
    svg.append("g")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

    // add the Y Axis
    svg.append("g")
      .call(d3.axisLeft(y));


  }


});
