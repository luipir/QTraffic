/***************************************************************************
    A QGIS plugin for Road contamination modelling for EMSURE Project
                              -------------------
        begin                : 2015-04-20
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Luigi Pirelli (for EMSURE project)
        email                : luipir@gmail.lcom
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
// Dimensions of sunburst.
var width = 500;
var height = 450;
var radius = Math.min(width, height) / 2;
var innerHole = 10;

// Breadcrumb dimensions: width, height, spacing, width of tip/tail.
var b = {
    w: 100, h: 20, s: 3, t: 10
};

// make `colors` an ordinal scale
var colors = d3.scale.category20b();

var partition = d3.layout.partition()
  .sort(null)
  .size([2 * Math.PI, 100])
  .value(function(d) {
    return d.total;
  });

var arc = d3.svg.arc()
  .startAngle(function(d) { return d.x; })
  .endAngle(function(d) { return d.x + d.dx; })
  .innerRadius(function(d) {
    var innerRadius = d.y == 0 ? d.y+innerHole : d.y;
    return radius * Math.sqrt(innerRadius) / 10; 
  })
  .outerRadius(function(d) { return radius * Math.sqrt(d.y + d.dy) / 10; });

//loadTestData();

// Main function to draw and set up the visualization, once we have the data.
function createVisualization(vechicleName, json) {
    
    // Basic setup of page elements.
    initializeBreadcrumbTrail();
    initializeSunburst();
    initializeSliders();
    
    // open legend if toggled
    //d3.select("#togglelegend").on("click", toggleLegend);

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

    // make sure this is done after setting the domain
    drawLegend();
    
    // draw sunburst
    var g = vis.data([json]).selectAll("g")
            .data(nodes)
        .enter()
            .append("g");
    
    var path = g.append("path")
        .attr("d", arc)
        .attr("fill-rule", "evenodd")
        .style("fill", function(d) { return colors(d.name); })
        .style("opacity", 1)
        .on("mouseover.breadcrumb", mouseover)
        .on("mouseover.tooltip", showToolTip)
        .on("mouseout", hideToolTip)
        .on("click", showSliders)
        // for each path data save it in _current to have it as reference 
        // when angle is changed
        .each(function(d) { this._oldArc = d; console.log("added", this._oldArc); });

    // Add the mouseleave handler to the bounding circle.
    d3.select("#container").on("mouseleave", mouseleave);

    // show lagend activating checkbox
    //d3.select("#togglelegend").property('checked', true);
    //d3.select("#togglelegend").on("click")();

    // set vechicle name
    d3.select("#vechicle").text(vechicleName);
    //d3.select("#explanation").style("visibility", "");
    
    // open sliders on the fist node
    showSliders(json);
}

function showToolTip(d) {
    var tooltip = d3.select("#tooltip")
        .style("left", d3.event.pageX + "px")
        .style("top", d3.event.pageY + "px")
        .style("opacity", 1)
        .style("background-color", colors(d.name));
        
    tooltip.select("#value")
            .text(d.percentage + '%');
    tooltip.select("#arcName")
            .text(d.name);
}

function hideToolTip() {
    d3.select("#tooltip")
        .style("opacity", 0);;
}

function setColorLegend(json) {
    var ns = partition.nodes(json);
    
    var uniqueNames = (function(a) {
        var output = [];
        a.forEach(function(d) {
            if (output.indexOf(d.name) === -1) {
              output.push(d.name);
            }
        });
        return output;
    })(ns);
    
    // set domain of colors scale based on data
    colors.domain(uniqueNames);
}

// Fade all but the current sequence, and show it in the breadcrumb trail.
function mouseover(d) {
  
  var percentage = d.percentage;
  
  var percentageString = percentage + "%";
  if (percentage < 0.1) {
    percentageString = "< 0.1%";
  }

/*  d3.select("#percentage")
    //.text(percentageString);
    .text(vechicleName);

  d3.select("#  ")
    .style("visibility", "");
*/
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
    .duration(500)
    .style("opacity", 1)
    .each("end", function() {
      d3.select(this).on("mouseover", mouseover);
    });

/*  d3.select("#explanation")
    .transition()
    .duration(500)
    .style("visibility", "hidden");
*/
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
    if (typeof current.parent == 'undefined') {
        path.unshift(current);
    }
    return path;
}

function initializeBreadcrumbTrail() {
    // erase and set info box
    d3.select('#chart').html('');
    
    // Add the svg area.
    var trail = d3.select("#sequence").append("svg:svg")
        .attr("width", width)
        .attr("height", 20)
        .attr("id", "trail");
    // Add the label at the end, for the percentage.
    trail.append("svg:text")
        .attr("id", "endlabel")
        .style("fill", "#000");
}

