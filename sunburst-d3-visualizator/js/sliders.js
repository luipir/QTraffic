var nb_sliders = null; // nb of range sliders
var moving_id = null; // id of the moved slider
var oldValue = []; // previous values of the sliders

var radius = 150; // pie chart radius
var color = d3.scale.category20(); // color scheme (10, 20, 20b, 20c ...)
var pi = Math.PI; // 3.14

// pie chart config
var pie = d3.layout.pie()
    .value(function (d) {
    return d.value;
})
//.startAngle(-90 * (pi/180))
//.endAngle(90 * (pi/180))
.sort(null);

// arc object
var arc = d3.svg.arc()
    .outerRadius(radius)
    .innerRadius(radius / 2);

// nb sliders event
d3.select('#nbFormSubmit').on('click', function () {
    d3.event.preventDefault();
    nb_sliders = d3.select('#nbSliders')[0][0].value;
    init();
});

// initialize the sliders, events and pie chart
function init() {
    oldValue = [];
    moving_id = null;

    d3.select('#rangebox tbody').html('');

    // append sliders to table
    for (i = 0; i < nb_sliders; i++) {
        var tr = d3.select('#rangebox tbody').append('tr');
        tr.append('td')
            .attr('class', 'edit')
            .attr('contenteditable', true)
            .text('Label ' + (i + 1));
        tr.append('td')
            .append('input')
            .attr('type', 'range')
            .attr('data-id', i)
            .attr('class', 'range')
            .attr('step', 1)
            .attr('min', 0)
            .attr('max', 1000);
        tr.append('td')
            .attr('class', 'range_value');
    }

    d3.selectAll('#rangebox .range').each(function () {
        var def = parseInt(1000 / nb_sliders);
        this.value = def;
        oldValue[d3.select(this).attr('data-id')] = this.value;
    });

    equalize();
    showValues();
    pieChart();

    // content edit event
    d3.selectAll('.edit').on('input', function () {
        updateLabels();
    });

    // slider event
    d3.selectAll('.range').on('change', function () {
        this.value = parseInt(this.value);
        if (this.value < 0) this.value = 0;
        else if (this.value > 1000) this.value = 1000;

        var id = d3.select(this).attr('data-id');
        moving_id = id;

        var old_value = oldValue[moving_id];
        var new_value = this.value;
        var delta = (new_value - old_value) / (nb_sliders - 1);

        d3.selectAll('#rangebox .range').each(function () {
            var r_id = d3.select(this).attr('data-id');
            var r_val = this.value;
            if (r_id != moving_id && r_val > delta) {
                var equalized = parseInt(r_val - delta);
                this.value = equalized;
                oldValue[r_id] = this.value;
            }
        });

        oldValue[moving_id] = new_value;

        equalize();
        showValues();
        updatePieChart();
    });
}

// get JSON data from sliders
function getData() {
    var json = [];
    d3.selectAll('#rangebox .range').each(function () {

        json.push({
            label: d3.select(this.parentNode.parentNode)
                .select('td:first-child')
                .text(),
            value: this.value
        });
    });
    return json;
}

// compute total percentage from sliders
function getTotal() {
    var total = 0;
    d3.selectAll('#rangebox .range').each(function () {
        total = total + parseInt(this.value);
    });
    return total;
}

// equalize the sliders (decimal delta)
function equalize() {
    var remaining = 1000 - getTotal();

    if (remaining != 0) {
        var to_eq = null;
        var min = null;
        var max = null;
        var min_value = 9999;
        var max_value = 0;

        // console.log(remaining);

        d3.selectAll('#rangebox .range').each(function () {
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

// show slider value
function showValues() {
    d3.selectAll('#rangebox .range').each(function () {
        var perct = (this.value / 10) + '%';
        d3.select(this.parentNode.nextSibling).html(perct);
    });
}

// draw pie chart
function pieChart() {
    var json = getData();

    d3.select("#pie svg").remove();

    // svg canvas
    var svg = d3.select("#pie")
        .append("svg:svg")
        .attr("width", radius * 2)
        .attr("height", radius * 2)
        .append("svg:g")
        .attr("transform", "translate(" + radius + "," + radius + ")");

    // slices
    var arcs = svg.selectAll("path").data(pie(getData()));

    // render the slices
    arcs.enter()
        .append('svg:path')
        .attr("fill", function (d, i) {
        return color(i);
    })
        .attr("d", arc)
        .each(function (d) {
        this._current = d;
    })
        .append('title')
        .text(function (d, i) {
        return json[i].value + '%';
    });

    // render the labels
    arcs.enter()
        .append("svg:text")
        .attr("transform", function (d) {
        return "translate(" + arc.centroid(d) + ")";
    })
        .attr("text-anchor", "middle")
        .text(function (d, i) {
        if (json[i].value > 1) return json[i].label;
        else return null;
    });
}

// update pie chart
function updatePieChart() {
    updateArcs();
    updateLabels();
}

// update the slices of the pie chart
function updateArcs() {
    var json = getData();

    d3.selectAll("#pie path title")
        .text(function (d, i) {
        return (parseInt(json[i].value) / 10) + '%';
    });

    d3.selectAll("#pie path")
        .data(pie(json))
        .transition()
        .duration(700)
        .attrTween('d', arcTween);
}

// update the labels of the pie chart
function updateLabels() {
    d3.selectAll("#pie text")
        .data(pie(getData()))
        .transition()
        .duration(700)
        .attr("transform", function (d) {
        return "translate(" + arc.centroid(d) + ")";
    })
        .text(function (d, i) {
        if (getData()[i].value > 0) return getData()[i].label;
        else return null;
    });
}

// transition for the arcs
function arcTween(a) {
    var i = d3.interpolate(this._current, a);
    this._current = i(0);
    return function (t) {
        return arc(i(t));
    };
}