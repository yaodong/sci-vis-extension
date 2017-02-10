import Ember from 'ember';
const $ = Ember.$;
const d3 = window.d3;

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

  didRender() {
    this._super(...arguments);

    /**
     * https://bl.ocks.org/alandunning/18c5ec8d06938edd31968e2fd104a58a
     */
    const tooltip = d3.select("body")
      .append("div")
      .style("position", "absolute")
      .style("z-index", "10")
      .style("visibility", "hidden")
      .style("background", "#FFF")
      .style("padding", "10px")
      .style("border", "1px solid #777")
      .style("border-radius", "3px")
      .text("");

    const svg = d3.select("#scatter"),
      borderColor = "#999",
      baseR = 6,
      hoverCircleR = 9,
      borderCircleColor = "#666",
      borderHoverColor = "#000",
      margin = {top: 50, right: 50, bottom: 50, left: 50},
      width = +svg.attr("width"),
      height = +svg.attr("height"),
      domainWidth = width - margin.left - margin.right,
      domainHeight = height - margin.top - margin.bottom,
      domain = [-90, 85],
      minDistance = this.get('outputs.best_projection')[2],
      maxDistance = this.get('outputs.worst_projection')[2],
      range = maxDistance - minDistance;

    const zx = d3.scaleLinear().domain(domain).range([0, domainWidth]);
    const zy = d3.scaleLinear().domain(domain).range([0, domainHeight]);
    const g = svg.append("g").attr("transform", "translate(" + margin.top + "," + margin.top + ")");

    g.append("rect")
      .attr("width", width - margin.left - margin.right)
      .attr("height", height - margin.top - margin.bottom)
      .attr("fill", "#FFF");

    const data = $.map(this.get('outputs.bottleneck_distances'), function (d) {
      return {
        zx: d[0],
        zy: d[1],
        dis: d[2],
      };
    });

    const colorRange = this.get('colors');

    const moveAxisPointer = function(cxValue, cyValue) {
      svg.select("#x-axis-pointer")
        .attr("fill", "black")
        .attr("points",  (cxValue - 5) + ",-40 " + cxValue + ",-30 " + (cxValue + 5) + ",-40");

      svg.select("#y-axis-pointer")
        .attr("fill", "black")
        .attr("points",  "-45," + (cyValue - 5) + "-35," + cyValue + " -45," + (cyValue + 5));
    };

    $("#svg-wrapper").hover(null, function () {
      g.selectAll(".dot").attr("r", baseR).attr("stroke", borderColor);
    });

    const onMouseMove = function (target) {
      let circle = $(target);
      let zxValue = parseInt(circle.data("zx"));
      let zyValue = parseInt(circle.data("zy"));
      let cxValue = parseFloat(circle.attr("cx"));
      let cyValue = parseFloat(circle.attr("cy"));
      let absX = Math.abs(zxValue);
      let absY = Math.abs(zyValue);

      moveAxisPointer(cxValue, cyValue);

      g.selectAll(".dot")
        .attr("r", baseR)
        .attr("stroke-dasharray", 0)
        .attr("stroke", borderColor);

      let absR = Math.max(absX, absY);
      if (absR < 90) {
        for (let step = 0; step <= absR; step += 5) {
          let points = [
            [-absR, +step],
            [-absR, -step],
            [+absR, +step],
            [+absR, -step],
            [+step, +absR],
            [-step, +absR],
            [+step, -absR],
            [-step, -absR],
          ];
          $.map(points, function (p) {
            g.select("circle.dot[data-zx='" + p[0] + "'][data-zy='" + p[1] + "']")
              .attr("stroke", borderCircleColor)
              .attr("stroke-dasharray", "4, 1")
              .attr("r", hoverCircleR);
          });
        }
      }

      g.select("circle.dot[data-zx='" + zxValue + "'][data-zy='" + zyValue + "']")
        .attr("stroke-dasharray", 0)
        .attr("stroke", borderHoverColor);
    };

    g.selectAll("circle")
      .data(data)
      .enter().append("circle")
      .attr("class", "dot")
      .attr("r", baseR)
      .attr("stroke", borderColor)
      .attr("data-dis", function (d) {
        return d.dis;
      })
      .attr("data-zx", function (d) {
        return d.zx;
      })
      .attr("data-zy", function (d) {
        return d.zy;
      })
      .attr("cx", function (d) {
        return zx(d.zx);
      })
      .attr("cy", function (d) {
        return zy(d.zy);
      })
      .style("fill", function (d) {
        if (d.dis == minDistance) {
          return colorRange[10];
        }
        return colorRange[parseInt((range - d.dis) / range * 10)];
      })
      .style("cursor", "pointer")
      .on("mouseover", function () {
        onMouseMove(this);
        return tooltip
          .style("visibility", "visible")
          .text($(this).data('dis'));
      })
      .on("mousemove", function () {
        return tooltip
          .style("top", (event.pageY - 10) + "px")
          .style("left", (event.pageX + 10) + "px");
      })
      .on("mouseout", function () {
        return tooltip.style("visibility", "hidden");
      });

    g.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + (zy.range()[0] - 10) + ")")
      .call(d3.axisTop(zx).ticks(36));

    g.append("g")
      .attr("class", "y axis")
      .attr("transform", "translate(-10, 0)")
      .call(d3.axisLeft(zy).ticks(36));

    g.append("polygon")
      .attr("id", "x-axis-pointer")
      .attr("points", "0,0 0,0 0,0")
      .attr("fill", "none")
      .attr("stroke", "none")
      .attr("stroke-width", 2);

    g.append("polygon")
      .attr("id", "y-axis-pointer")
      .attr("points", "0,0 0,0 0,0")
      .attr("fill", "none")
      .attr("stroke", "none")
      .attr("stroke-width", 2);

  }
});
