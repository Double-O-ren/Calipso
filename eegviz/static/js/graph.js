limit = 60 * 2;
duration = 750;
now = new Date(Date.now() - duration);

graphs = {
    graph1: {
	groups: {
	    heart: {
		value: 0,
		color: 'blue',
		data: d3.range(limit).map(function() {
		    return 0
		})
	    }
	}
    },
    graph2: {
    groups: {
        hrv: {
        value: 0,
        color: 'red',
        data: d3.range(limit).map(function() {
            return 0
        })
        }
    }
    },
    graph3: {
    groups: {
        brain: {
        value: 0,
        color: 'green',
        data: d3.range(limit).map(function() {
            return 0
        })
        }
    }
    }
}

function initGraphs(){
    width = $(window).width();
    height = $(window).height() / 3.5;

    for(var graph_name in graphs){
	var graph = graphs[graph_name];
	$('body').append("<div class='" + graph_name + " graph'></div><br/>")
	graph.svg = d3.select('.' + graph_name).append('svg')
            .attr('class', 'chart')
            .attr('width', width)
            .attr('height', height + 50)

	graph.x = d3.time.scale()
            .domain([now - (limit - 2), now - duration])
            .range([0, width])

	graph.y = d3.scale.linear()
            .domain([0, 100])
            .range([height, 0])

	graph.line = d3.svg.line()
            .interpolate('basis')
            .x(function(d, i) {
		return graph.x(now - (limit - 1 - i) * duration)
            })
            .y(function(d) {
		return graph.y(d)
            })

	graph.axis = graph.svg.append('g')
            .attr('class', 'x axis')
            .attr('transform', 'translate(0,' + height + ')')
            .call(graph.x.axis = d3.svg.axis().scale(graph.x).orient('bottom'))

	graph.paths = graph.svg.append('g')

	for (var group_name in graph.groups) {
            var group = graph.groups[group_name]
            group.path = graph.paths.append('path')
		.data([group.data])
		.attr('class', group_name + ' group')
		.style('stroke', group.color)
	}
    }

    for(var graph_name in graphs)
	tick(graph_name);
}

function tick(graph_name) {

    now = new Date()
    var graph = graphs[graph_name];
    for (var group_name in graph.groups) {
        var group = graph.groups[group_name]
	console.log(vals[group_name] || 0);
        group.data.push(100 * (vals[group_name] || 0));
        group.path.attr('d', graph.line)
    }

    // Shift domain
    graph.x.domain([now - (limit - 2) * duration, now - duration])

    // Slide x-axis left
    graph.axis.transition()
        .duration(duration)
        .ease('linear')
        .call(graph.x.axis)

    // Slide paths left
    r = graph.paths.attr('transform', null)
        .transition()
        .duration(duration)
        .ease('linear')
        .attr('transform', 'translate(' + graph.x(now - (limit - 1) * duration) + ')')
	.each('end', function(){tick(graph_name)})

	    // Remove oldest data point from each group
	    for (var group_name in graph.groups) {
		var group = graph.groups[group_name]
		group.data.shift()
	    }
}
