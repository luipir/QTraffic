// Dimensions of sunburst.
var width = 450;
var height = 450;
var radius = Math.min(width, height) / 2;

// Breadcrumb dimensions: width, height, spacing, width of tip/tail.
var b = {
    w: 75, h: 30, s: 3, t: 10
};

// make `colors` an ordinal scale
var colors = d3.scale.category20b();

var vis = d3.select("#chart").append("svg:svg")
    .attr("width", width)
    .attr("height", height)
    .append("svg:g")
    .attr("id", "container")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

var partition = d3.layout.partition()
    .size([2 * Math.PI, 100])
    .value(function(d) {
    	return d.total;
    });

var arc2 = d3.svg.arc()
    .startAngle(function(d) { return d.x; })
    .endAngle(function(d) { return d.x + d.dx; })
    .innerRadius(function(d) { return radius * Math.sqrt(d.y) / 10; })
    .outerRadius(function(d) { return radius * Math.sqrt(d.y + d.dy) / 10; });
    //.innerRadius(function(d) { return radius * (d.y) / 100; })
    //.outerRadius(function(d) { return radius * (d.y + d.dy) / 100; });

loadData();






// Main function to draw and set up the visualization, once we have the data.
function createVisualization(json) {

    // Basic setup of page elements.
    initializeBreadcrumbTrail();
  
    d3.select("#togglelegend").on("click", toggleLegend);

    // Bounding circle underneath the sunburst, to make it easier to detect
    // when the mouse leaves the parent g.
    vis.append("svg:circle")
        .attr("r", radius)
        .style("opacity", 0);

    // For efficiency, filter nodes to keep only those large enough to see.
    var nodes = partition.nodes(json);
        //.filter(function(d) {
        //    return (d.dx > 0.005); // 0.005 radians = 0.29 degrees
        //});
  
    var uniqueNames = (function(a) {
        var output = [];
        a.forEach(function(d) {
            if (output.indexOf(d.name) === -1) {
                output.push(d.name);
            }
        });
        return output;
    })(nodes);
    
    // set domain of colors scale based on data
    colors.domain(uniqueNames);
    
    // make sure this is done after setting the domain
    drawLegend();
        
    var path = vis.data([json]).selectAll("path")
        .data(nodes)
       .enter()
        .append("svg:path")
        .attr("display", function(d) { return d.depth ? null : "none"; })
        .attr("d", arc2)
        .attr("fill-rule", "evenodd")
        .style("fill", function(d) { return colors(d.name); })
        .style("opacity", 1)
        .on("mouseover", mouseover)
        .on("click", showSliders);

    // Add the mouseleave handler to the bounding circle.
    d3.select("#container").on("mouseleave", mouseleave);

    // show lagend activating checkbox
	d3.select("#togglelegend").property('checked', true);
	d3.select("#togglelegend").on("click")();
};

// Show sliders to allow arc editing
function showSliders(d) {
	// do nothing in case of last leaf
	if (typeof d.children == "undefined") return;

	numOfchildrens = d.children.length;
	
	// reset basic vars
    oldValue = [];

	// erase previous sliders	
    d3.select('#rangebox tbody').html('');

    // append sliders to table
    for (i = 0; i < numOfchildrens; i++) {
    	label = d.children[i].name
    
        var tr = d3.select('#rangebox tbody').append('tr');
        tr.append('td')
            .attr('class', 'edit')
            .attr('contenteditable', false)
            .text(label);
        tr.append('td')
            .append('input')
            .attr('type', 'range')
            .attr('data-id', i)
            .attr('class', 'range')
            .attr('step', 1)
            .attr('min', 0)
            .attr('max', 100);
        tr.append('td')
            .attr('class', 'range_value');
    }
    
    // set slider values depending of the clicked class
    d3.selectAll('#rangebox .range').each(function () {
        index = parseInt(d3.select(this).attr('data-id'));
        this.value = d.children[index].percentage;
        oldValue[index] = this.value;
    });


}

// Fade all but the current sequence, and show it in the breadcrumb trail.
function mouseover(d) {
  
  var percentage = d.percentage;
  
  var percentageString = percentage + "%";
  if (percentage < 0.1) {
    percentageString = "< 0.1%";
  }

  d3.select("#percentage")
      .text(percentageString);

  d3.select("#explanation")
      .style("visibility", "");

  var sequenceArray = getAncestors(d);
  updateBreadcrumbs(sequenceArray, percentageString);

  // Fade all the segments.
  d3.selectAll("path")
      .style("opacity", 0.3);

  // Then highlight only those that are an ancestor of the current segment.
  vis.selectAll("path")
      .filter(function(node) {
                return (sequenceArray.indexOf(node) >= 0);
              })
      .style("opacity", 1);
}

