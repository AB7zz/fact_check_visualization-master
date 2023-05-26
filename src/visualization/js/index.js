const timeline = document.getElementById('timeline');

const svg = d3.select("body").append("svg")
    .attr("width", 5000)
    .attr("height", 5000)
    .attr('id', 'outside')
const outside = document.getElementById('outside')



d3.json("./json/newdata.json").then(function(json, error){
    if (error){
        console.log(error)  
    }

    // const simulation = d3.forceSimulation(json.nodes)                 
    //     .force("link", d3.forceLink(json.links)
    //     .distance(900)
    //     .strength(0.2))   
    //     .force("charge", d3.forceManyBody().strength(-120))         
    //     .force("center", d3.forceCenter(900, 2500))
    //     .stop()
    // for (var i = 0; i < 300; ++i) simulation.tick();

    var edges = [];
    console.log(json.links)
    json.links.forEach(function(e, i) {
        var sourceNode = json.nodes.filter(function(n) {
            return n.id === e.source;
        })[0],
            targetNode = json.nodes.filter(function(n) {
                return n.id === e.target;
            })[0];
    
        edges.push({
            source: sourceNode,
            target: targetNode,
            value: e.value
        });
    });

    console.log(edges)

    d3.forceSimulation(json.nodes)                 
        .force("link", d3.forceLink(edges))
    
    const arrows = svg
        .selectAll('defs')
        .data(edges)
        .enter()
        .append("svg:defs")
        .append("svg:marker")
        .attr('id', 'arrow')
        .attr('refX', -108)
        .attr('refY', 0)
        .attr("viewBox", "0 -5 10 10")
        .attr("markerWidth", 20)
        .attr("markerHeight", 10)
        .attr("orient", "auto")
        
    
    arrows
        .append("svg:path")
        .attr("d", "M0,-5L10,0L0,5");


    const link = svg
        .selectAll("line")
        .data(edges)
        .enter()
        .append("line")
        .attr('class', 'lines')
        .style( "stroke", "#000" )
        .attr('marker-start', (d) => `url(#arrow)`)
        .style( "stroke-width", 1.5 );

    const node = svg
        .selectAll('foreignObject')
        .data(json.nodes)
        .enter()
        .append('foreignObject')
        .attr('id', data => `${data.id}`)
        .attr('width', 300)
        .attr('height', '100%')
        
    function bottomYear(x, y, year){
        svg
            .append('text')
            .text(year)
            .attr('fill', 'red')
            .attr('font-size', '25px')
            .attr('font-weight', 'bold')
            .attr('x', x+120)
            .attr('y', y+500)
    }
    
    const yAxis = []
    const xAxis = []
    const timelineset = []
    let maxyear = 2023
    let minyear = 2010
    
    node 
        .attr('class', (d) => `l${d.id} nodes`)
        .html( function(data){
            if(data.type == "evidence"){
                return '<div class="box"><p class="boxfirstline">' + data.snippet + '</p><a target="_blank" style="text-decoration: none" href="' + '//www.' + data.source + '" class="boxsecondline">'+data.source+'</a><hr class="solid"><p class="boxdate">' + data.year + '</p></div>';
            }else if(data.type == "claim" && data.id!=0){
                return '<div class="claimbox tri-right2 btm-left-in2 border2 sb32"><p class="claimfirstline">' + data.snippet + '</p><p class="claimsecondline">'+data.claimer +'</p><hr class="solid"><p class="claimdate">' + data.year + '</p></div>';
            }else if(data.type == "claim" && data.id==0){
                return '<div class="greenclaim tri-right btm-left-in border sb32"><p class="greenclaimfirstline">' + data.snippet + '</p><p class="greenclaimsecondline">'+data.claimer +'</p><hr class="solid"><p class="claimdate">' + data.year + '</p></div>';
            }
            else if(data.type == "fact_check"){
                return '<div class="fact_check"><p class="fact_checkfirstline">' + data.snippet + '</p><a target="_blank" href="' + '//www.' + data.source + '"  class="fact_checksecondline">'+data.source +'</a><p class="fact_checkthirdline">Truth value: '+data.truth_value +'</p><hr class="solid"><p class="fact_checkdate">' + data.year + '</p></div>';
            }
        })
        // .call(d3.drag()
        //         .on('start', dragstarted)
        //         .on('drag', dragged)
        //         .on('end', dragended)
        // )
        .attr("x", function(d){
            let xi, month = 0
            let year = d.year[0]
            if(year == 0 || d.year == "UNKNOWN"){
                xi = ((maxyear-minyear)*400)+50
            }else{
                xi = ((maxyear-year)*400)+50
            }
            xAxis.push(xi)
            d.x = parseFloat(xi)
            return xi;
        })
        .attr("y", function(d){
            let i, yi
            i = 0
            let year = d.year[0]
            while(json.nodes[i].id!=d.id){
                i++
            }
            if(year == "UNKNOWN"){
                year = 2023
            }
            if(!yAxis[maxyear-year]){
                yAxis[maxyear-year] = 200
            }
            else{
                yAxis[maxyear-year] += 500
            }
            yi = yAxis[maxyear-year]
            d.y = parseFloat(yi)
            return yi;  
        })
        .attr('timeline', (d) => {
            let ymax=json.nodes[0].y, xmax=json.nodes[0].x
            let year = d.year[0]
            if(year == "UNKNOWN"){
                year = 2023
            }
            for(let l = 1; l < json.nodes.length; l++){
                if(json.nodes[l].y >= ymax){
                    ymax = json.nodes[l].y
                }
                if(json.nodes[l].x >= xmax){
                    xmax = json.nodes[l].x
                }
            }
            if(!timelineset[year]){
                bottomYear(d.x, ymax, year)
                timelineset[year] = true
            }
            svg
                .attr("height", ymax+1000)
                .attr("width", xmax+1000)
        })
    


    link
        .attr("x1", function(d){
            x1 = d.source.x + 150;
            return x1
        })
        .attr("y1", function(d){
            y1 = d.source.y+75;
            return y1
        })
        .attr("x2", function(d){
            x2 = d.target.x+150;
            return x2
        })
        .attr("y2", function(d){
            y2 = d.target.y+75;
            return y2
        })
        .attr( "d", function(d){
            x1 = d.source.x + 150;
            y1 = d.source.y+75;
            x2 = d.target.x+150;
            y2 = d.target.y+75;
            return "M" + x1 + "," + y1 + ", " + x2 + "," + y2
        })
    link.each(function(d){
        let source = d.source.id
        let target = d.target.id
        this.classList.add(`l${source}`)
        this.classList.add(`l${target}`)

        let snodesource = document.getElementById(`${source}`)
        let snodetarget = document.getElementById(`${target}`)
        snodetarget.classList.add(`l${source}`)
        snodesource.classList.add(`l${target}`)
    })

    svg
        .on('click', (evt) => {
            let target = evt.target
            let lines = document.getElementsByClassName('lines')
            let allnodes = document.getElementsByClassName('nodes')
            if(outside == target){
                for(let i=0; i<lines.length; i++){
                    lines[i].style.opacity = '1'
                    lines[i].style.stroke = 'black'
                    lines[i].style.strokeWidth = '1.5'
                }
    
                for(let i=0; i<allnodes.length; i++){
                    allnodes[i].style.opacity = '1'
                    allnodes[i].style.pointerEvents = 'all'
                }
                return
            }
        }
    )

    node
        .on('click', function(){
            let lines = document.getElementsByClassName('lines')
            let allnodes = document.getElementsByClassName('nodes')
            for(let i=0; i<lines.length; i++){
                if(!lines[i].classList.contains(`l${this.id}`)){
                    lines[i].style.opacity = '0.03'
                }else{
                    lines[i].style.stroke = 'red'
                }
            }

            for(let i=0; i<allnodes.length; i++){
                if(!allnodes[i].classList.contains(`l${this.id}`)){
                    allnodes[i].style.opacity = '0.15'
                    allnodes[i].style.pointerEvents = 'none'
                }
            }
        })
    
    



    
    // function dragstarted(event, d) {
    //     d3.select(this)
    //         .attr("fx", d.x = event.x )
    //         .attr("fy", d.y = event.y )
        
    //     ticked()
    // }

    // function dragged(event, d) { 
    //     d3.select(this)
    //         .attr("fx", d.x = event.x )
    //         .attr("fy", d.y = event.y )
        
    //     ticked()
    // }

    // function dragended(event, d) {
    //     d3.select(this)
    //         .attr("fx", d.x = event.x )
    //         .attr("fy", d.y = event.y )
    //         .attr('lol', id = d.id, x=d.x, y=d.y, vx=d.vx, vy=d.vy )
        
    //     ticked()

    // }

    // function ticked() {
    //     link
    //         .attr("x1", d => d.source.x+150)
    //         .attr("x2", d => d.target.x+150)
    //         .attr("y1", d => d.source.y+75)
    //         .attr("y2", d => d.target.y+75)

    //     node
    //         .attr("x", d => d.x )   
    //         .attr("y", d => d.y )
    // }
})