import Ember from 'ember';
const $ = Ember.$;
const d3 = window.d3;

// Version 0.0.0. Copyright 2017 Mike Bostock.
(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
    typeof define === 'function' && define.amd ? define(factory) :
      (global.versor = factory());
}(window, (function () {
  'use strict';

  var acos = Math.acos,
    asin = Math.asin,
    atan2 = Math.atan2,
    cos = Math.cos,
    max = Math.max,
    min = Math.min,
    PI = Math.PI,
    sin = Math.sin,
    sqrt = Math.sqrt,
    radians = PI / 180,
    degrees = 180 / PI;

// Returns the unit quaternion for the given Euler rotation angles [λ, φ, γ].
  function versor(e) {
    var l = e[0] / 2 * radians, sl = sin(l), cl = cos(l), // λ / 2
      p = e[1] / 2 * radians, sp = sin(p), cp = cos(p), // φ / 2
      g = e[2] / 2 * radians, sg = sin(g), cg = cos(g); // γ / 2
    return [
      cl * cp * cg + sl * sp * sg,
      sl * cp * cg - cl * sp * sg,
      cl * sp * cg + sl * cp * sg,
      cl * cp * sg - sl * sp * cg
    ];
  }

// Returns Cartesian coordinates [x, y, z] given spherical coordinates [λ, φ].
  versor.cartesian = function (e) {
    var l = e[0] * radians, p = e[1] * radians, cp = cos(p);
    return [cp * cos(l), cp * sin(l), sin(p)];
  };

// Returns the Euler rotation angles [λ, φ, γ] for the given quaternion.
  versor.rotation = function (q) {
    return [
      atan2(2 * (q[0] * q[1] + q[2] * q[3]), 1 - 2 * (q[1] * q[1] + q[2] * q[2])) * degrees,
      asin(max(-1, min(1, 2 * (q[0] * q[2] - q[3] * q[1])))) * degrees,
      atan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] * q[2] + q[3] * q[3])) * degrees
    ];
  };

// Returns the quaternion to rotate between two cartesian points on the sphere.
  versor.delta = function (v0, v1) {
    var w = cross(v0, v1), l = sqrt(dot(w, w));
    if (!l) return [1, 0, 0, 0];
    var t = acos(max(-1, min(1, dot(v0, v1)))) / 2, s = sin(t); // t = θ / 2
    return [cos(t), w[2] / l * s, -w[1] / l * s, w[0] / l * s];
  };

// Returns the quaternion that represents q0 * q1.
  versor.multiply = function (q0, q1) {
    return [
      q0[0] * q1[0] - q0[1] * q1[1] - q0[2] * q1[2] - q0[3] * q1[3],
      q0[0] * q1[1] + q0[1] * q1[0] + q0[2] * q1[3] - q0[3] * q1[2],
      q0[0] * q1[2] - q0[1] * q1[3] + q0[2] * q1[0] + q0[3] * q1[1],
      q0[0] * q1[3] + q0[1] * q1[2] - q0[2] * q1[1] + q0[3] * q1[0]
    ];
  };

  function cross(v0, v1) {
    return [
      v0[1] * v1[2] - v0[2] * v1[1],
      v0[2] * v1[0] - v0[0] * v1[2],
      v0[0] * v1[1] - v0[1] * v1[0]
    ];
  }

  function dot(v0, v1) {
    return v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2];
  }

  return versor;
})));

export default Ember.Component.extend({
  colors: [
    "#E1F5FE", // 1
    "#B2EBF2", // 2
    "#B2DFDB", // 3
    "#A5D6A7", // 4
    "#AED581", // 5
    "#D4E157", // 6
    "#FFEB3B", // 7
    "#FFB300", // 8
    "#F57C00", // 9
    "#BF360C", // 10
    "#8E24AA", // best
  ],

  /**
   * https://gist.github.com/serdaradali/11346541
   * https://bl.ocks.org/mbostock/7ea1dde508cec6d2d95306f92642bc42
   */
  didRender() {
    this._super(...arguments);

    var minDistance = this.get('outputs.best_projection')[2],
      maxDistance = this.get('outputs.worst_projection')[2],
      range = maxDistance - minDistance;

    var width = 960,
      height = 500,
      rotate = [10, -10],
      velocity = [.003, -.001],
      time = Date.now(),
      sens = 0.25;

    var projection = d3.geoOrthographic()
      .scale(240)
      .translate([width / 2, height / 2])
      .clipAngle(90 + 1e-6)
      .precision(.3);

    var path = d3.geoPath()
      .projection(projection);

    var graticule = d3.geoGraticule();

    var svg = d3.select("svg")
      .attr("width", width)
      .attr("height", height);

    svg.append("path")
      .datum({type: "Sphere"})
      .attr("class", "sphere")
      .attr("d", path);

    svg.append("path")
      .datum(graticule)
      .attr("class", "graticule")
      .attr("d", path);

    svg.append("path")
      .datum({type: "LineString", coordinates: [[-180, 0], [-90, 0], [0, 0], [90, 0], [180, 0]]})
      .attr("class", "equator")
      .attr("d", path);

    const colorRange = this.get('colors');

    let circleG = d3.geoCircle().radius(1.5).precision(90);
    $.map(this.get('outputs.bottleneck_distances'), function (d) {
      let zx_angle = d[0];
      let zy_angle = d[1];


      let color = null;
      if (d[2] == minDistance) {
        color = colorRange[10];
      } else {
        color = colorRange[parseInt((range - d[2]) / range * 10)];
      }
      svg.append("path")
        .datum(circleG.center([90 - zx_angle, 90 - zy_angle])())
        .style("fill", color);
    });

    svg.append("path")
      .datum(circleG.center([30, 30]))
      .attr("stroke", "red");

    svg.call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged));

    var render = function () {
      },
      v0, // Mouse position in Cartesian coordinates at start of drag gesture.
      r0, // Projection rotation as Euler angles at start.
      q0; // Projection rotation as versor at start.

    render = function () {
    };

    function dragstarted() {
      v0 = versor.cartesian(projection.invert(d3.mouse(this)));
      r0 = projection.rotate();
      q0 = versor(r0);
    }

    function dragged() {
      var v1 = versor.cartesian(projection.rotate(r0).invert(d3.mouse(this))),
        q1 = versor.multiply(q0, versor.delta(v0, v1)),
        r1 = versor.rotation(q1);
      projection.rotate(r1);
      svg.selectAll("path").attr("d", path);
    }


  }

  });
