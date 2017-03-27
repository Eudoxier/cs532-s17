//Constants for the SVG
var w = 1280,
    h = 720,
    img_w = 20,
    img_h = 20,
    // Image big (mouseover)
    img_bw = 100,
    img_bh = 100,
    //Set up the colour scale
    fill = d3.scale.category20();

//Append a SVG to the body of the html page. Assign this SVG as an object to svg
var vis = d3.select("#chart")
  .append("svg:svg")
    .attr("width", w)
    .attr("height", h);

//Set up the force layout
//Creates the graph data structure out of the json data
d3.json("force.json", function(json) {
  var force = d3.layout.force()
      .charge(-600)
      .linkDistance(40)
      .nodes(json.nodes)
      .links(json.links)
      .size([w, h])
      .friction(0.5)
      .gravity(0.05)
      .start();

  //Create all the line svgs but without locations yet
  var link = vis.selectAll("line.link")
      .data(json.links)
    .enter().append("svg:line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); })
      .attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

  //Do the same with the circles for the nodes - no 
  var node = vis.selectAll("circle.node")
      .data(json.nodes)
    .enter().append("image")
      .attr("class", "node")
      .attr("xlink:href", function(d) { return d.profile_image_url })
      .attr("x", function(d) { return -img_w/2; })
      .attr("y", function(d) { return -img_h/2; })
      .attr("width", img_w)
      .attr("height", img_h)
      .on("mouseenter", function(d) {
            // select element in current context
            d3.select( this )
              .transition()
              .attr("x", function(d) { return -img_bw/2;})
              .attr("y", function(d) { return -img_bh/2;})
              .attr("height", img_bh)
              .attr("width", img_bw);
          })
      .on("mouseleave", function(d) {
            d3.select( this )
              .transition()
              .attr("x", function(d) { return -img_w/2;})
              .attr("y", function(d) { return -img_h/2;})
              .attr("height", img_h)
              .attr("width", img_w);
          })
      .call(force.drag);

  node.append("title")
      .text(function(d) { return d.screen_name + ": " + d.name; });

  vis.style("opacity", 1e-6)
    .transition()
      .duration(1000)
      .style("opacity", 1);

  //Now we are giving the SVGs co-ordinates - the force layout is generating 
  //the co-ordinates which this code is using to update the attributes of the SVG elements
  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
        
    node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
  });
});