// Restore everything to full opacity when moving off the visualization.
function mouseleave(d) {

  // Hide the breadcrumb trail
  d3.select("#trail")
      .style("visibility", "hidden");

  // Deactivate all segments during transition.
  d3.selectAll("path").on("mouseover", null);

  // Transition each segment to full opacity and then reactivate it.
  d3.selectAll("path")
      .transition()
      .duration(1000)
      .style("opacity", 1)
      .each("end", function() {
              d3.select(this).on("mouseover", mouseover);
            });

  d3.select("#explanation")
      .transition()
      .duration(1000)
      .style("visibility", "hidden");
}

// Given a node in a partition layout, return an array of all of its ancestor
// nodes, highest first, but excluding the root.
function getAncestors(node) {
  var path = [];
  var current = node;
  while (current.parent) {
    path.unshift(current);
    current = current.parent;
  }
  return path;
}

function initializeBreadcrumbTrail() {
  // Add the svg area.
  var trail = d3.select("#sequence").append("svg:svg")
      .attr("width", width)
      .attr("height", 50)
      .attr("id", "trail");
  // Add the label at the end, for the percentage.
  trail.append("svg:text")
    .attr("id", "endlabel")
    .style("fill", "#000");
}

// Generate a string that describes the points of a breadcrumb polygon.
function breadcrumbPoints(d, i) {
  var points = [];
  points.push("0,0");
  points.push(b.w + ",0");
  points.push(b.w + b.t + "," + (b.h / 2));
  points.push(b.w + "," + b.h);
  points.push("0," + b.h);
  if (i > 0) { // Leftmost breadcrumb; don't include 6th vertex.
    points.push(b.t + "," + (b.h / 2));
  }
  return points.join(" ");
}

// Update the breadcrumb trail to show the current sequence and percentage.
function updateBreadcrumbs(nodeArray, percentageString) {

  // Data join; key function combines name and depth (= position in sequence).
  var g = d3.select("#trail")
      .selectAll("g")
      .data(nodeArray, function(d) { return d.name + d.depth; });

  // Add breadcrumb and label for entering nodes.
  var entering = g.enter().append("svg:g");

  entering.append("svg:polygon")
      .attr("points", breadcrumbPoints)
      .style("fill", function(d) { return colors(d.name); });

  entering.append("svg:text")
      .attr("x", (b.w + b.t) / 2)
      .attr("y", b.h / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", "middle")
      .text(function(d) { return d.name; });

  // Set position for entering and updating nodes.
  g.attr("transform", function(d, i) {
    return "translate(" + i * (b.w + b.s) + ", 0)";
  });

  // Remove exiting nodes.
  g.exit().remove();

  // Now move and update the percentage at the end.
  d3.select("#trail").select("#endlabel")
      .attr("x", (nodeArray.length + 0.5) * (b.w + b.s))
      .attr("y", b.h / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", "middle")
      .text(percentageString);

  // Make the breadcrumb trail visible, if it's hidden.
  d3.select("#trail")
      .style("visibility", "");

}

function drawLegend() {

  // Dimensions of legend item: width, height, spacing, radius of rounded rect.
  var li = {
    w: 75, h: 30, s: 3, r: 3
  };

  var legend = d3.select("#legend").append("svg:svg")
      .attr("width", li.w)
      .attr("height", colors.domain().length * (li.h + li.s));

  var g = legend.selectAll("g")
      .data(colors.domain())
      .enter().append("svg:g")
      .attr("transform", function(d, i) {
              return "translate(0," + i * (li.h + li.s) + ")";
           });

  g.append("svg:rect")
      .attr("rx", li.r)
      .attr("ry", li.r)
      .attr("width", li.w)
      .attr("height", li.h)
      .style("fill", function(d) { return colors(d); });

  g.append("svg:text")
      .attr("x", li.w / 2)
      .attr("y", li.h / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", "middle")
      .text(function(d) { return d; });
}

function toggleLegend() {
  var legend = d3.select("#legend");
  if (legend.style("visibility") == "hidden") {
    legend.style("visibility", "");
  } else {
    legend.style("visibility", "hidden");
  }
}

function loadData() {
	d3.json("FleetSplit-converted.json", function(error, json) {
	  if (error) return console.warn(error);
	  
	  json = json;
	  
	  // show only Passenger Cars
	  json = json["children"][0]["children"][1];
	  
	  console.log(json);
	  
	  createVisualization(json);
	});
};