// reset current sunburst and reinitialize to allow
// clean redraw
function initializeSunburst() {
    // erase and set info box
    // would be better to avoid add explanation here but leave in the html only and erase
    // only svg... but I've to focus on other part of the code
    d3.select('#chart').html('<div id="explanation"><span id="percentage"></span><span id="vechicle"></span></div>');
    
    translateX =  (width / 2)-25;
    translateY =  (height / 2);
    vis = d3.select("#chart").append("svg:svg")
      .attr("width", width)
      .attr("height", height)
      .append("svg:g")
      .attr("id", "container")
      .attr("transform", "translate(" + translateX + "," + translateY + ")");
}

// inizialize sliders to allow a clean redraw
function initializeSliders() {
    // erase and set info box
    d3.select('#infoBox').html('');
    d3.select('#rangebox tbody').html('');
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
    .style("fill", "#fff")
    .style("stroke", "none")
    //.style("stroke-width", 0.3)
    .text(function(d) { return d.name; });

  // Set position for entering and updating nodes.
  g.attr("transform", function(d, i) {
    return "translate(" + i * (b.w + b.s) + ", 0)";
  });

  // Remove exiting nodes.
  g.exit().remove();

  // Now move and update the percentage at the end.
  d3.select("#trail").select("#endlabel")
    .attr("x", (nodeArray.length+0.27) * (b.w + b.s))
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
    w: 100, h: 20, s: 3, r: 3
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

function showJson(vechicleName, jsonFromPython) {
    
    // set global json to allow its update from other function
    json = jsonFromPython;
    var vechicle = vechicleName;

    createVisualization(vechicle, json);
}

function loadTestData() {
    d3.json("FleetSplit-converted.json", function(error, data) {
        if (error) return console.warn(error);
        
        // show only Passenger Cars for test reason
        json = data["children"][0]["children"][1];
        
        createVisualization("Passenger cars", json);
    });
}

function findInJson(currentNode, compareNode) {
    // TODO: can be done with d3.select and filter ???
    if (typeof currentNode.parent != 'undefined') {
        if (currentNode.name == compareNode.name && 
            currentNode.depth == compareNode.depth &&
            currentNode.parent.name == compareNode.parent.name) {
            return currentNode;
        }
    } else {
        if (currentNode.name == compareNode.name && 
            currentNode.depth == compareNode.depth) {
            return currentNode;
        }
    }
        
    if (typeof currentNode.children == 'undefined') {
        return false;
    }
    
    for (var i=0; i < currentNode.children.length; i++) {
        var subNode = currentNode.children[i];
        var foundNode = findInJson(subNode, compareNode);
        if (foundNode) {
            return foundNode;
        }
    }
    return false;
}

function updateJsonData(d) {
    // modify the original JSON
    // on the input node basing on node value
    var foundNode = findInJson(json, d);
    if (!foundNode) return;
    
    // modify node to be equal to values set in sliders
    d3.selectAll('#rangebox .range').each(function () {
        index = parseInt(d3.select(this).attr('data-id'));
        foundNode.children[index].percentage = this.value / 10;
    });
}

function recomputeTotals(node) {
    // rematerialize all percentage
    if (typeof node.parent != 'undefined') {
        // do this only if is not the root node
        node.total = (node.parent.total * node.percentage) / 100;
    }
    node.value = node.total;
      
    // calc total for the children if any
    if (typeof node.children == 'undefined') return;
    for (var i=0; i < node.children.length; i++) {
        recomputeTotals(node.children[i]);
    }
}

function updateVis() {
    var nodes = partition.nodes(json);
    
    vis.selectAll("path")
            .data(nodes)
        .transition()
            .duration(700)
            .attr("d", arc);
            //.attrTween("d", arcTween);
}

// Store the displayed angles in _current.
// Then, interpolate from _current to the new angles.
// During the transition, _current is updated in-place by d3.interpolate.
function arcTween(d) {
    
    console.log(d)
    console.log(this._oldArc)
    console.log("------------------------")
    
    if (d === this._oldArc) {
        console.log("!!!!!!!!!!!!!!!!!!equals")
        return arc(d)
    }
    
    var i = d3.interpolate(this._oldArc, d);
    this._current = i(0);
    return function(t) {
        return arc(i(t));
    };
}


//////////////////////////////////////////////////////////
// Slider management
//////////////////////////////////////////////////////////

// Show sliders to allow arc editing
function showSliders(clickedNode) {
    // do nothing in case of last leaf
    if (typeof clickedNode.children == "undefined") {
        d3.select('#infoBox').html('');
        d3.select('#rangebox tbody').html('');
        return;
    }

    // remember the node currently shown
    currentSliderNode = clickedNode;
    
    // reset basic vars
    oldValue = [];
    moving_id = null;
    
    // erase and set info box
    var li = {
        w: 120, h: 30, s: 3, r: 3
    };
    
    var shift = 130;
    d3.select('#infoBox').html('');
    d3.select("#infoBox").append("svg:svg")
        .attr("width", li.w + shift)
        .attr("height", li.h)
        .append("svg:g")
            .attr("transform", function(d, i) {
                return "translate(" + (i  + shift) + ", 0)";
            });

    var g = d3.select("#infoBox").selectAll("g");
    g.append("svg:rect")
        .attr("rx", li.r)
        .attr("ry", li.r)
        .attr("width", li.w)
        .attr("height", li.h)
        .style("fill", function(d) { return colors(clickedNode.name); });
    g.append("svg:text")
        .attr("x", li.w / 2)
        .attr("y", li.h / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .text(function(d) { return clickedNode.name; });

    // erase previous sliders   
    d3.select('#rangebox tbody').html('');

    // append sliders to table
    for (i = 0; i < clickedNode.children.length; i++) {
        var label = clickedNode.children[i].name;
        var color = colors(label);
        
        var tr = d3.select('#rangebox tbody').append('tr');
        
        // create label
        var g = tr.append('td').append("svg")
            .attr("width", li.w)
            .attr("height", li.h)
            .append("svg:g");
        g.append("svg:rect")
            .attr("rx", li.r)
            .attr("ry", li.r)
            .attr("width", li.w)
            .attr("height", li.h)
            .style("fill", function(d) { return color; });
        g.append("svg:text")
            .attr("x", li.w / 2)
            .attr("y", li.h / 2)
            .attr("dy", "0.35em")
            .attr("text-anchor", "middle")
            .text(function(d) { return label; });
       
        // add slider with label and blocker checkbox
        tr.append('td')
            .append('input')
            .attr('type', 'range')
            .attr('data-id', i)
            .attr('class', 'range')
            .attr('step', 1)
            .attr('min', 0)
            .attr('max', 1000)
            .attr('contentEditable', true);
        tr.append('td')
            .attr('class', 'range_value');
        tr.append('td')
            .append('input')
            .attr('type', 'checkbox')
            .attr('class', 'lockCheckbox')
            .attr('data-id', i)
            .style('color', '#000')
            .style('opacity', 1)
            .attr('contentEditable', true);

        // memorize chidlren node of the current tr
        tr.attr('data-id', i);
        tr.on("mouseover", hilightAnchestors);
    }
        
    // set slider values depending of the clicked class
    d3.selectAll('#rangebox .range').each(function () {
        index = parseInt(d3.select(this).attr('data-id'));
        this.value = clickedNode.children[index].percentage*10;
        oldValue[index] = this.value;
    });
    
    //equalize(); // necessary only in case input data are not alrewady equilised
    showValues();
    
    // lock checkbox event prevent sliders to be editable
    // TODO: can be obtained with this.disable avoing to generate events
    d3.selectAll('.lockCheckbox').on('click', function () {
        var id = d3.select(this).attr('data-id');
        var locked = Boolean(this.checked);
        
        d3.selectAll('#rangebox .range')
            .filter(function() {return (d3.select(this).attr('data-id') == id); })
                .attr('contentEditable', !locked);
    });
    
    // slider event
    d3.selectAll('#rangebox .range').on('change', function () {
        
        moving_id = d3.select(this).attr('data-id');
        
        // if it's locked...don't move it
        // TODO: can be obtained with this.disable avoing to generate events
        if (this.contentEditable == 'false') {
            this.value = oldValue[moving_id];
            return;
        }
        
        // because range slider has TextLabelonly min/max and not dominum of validity
        // It's necessary to check if curent value is more than 
        // that allowed by (1000 - the sum of locked sliders)
        // - note 1000 because slideres are set from 0 to 1000 to have 1 digit precision -
        // this sum can be managed during checkbox clicked event
        // but I prefer to sum everytime, because it result more readable
        var rangeDomain = 1000;
        d3.selectAll('#rangebox .range')
            .filter(function() {return (d3.select(this).attr('contentEditable') == 'false'); })
                .each(function() {
                    rangeDomain -= parseInt(this.value); // casting to numeric with +
                });
        
        if (parseInt(this.value) > rangeDomain) {
            this.value = oldValue[moving_id];
            return;
        }
        
        this.value = parseInt(this.value);
        if (this.value < 0) this.value = 0;
        else if (this.value > 1000) this.value = 1000;
        
        var old_value = oldValue[moving_id];
        var new_value = this.value;
        
        // check how many sliders are not blocked
        var notLockedSliders = 0;
        d3.selectAll('#rangebox .range')
            .filter(function() {return (this.contentEditable == 'true'); })
                .each(function() {
                   notLockedSliders++; 
                });
        
        // if the current slider is the only remained unlocked then set
        // its value to the domain... that means force lock due the fact
        // that sum have to be 10000
        if (notLockedSliders == 1) {
            this.value = rangeDomain;
            oldValue[moving_id] = this.value;
            return;
        }
        
        // the moveed difference have to be distributed among
        // the remaining not locked sliders
        var delta = (new_value - old_value) / (notLockedSliders - 1);
        
        d3.selectAll('#rangebox .range')
            .filter(function() {return (this.contentEditable == 'true'); })
                .each(function () {
                    var r_id = d3.select(this).attr('data-id');
                    var r_val = this.value;
                    if (r_id != moving_id && r_val > delta) {
                        var equalized = parseInt(r_val - delta);
                        this.value = equalized;
                        oldValue[r_id] = this.value;
                    }
                });

        oldValue[moving_id] = new_value;
        
        // after distributed delta have to equilize values to avoid 
        // that sum would be greater the 1000
        equalize();
        
        // show slider value in %
        showValues();
        
        // perform JSOn update and recmpute of totals to
        // allow visualization update
        // without recopute totals, vis is not update
        // because sunburst is based on materialised percentage
        // and not on relative percentage
        updateJsonData(clickedNode);
        recomputeTotals(json);

        // update sunburst
        updateVis();
        
        // notify json modification to the python side
        // the d3PartitionCensor is used to remove d3 layout parameters added to json
        // that create a cyclic JSON and that add not original data
        var d3PurgedJson = JSON.stringify(json, d3PartitionCensor);
        sunburstEditorBridge.modifiedStatistic(d3PurgedJson);
    });
}

// show slider value
function showValues() {
  d3.selectAll('#rangebox .range').each(function () {
    var perct = (this.value / 10) + '%';
    d3.select(this.parentNode.nextSibling).html(perct);
  });
}

// get JSON data from sliders
function getSliderData() {
    var sliderData = [];
    d3.selectAll('#rangebox .range').each(function () {

      sliderData.push({
        label: d3.select(this.parentNode.parentNode)
            .select('td:first-child')
            .text(),
        value: this.value
      });
    });
    return sliderData;
}

// compute total percentage from sliders
function getCurrentSliderTotal() {
    var total = 0;
    d3.selectAll('#rangebox .range').each(function () {
        total = total + parseInt(this.value);
    });
    return total;
}

// equalize the sliders (decimal delta)
function equalize() {
  var remaining = 1000 - getCurrentSliderTotal();

  if (remaining != 0) {
    var to_eq = null;
    var min = null;
    var max = null;
    var min_value = 9999;
    var max_value = 0;

    d3.selectAll('#rangebox .range')
        .filter(function() {return (this.contentEditable == 'true'); })
            .each(function () {
                var id = d3.select(this).attr('data-id');
                
                if (id != moving_id) {
                    if (parseInt(this.value) > parseInt(max_value)) {
                        max_value = this.value;
                        max = this;
                    }
                    if (parseInt(this.value) < parseInt(min_value)) {
                        min_value = this.value;
                        min = this;
                    }
                }
            });

    if (remaining > 0) to_eq = min;
    else to_eq = max;

    if (to_eq) {
        if (remaining > 0) {
            to_eq.value = parseInt(to_eq.value) + 1;
            remaining = remaining - 1;
        } else {
            to_eq.value = parseInt(to_eq.value) - 1;
            remaining = remaining + 1;
        }
        oldValue[d3.select(to_eq).attr('data-id')] = to_eq.value;
    
        if (remaining != 0) equalize();
    }
  }
}

// hilight anchestor nodes of the current selected node
function hilightAnchestors() {
    if (!currentSliderNode){
        return;
    }

    // get current node index
    var i = d3.select(this).attr('data-id');

    // hilight current node anchestors
    var sequenceArray = getAncestors(currentSliderNode.children[i]);

    // Fade all the segments.
    d3.selectAll("path")
        .style("opacity", 0.25);

    // Then highlight only those that are an ancestor of the current segment.
    vis.selectAll("path")
        .filter(function(node) {
            return (sequenceArray.indexOf(node) >= 0);
        })
        .style("opacity", 1);
}

//////////////////////////////////////////////////////////
// utilities functions
//////////////////////////////////////////////////////////

// function to purge d3 added values to JSON. This function will be the censo in the JSON.stringify
function d3PartitionCensor(key, value) {
    if (key == 'parent' ||
        key == 'value' ||
        key == 'depth' ||
        key == 'x' ||
        key == 'y' ||
        key == 'dx' ||
        key == 'dy') {
        return undefined;
    }
    return value;   
}
