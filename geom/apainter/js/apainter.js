$(function()  { 
	var canvas=[screen.width*0.99,screen.height-250];
	var db=TAFFY(); // http://taffydb.com/working_with_data.html
	var selected_rect='';
	var zt={'x':0, 'y':0, 'k':1}; // zoom transform
	var gg=make_gg();
	var svg;
	var counter=0;
	var g_aamks;
	var g_snap_lines;
	var ax={};
	var snap_dist=15;
	var snap_lines={};
	var snap_points={};
	var current_snapping=[];
	site();

// gg geoms //{{{
function make_gg() {
	// tango https://sobac.com/sobac/tangocolors.htm
	// Aluminium   #eeeeec #d3d7cf #babdb6
	// Butter      #fce94f #edd400 #c4a000
	// Chameleon   #8ae234 #73d216 #4e9a06
	// Orange      #fcaf3e #f57900 #ce5c00
	// Chocolate   #e9b96e #c17d11 #8f5902
	// Sky Blue    #729fcf #3465a4 #204a87
	// Plum        #ad7fa8 #75507b #5c3566
	// Slate       #888a85 #555753 #2e3436
	// Scarlet Red #ef2929 #cc0000 #a40000

	return {
		ROOM : { l: "r" , c: "#729fcf" },
		COR  : { l: "q" , c: "#3465a4" },
		DOOR : { l: "d" , c: "#73d216" },
		HOLE : { l: "z" , c: "#c4a000" },
		WIN  : { l: "w" , c: "#cc0000" },
		STAI : { l: "s" , c: "#5c3566" },
		HALL : { l: "a" , c: "#ad7fa8" },
		ClosD: { l: "c" , c: "#fce94f" },
		ElktD: { l: "e" , c: "#ce5c00" },
		VVNT : { l: "v" , c: "#ef2929" }
	}
}
//}}}
// zoomer//{{{
	svg.append("rect")
		.attr("id", 'zoomer')
		.attr("width", canvas[0])
		.attr("height", canvas[1])
		.attr("fill", "#ax4400")
		.attr("opacity", 0)
		.attr("pointer-events", "visible")
		.attr("visibility", "hidden")
		.call(d3.zoom()
			.scaleExtent([1 / 10, 40])
			.filter(function(){
			return ( event.button === 0 ||
					 event.button === 1);
			})
			.translateExtent([[-10000, -10000], [10000 , 10000]])
			.on("zoom", zoomed));
	function zoomed() {
		g_aamks.attr("transform", d3.event.transform);
		zt = d3.event.transform;
		ax.gX.call(ax.xAxis.scale(d3.event.transform.rescaleX(ax.x)));
		ax.gY.call(ax.yAxis.scale(d3.event.transform.rescaleY(ax.y)));

	}
//}}}
// image//{{{
	g_aamks.append("svg:image")
		.attr("id", 'img')
		.attr("x", 0)
		.attr("y", 0)
		.attr("opacity", 0.3)
		.attr("xlink:href", "gfx.jpg");
//}}}
// keyboard//{{{
	$(this).keypress((e) => { 
		for(var key in gg) {
			if (e.key == gg[key].l) { rect_create(gg[key].c, gg[key].l); }
		}
	});

	$(this).keydown((e) => { 
		if (e.key == 'Shift') { 
			$("#zoomer").attr("visibility", "visible");
		}
	});

	$(this).keyup((e) => { 
		if (e.key == 'Shift') { 
			$("#zoomer").attr("visibility", "hidden");
		}
	});

//}}}
// selected //{{{
	$('body').click(function(evt){
		if (evt.target.id != '' && ! ['g_snap_lines', 'g_aamks', 'zoomer', 'img'].includes(evt.target.id)) { 
			d3.selectAll('rect').attr('fill-opacity', 0.4);
			$("#"+evt.target.id).attr('fill-opacity', 0.1);
			selected_rect=evt.target.id;
			var x=db({'name':selected_rect}).select("name", "id", "geom", "x", "y");
			$("status").html("INFO: "+JSON.stringify(x));
		}
		if (evt.target.id != '' && ( evt.target.id == 'zoomer' || evt.target.id == 'img' )) { 
			d3.selectAll('rect').attr('fill-opacity', 0.4);
			selected_rect=''
		}
	});

	$(this).keypress((e) => { 
		if (e.key == 'x' && selected_rect != "") { 
			$("#"+selected_rect).remove();
			db({"name":selected_rect}).remove();
		}
	});
	//}}}
	function make_snap_data() { //{{{
		d3.select("#g_snap_lines").selectAll("line").remove();
		var lines=db().select("lines");
		snap_lines['horiz']=[];
		snap_lines['vert']=[];
		var below, above, right, left;

		for(var points in lines) { 
			below = Math.round(lines[points][0][1]);
			above = Math.round(lines[points][2][1]);
			right = Math.round(lines[points][0][0]);
			left  = Math.round(lines[points][1][0]);

			snap_lines['horiz'].push(below);
			snap_lines['horiz'].push(above);
			snap_lines['vert'].push(right);
			snap_lines['vert'].push(left);

			g_snap_lines.append('line').attr('id' , 'sh_'+below).attr('class' , 'snap_v').attr('y1' , below).attr('y2' , below).attr('x1' , -1000).attr('x2' , 1000).attr("visibility", "hidden");
			g_snap_lines.append('line').attr('id' , 'sh_'+above).attr('class' , 'snap_v').attr('y1' , above).attr('y2' , above).attr('x1' , -1000).attr('x2' , 1000).attr("visibility", "hidden");
			g_snap_lines.append('line').attr('id' , 'sv_'+right).attr('class' , 'snap_h').attr('x1' , right).attr('x2' , right).attr('y1' , -1000).attr('y2' , 1000).attr("visibility", "hidden");
			g_snap_lines.append('line').attr('id' , 'sv_'+left).attr('class'  , 'snap_h').attr('x1' , left).attr('x2'  , left).attr('y1'  , -1000).attr('y2' , 1000).attr("visibility", "hidden");

		}
		snap_lines['horiz']=Array.from(new Set(snap_lines['horiz']));
		snap_lines['vert']=Array.from(new Set(snap_lines['vert']));
		make_snap_points();
	}
//}}}
	function make_snap_points() { //{{{
		snap_points=[];
		for(var vert in snap_lines['vert']) { 
			for(var horiz in snap_lines['horiz']) { 
				snap_points.push([snap_lines['vert'][vert], snap_lines['horiz'][horiz]]);
			}
		}
	}
//}}}
	function legend() { //{{{
		for(var key in gg) {
			$('legend').append("<div class=legend style='background-color: "+gg[key].c+"'>"+gg[key].l+" "+key+"</div>");
		}
	}

//}}}
	function db_insert(geom) { //{{{
		var lines=[];
		x0 = Math.round(geom.rr.x0);
		x1 = Math.round(geom.rr.x1);
		y0 = Math.round(geom.rr.y0);
		y1 = Math.round(geom.rr.y1);
		lines.push([x0, y0], [x1, y0], [x1, y1], [x0, y1]);
		db.insert({"name": geom.name, "lines": lines });
		var x=db().select("name");
		$("status").html(x.length + " | " + JSON.stringify(x));
	}
//}}}
function axes() { //{{{
	ax.x = d3.scaleLinear()
		.domain([-1, canvas[0]+ 1])
		.range([-1, canvas[0]+ 1 ]);

	ax.y = d3.scaleLinear()
		.domain([-1, canvas[1] + 1])
		.range([-1, canvas[1] + 1]);

	ax.xAxis = d3.axisBottom(ax.x)
		.ticks(10)
		.tickSize(canvas[1])
		.tickPadding(8 - canvas[1]);

	ax.yAxis = d3.axisRight(ax.y)
		.ticks(4)
		.tickSize(canvas[0])
		.tickPadding(8 - canvas[0]);

	ax.gX = svg.append("g")
		.attr("class", "axis axis--x")
		.call(ax.xAxis);

	ax.gY = svg.append("g")
		.attr("class", "axis axis--y")
		.call(ax.yAxis);
}
//}}}
function make_setup_box() {//{{{
	$('show-setup-box').click(function() {
		$('setup-box').toggle(400);
	});
	d3.select('body').append('setup-box').html("				\
		<table>													\
		<tr><td>letter + mouse1 <td> create						\
		<tr><td>shift + mouse2	    <td> zoom/drag              \
		<tr><td>x				    <td> deletes selected       \
		<tr><td>hold ctrl			<td> disable snapping       \
		</table>                                                \
		");
}
//}}}
function site() { //{{{
	d3.select('body').append('show-setup-box').html("[help]");
	d3.select('body').append('legend');
	svg = d3.select('body').append('svg').attr("width", canvas[0]).attr("height", canvas[1]);
	axes();
	g_aamks = svg.append("g").attr("id", "g_aamks");
	g_snap_lines= svg.append("g").attr("id", "g_snap_lines");
	svg.append('circle').attr('id', 'snapper').attr('cx', 100).attr('cy', 100).attr('r',5).attr('fill-opacity', 0).attr('fill', "#ff8800");
	legend();
	make_setup_box();
	d3.select('body').append('br');
	d3.select('body').append('status');
}
//}}}
function snap_me(m,rect,first_click) {//{{{
	d3.selectAll('.snap_v').attr('visibility', 'hidden');
	d3.selectAll('.snap_h').attr('visibility', 'hidden');
	$('#snapper').attr('fill-opacity', 0);
	if (event.ctrlKey) {
		return;
	} 
	current_snapping=[];

	for(var point in snap_lines['vert']) {
		p=snap_lines['vert'][point];
		if (	
			m[0] > p - snap_dist &&
			m[0] < p + snap_dist ) { 
				if(first_click==1) { 
					rect.rr.x1=p;
				} else {
					rect.rr.x0=p;
				}
				$("#sv_"+p).attr("visibility", "visible");
				$('#snapper').attr('fill-opacity', 1).attr({ r: 2, cy: m[1], cx: p });
				current_snapping.push(p);
				break;
		}
	}

	for(var point in snap_lines['horiz']) {
		p=snap_lines['horiz'][point];
		if (	
			m[1] > p - snap_dist &&
			m[1] < p + snap_dist ) { 
				if(first_click==1) { 
					rect.rr.y1=p;
				} else {
					rect.rr.y0=p;
				}
				$("#sh_"+p).attr("visibility", "visible");
				$('#snapper').attr('fill-opacity', 1).attr({ r: 2, cx: m[0], cy: p });
				current_snapping.push(p);
				break;
		}
	}
	if(current_snapping.length==2) { 
		$('#snapper').attr({ r: 5, cx: current_snapping[0], cy: current_snapping[1]});
	}
	console.log("current_snapping",current_snapping);
}

//}}}
	function rect_create(color, geom) {//{{{
		var self = this;
		var mouse;
		var first_click=0;

		function before_first_click() {
			if (first_click==1) { return; }
			var x0=(mouse[0]-zt.x)/zt.k;
			var y0=(mouse[1]-zt.y)/zt.k;
			self.rr = { 'x0': x0, 'y0': y0, 'x1': x0, 'y1': y0 };
		}

		svg.on('mousedown', function() {
			mouse=d3.mouse(this);
			before_first_click();
			counter++;
			self.name=geom+"_"+counter;
			self.rect=g_aamks.append('rect').attr('id', self.name).attr('fill-opacity',0.4).attr('fill', color).attr('stroke-width', 1).attr('stroke', color).attr('class', 'rectangle');
			first_click=1;
		});

		svg.on('mousemove', function() {
			mouse=d3.mouse(this);
			before_first_click();
			self.rr.x1=(mouse[0]-zt.x)/zt.k;
			self.rr.y1=(mouse[1]-zt.y)/zt.k;
			if (first_click==0) { 
				snap_me(mouse,self,0);
			} else {
				snap_me(mouse,self,1);
			}
			updateRect();
		});  

		svg.on('mouseup', function() {
			svg.on('mousedown', null);
			svg.on('mousemove', null);
			first_click=0;
			if(self.rr.x0 == self.rr.x1 && self.rr.y0 == self.rr.y1) { 
				$("#"+this.name).remove();
				counter--;
			} else {
				db_insert(self);
				make_snap_data();
			}
		});

		function updateRect() {  
			if(first_click==0) { return; }
			$("#"+self.name).attr({
				x: Math.min(self.rr.x0   , self.rr.x1) ,
				y: Math.min(self.rr.y0   , self.rr.y1) ,
				x1: Math.max(self.rr.x0  , self.rr.x1) ,
				y1: Math.max(self.rr.y0  , self.rr.y1) ,
				width: Math.abs(self.rr.x1 - self.rr.x0) ,
				height: Math.abs(self.rr.y1 - self.rr.y0)
			});   
		}

	}
//}}}

});
